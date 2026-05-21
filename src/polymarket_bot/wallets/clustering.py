from __future__ import annotations

from collections import defaultdict

from polymarket_bot.core.models import WalletCluster, WalletTrade


def heuristic_clusters(trades: list[WalletTrade]) -> list[WalletCluster]:
    by_market: dict[str, set[str]] = defaultdict(set)
    for t in trades:
        by_market[t.market_id].add(t.wallet_id)
    clusters: list[WalletCluster] = []
    idx = 0
    for market_id, ws in by_market.items():
        if len(ws) >= 2:
            idx += 1
            clusters.append(WalletCluster(f"cluster-{idx}", sorted(ws), 0.4, [f"co_entry_market:{market_id}", "heuristic_not_identity"]))
    return clusters
