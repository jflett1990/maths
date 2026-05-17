from polymarket_bot.core.models import WalletTrade
from polymarket_bot.wallets.performance import attribute_wallet_performance
from polymarket_bot.wallets.scoring import score_wallet


def test_small_sample_penalty() -> None:
    trades = [WalletTrade("w", "m", 1, "buy", 0.4, 10, "c", 10000, 0.9, True, 1)]
    perf = attribute_wallet_performance(trades)
    s = score_wallet(perf)
    assert s.sample_warning == "small_sample"


def test_ambiguity_adjusted_scoring() -> None:
    t1 = WalletTrade("w", "m", 1, "buy", 0.4, 10, "c", 10000, 0.2, True, 1)
    perf = attribute_wallet_performance([t1])
    assert perf.ambiguity_adjusted_return <= perf.roi
