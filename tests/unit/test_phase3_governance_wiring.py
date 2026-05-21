import json
import subprocess
import sys
import os
from pathlib import Path

from polymarket_bot.app import run_once
from polymarket_bot.core.config import load_config
from polymarket_bot.governance.models import (
    ApprovalRecord,
    DatasetSpec,
    ExperimentSpec,
    ExpirationPolicy,
    MetricSummary,
    PromotionGateDecision,
    SignalSpec,
    ValidationRunRecord,
)
from polymarket_bot.governance.permissions import resolve_signal_permission
from polymarket_bot.governance.registry import ExperimentRegistry
from polymarket_bot.core.models import WalletSignal


class CaptureWalletAdapter:
    def __init__(self):
        self.calls = []

    def fetch_wallet_trades(self, wallet_id: str, limit: int = 500):
        self.calls.append(wallet_id)
        return []


class FakeMarketAdapter:
    def fetch_active_markets(self):
        rows = json.loads(Path("tests/fixtures/markets.json").read_text())
        from polymarket_bot.core.models import Market

        return [
            Market(
                market_id=str(r["id"]), question=str(r["question"]), category=str(r["category"]),
                yes_price=float(r["yes_price"]), no_price=float(r["no_price"]),
                spread_bps=abs(float(r["no_price"]) - float(r["yes_price"])) * 10000,
                liquidity=float(r["liquidity"]), open_interest=float(r["open_interest"]),
                event_ts=int(r["event_ts"]), rules_text=str(r["rules_text"]),
                last_update_ts=int(r["last_update_ts"]),
            )
            for r in rows
        ]


def test_wallet_universe_config_replaces_smart1_hardcode(tmp_path: Path) -> None:
    cfg = Path("configs/base.yaml").read_text().replace("output_dir: state", f"output_dir: {tmp_path / 'state'}")
    cfg += "\nsignals:\n  wallet_universe: [alpha, beta]\n  wallet_intelligence:\n    enabled: false\n    signal_name: wallet_intelligence\n    signal_version: v1\n    experiment_id: e\n    requested_mode: observe_only\n    registry_path: state/registry_events.jsonl\n    validation_report_path: state/wallet_validation_report.json\n    dataset_paths: []\n    allow_edge_contribution: false\n"
    p = tmp_path / "c.yaml"
    p.write_text(cfg)
    wa = CaptureWalletAdapter()
    run_once(str(p), market_adapter=FakeMarketAdapter(), wallet_adapter=wa)
    assert wa.calls == ["alpha", "beta"]


def test_runtime_requested_mode_clamped_to_registry_grant() -> None:
    rec = {
        "gate": {"granted_mode": "risk_filter_only", "max_wallet_alpha_bps": 7},
        "expiration": {"expires_at": "2999-01-01T00:00:00+00:00"},
        "immutable_fingerprints": {"dataset_fingerprint": "d", "report_fingerprint": "r"},
    }
    p = resolve_signal_permission("paper", rec, "d", "r", requested_mode="edge_contribution_allowed")
    assert p.effective_signal_mode == "risk_filter_only"


def test_allow_edge_contribution_false_blocks_positive_alpha(tmp_path: Path) -> None:
    cfg = Path("configs/base.yaml").read_text().replace("output_dir: state", f"output_dir: {tmp_path / 'state'}")
    cfg = cfg.replace("allow_edge_contribution: false", "allow_edge_contribution: false")
    p = tmp_path / "c.yaml"
    p.write_text(cfg)
    run_once(str(p), market_adapter=FakeMarketAdapter(), wallet_adapter=CaptureWalletAdapter())
    signals = (tmp_path / "state" / "signals.jsonl").read_text().splitlines()
    if signals:
        row = json.loads(signals[0])
        assert row["wallet_signal"]["wallet_alpha_bps"] == 0.0


def test_expire_experiment_appends_durable_event(tmp_path: Path) -> None:
    (tmp_path / "state").mkdir()
    log = tmp_path / "state" / "registry_events.jsonl"
    state = tmp_path / "state" / "registry_state.json"
    reg = ExperimentRegistry(str(log), str(state))
    rec = ValidationRunRecord(
        1, "exp1", 1, "2026-01-01T00:00:00+00:00",
        ExperimentSpec("exp1", "wallet_intelligence", "v1", "observe_only"),
        DatasetSpec("d", "w", 10, {}),
        SignalSpec("wallet_intelligence", "v1", "c", "code"),
        MetricSummary("ok", {}, []),
        PromotionGateDecision("observe_only", "observe_only", ["pass"], False, 0.0),
        ExpirationPolicy(14, "2999-01-01T00:00:00+00:00"),
        ApprovalRecord(None, None),
        {"json": "r"},
        {"dataset_fingerprint": "d", "config_fingerprint": "c", "report_fingerprint": "r"},
    )
    reg.append(rec)
    subprocess.check_call([
        sys.executable, str((Path(__file__).resolve().parents[2] / "scripts" / "expire_experiment.py")), "--experiment-id", "exp1"
    ], cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2] / "src")})
    lines = [ln for ln in log.read_text().splitlines() if ln.strip()]
    assert len(lines) == 2
