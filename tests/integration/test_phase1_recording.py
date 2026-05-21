import json
from pathlib import Path

from polymarket_bot.app import run_once
from polymarket_bot.replay import replay_compare


def _cfg(tmp_path: Path) -> Path:
    txt = Path("configs/base.yaml").read_text().replace("output_dir: state", f"output_dir: {tmp_path / 'state'}")
    p = tmp_path / "cfg.yaml"
    p.write_text(txt)
    return p


def test_run_writes_decisions_orders_pnl_run_streams(tmp_path: Path) -> None:
    c = _cfg(tmp_path)
    run_once(str(c))
    for name in ["decisions.jsonl", "orders.jsonl", "pnl.jsonl", "run.jsonl"]:
        assert (tmp_path / "state" / name).exists()


def test_replay_matches_fixture_run_with_fills(tmp_path: Path) -> None:
    c = _cfg(tmp_path)
    run_once(str(c))
    cmp = replay_compare(str(tmp_path / "state"))
    assert cmp["mismatches"] == 0


def test_schema_versions_consistent_across_recorded_outputs(tmp_path: Path) -> None:
    c = _cfg(tmp_path)
    run_once(str(c))
    for fp in (tmp_path / "state").glob("*.jsonl"):
        for line in fp.read_text().splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            assert obj["schema_version"] == 2


def test_run_writes_only_canonical_streams(tmp_path: Path) -> None:
    c = _cfg(tmp_path)
    run_once(str(c))
    files = {f.name for f in (tmp_path / "state").glob("*.jsonl")}
    assert files == {
        "market_snapshots.jsonl",
        "wallet_observations.jsonl",
        "signals.jsonl",
        "decisions.jsonl",
        "orders.jsonl",
        "fills.jsonl",
        "pnl.jsonl",
        "run.jsonl",
        "run_report.jsonl",
        "reconciliation_anomalies.jsonl",
    }
