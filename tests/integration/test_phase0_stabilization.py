import json
from pathlib import Path

import pytest

from polymarket_bot.adapters.polymarket import AdapterError
from polymarket_bot.core.models import Market
from polymarket_bot.app import run_once


class FakeMarketAdapter:
    def fetch_active_markets(self):
        rows = json.loads(Path("tests/fixtures/markets.json").read_text())
        return [
            Market(
                market_id=str(r["id"]),
                question=str(r["question"]),
                category=str(r["category"]),
                yes_price=float(r["yes_price"]),
                no_price=float(r["no_price"]),
                spread_bps=abs(float(r["no_price"]) - float(r["yes_price"])) * 10000,
                liquidity=float(r["liquidity"]),
                open_interest=float(r["open_interest"]),
                event_ts=int(r["event_ts"]),
                rules_text=str(r["rules_text"]),
                last_update_ts=int(r["last_update_ts"]),
            )
            for r in rows
        ]


class FakeWalletAdapter:
    def fetch_wallet_trades(self, wallet_id: str, limit: int = 500):
        return []


class BoomAdapter:
    def fetch_active_markets(self):
        raise AdapterError("boom")


class FaultyRecorder:
    def __init__(self):
        self.seq = 0

    def write(self, stream: str, payload: dict):
        self.seq += 1
        raise OSError("disk full")


def _cfg(tmp_path: Path, **replace: str) -> Path:
    txt = Path("configs/base.yaml").read_text().replace("output_dir: state", f"output_dir: {tmp_path / 'state'}")
    for k, v in replace.items():
        txt = txt.replace(k, v)
    p = tmp_path / "cfg.yaml"
    p.write_text(txt)
    return p


def test_global_kill_switch_blocks_fixture_orders(tmp_path: Path) -> None:
    c = _cfg(tmp_path, **{"global_enabled: false": "global_enabled: true"})
    placed = run_once(str(c), market_adapter=FakeMarketAdapter(), wallet_adapter=FakeWalletAdapter())
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert placed == 0
    assert report["markets_rejected_by_reason"].get("global_kill_switch", 0) >= 1 or "cb_global_kill_switch" in report["circuit_breakers_triggered"]


def test_per_market_kill_switch_blocks_only_disabled_market(tmp_path: Path) -> None:
    markets = FakeMarketAdapter().fetch_active_markets()
    disabled = markets[0].market_id
    c = _cfg(tmp_path, **{"per_market_disabled: []": f"per_market_disabled: ['{disabled}']"})
    run_once(str(c), market_adapter=FakeMarketAdapter(), wallet_adapter=FakeWalletAdapter())
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert report["markets_rejected_by_reason"]["market_kill_switch"] == 1


def test_adapter_error_trips_fail_closed_report(tmp_path: Path) -> None:
    c = _cfg(tmp_path)
    placed = run_once(str(c), market_adapter=BoomAdapter(), wallet_adapter=FakeWalletAdapter())
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert placed == 0
    assert "cb_adapter_error_stop" in report["circuit_breakers_triggered"]


def test_run_once_uses_injected_adapters_no_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from polymarket_bot.adapters import polymarket as poly_mod

    def _boom(*args, **kwargs):
        raise AssertionError("network adapter should not be constructed when injected")

    monkeypatch.setattr(poly_mod.PolymarketRESTAdapter, "__init__", _boom)
    c = _cfg(tmp_path)
    placed = run_once(str(c), market_adapter=FakeMarketAdapter(), wallet_adapter=FakeWalletAdapter())
    assert placed >= 0


def test_recorder_error_trips_cb_when_fail_on_error(tmp_path: Path) -> None:
    c = _cfg(tmp_path)
    (tmp_path / "state").mkdir(parents=True, exist_ok=True)
    run_once(str(c), market_adapter=FakeMarketAdapter(), wallet_adapter=FakeWalletAdapter(), recorder=FaultyRecorder())
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert "cb_recorder_failure_stop" in report["circuit_breakers_triggered"]
