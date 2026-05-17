from polymarket_bot.core.models import WalletScore, WalletTrade
from polymarket_bot.wallets.signals import wallet_signal_for_market


def test_wallet_signal_generation() -> None:
    trades = [WalletTrade("w", "m", 1, "buy", 0.4, 1000, "c", 10000, 0.9, True, 1)]
    scores = {"w": WalletScore("w", 10, 0.8, ["c"], ["r"], [], None)}
    sig = wallet_signal_for_market("m", trades, scores)
    assert sig.wallet_alpha_bps >= 0
    assert sig.toxic_informed_flow_flag
