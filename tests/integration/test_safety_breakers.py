import json
from pathlib import Path

from polymarket_bot.app import run_once


def test_global_kill_switch_blocks_orders(tmp_path) -> None:
    cfg = Path("configs/base.yaml").read_text().replace("global_enabled: false", "global_enabled: true")
    c = tmp_path / "cfg.yaml"
    c.write_text(cfg.replace("output_dir: state", f"output_dir: {tmp_path / 'state'}"))
    placed = run_once(str(c))
    assert placed == 0
    report = json.loads((tmp_path / "state" / "run_report.json").read_text())
    assert "cb_global_kill_switch" in report["circuit_breakers_triggered"]
