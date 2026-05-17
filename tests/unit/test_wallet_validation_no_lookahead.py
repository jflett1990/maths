from polymarket_bot.core.models import WalletTrade
from polymarket_bot.wallets.validation.dataset import build_validation_rows


def test_no_lookahead_wallet_score() -> None:
    trades = [
        WalletTrade("w", "m1", 1, "buy", 0.4, 10, "c", 10000, 0.9, True, 1),
        WalletTrade("w", "m2", 2, "buy", 0.4, 10, "c", 10000, 0.9, True, 1),
    ]
    rows = build_validation_rows(trades)
    assert rows[0].wallet_score_at_ts == 0
    assert rows[1].wallet_score_at_ts != 0
