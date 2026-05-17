import json

from polymarket_bot.core.models import WalletTrade
from polymarket_bot.wallets.validation.harness import run_wallet_validation


def test_validation_report_shape(tmp_path) -> None:
    trades = [WalletTrade("w", "m", 1, "buy", 0.4, 10, "c", 10000, 0.9, True, 1) for _ in range(20)]
    j = tmp_path / "v.json"
    m = tmp_path / "v.md"
    report = run_wallet_validation(trades, str(j), str(m))
    obj = json.loads(j.read_text())
    assert "baseline_comparison" in obj
    assert "promotion" in obj
    assert report["promotion"]["mode"] in {"disabled", "observe_only", "risk_filter_only", "ranking_boost_allowed", "edge_contribution_allowed"}
