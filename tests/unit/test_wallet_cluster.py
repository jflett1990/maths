from polymarket_bot.core.models import WalletTrade
from polymarket_bot.wallets.clustering import heuristic_clusters


def test_cluster_heuristic() -> None:
    trades = [
        WalletTrade("w1", "m", 1, "buy", 0.4, 10, "c", 10000, 0.9, True, 1),
        WalletTrade("w2", "m", 2, "buy", 0.4, 11, "c", 10000, 0.9, True, 1),
    ]
    cs = heuristic_clusters(trades)
    assert cs
    assert "heuristic_not_identity" in cs[0].heuristic_labels
