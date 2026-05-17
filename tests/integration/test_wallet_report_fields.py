import json
from pathlib import Path

from polymarket_bot.app import run_once


def test_run_report_wallet_fields(tmp_path) -> None:
    cfg = Path("configs/base.yaml").read_text().replace("output_dir: state", f"output_dir: {tmp_path / 'state'}")
    c = tmp_path / "cfg.yaml"
    c.write_text(cfg)
    run_once(str(c))
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert "top_smart_wallets_observed" in report
    assert "wallet_derived_opportunities" in report
