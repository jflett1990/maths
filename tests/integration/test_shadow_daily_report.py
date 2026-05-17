import json
from pathlib import Path

from polymarket_bot.wallets.validation.harness import run_wallet_validation_from_recorded


def test_shadow_report_shape(tmp_path) -> None:
    rep = run_wallet_validation_from_recorded("tests/fixtures/recorded_state", str(tmp_path / "v.json"), str(tmp_path / "v.md"), [0,30,120,600])
    assert "baseline_comparison" in rep
    assert "latency_stress_results" in rep
    assert (tmp_path / "v.json").exists()
    json.loads((tmp_path / "v.json").read_text())
