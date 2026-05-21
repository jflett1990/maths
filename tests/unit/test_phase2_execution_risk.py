from pathlib import Path
import json

from polymarket_bot.app import run_once
from polymarket_bot.execution.paper_broker import PaperBroker
from polymarket_bot.reconciliation import reconcile_state


def _cfg(tmp_path: Path, **replace: str) -> Path:
    txt = Path("configs/base.yaml").read_text().replace("output_dir: state", f"output_dir: {tmp_path / 'state'}")
    for k, v in replace.items():
        txt = txt.replace(k, v)
    p = tmp_path / "cfg.yaml"
    p.write_text(txt)
    return p


def test_filled_order_not_missing_active_in_reconciliation() -> None:
    out = reconcile_state(
        intended_order_ids=["o1"],
        active_order_ids=[],
        recorded_order_ids=["o1"],
        recorded_fill_ids=["o1"],
        stateful_fill_ids=["o1"],
        recorder_seqs=[1, 2, 3],
    )
    assert not any(a.code == "missing_active_order" for a in out)


def test_max_orders_per_run_blocks_extra_orders(tmp_path: Path) -> None:
    c = _cfg(tmp_path, **{"max_orders_per_run: 100": "max_orders_per_run: 0"})
    placed = run_once(str(c))
    assert placed == 0


def test_aggregate_notional_limit_blocks_run(tmp_path: Path) -> None:
    c = _cfg(tmp_path, **{"max_order_notional_per_run: 50000": "max_order_notional_per_run: 1"})
    placed = run_once(str(c))
    assert placed == 0


def test_stale_quotes_cancelled_and_recorded() -> None:
    b = PaperBroker()
    class D:
        market_id = "m1"
        side = "yes"
        price = 0.5
        size = 1.0
    oid = b.place(D(), gtd_sec=1)
    cancelled = b.reconcile_market("m1", now_ts=10**10)
    assert oid in cancelled
    assert b._completed[oid].status == "expired"  # noqa: SLF001


def test_position_limit_blocks_run(tmp_path: Path) -> None:
    c = _cfg(tmp_path, **{"max_position_per_market: 2000": "max_position_per_market: 1", "min_expected_edge_bps: 25": "min_expected_edge_bps: -999"})
    placed = run_once(str(c))
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert placed == 0
    assert report["markets_rejected_by_reason"].get("max_position_per_market", 0) >= 1


def test_category_exposure_limit_blocks_run(tmp_path: Path) -> None:
    c = _cfg(tmp_path, **{"max_category_exposure: 12000": "max_category_exposure: 1", "min_expected_edge_bps: 25": "min_expected_edge_bps: -999"})
    placed = run_once(str(c))
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert placed == 0
    assert report["markets_rejected_by_reason"].get("max_category_exposure", 0) >= 1
