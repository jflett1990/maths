from __future__ import annotations

from polymarket_bot.core.models import WalletScore, WalletSignal, WalletTrade


def wallet_signal_for_market(market_id: str, trades: list[WalletTrade], scores: dict[str, WalletScore]) -> WalletSignal:
    relevant = [t for t in trades if t.market_id == market_id and t.wallet_id in scores]
    buy = sum(t.size for t in relevant if t.side == "buy")
    sell = sum(t.size for t in relevant if t.side != "buy")
    total = buy + sell
    consensus = 0.0 if total == 0 else (buy - sell) / total
    divergence = 1 - abs(consensus)
    score_weight = sum(max(0.0, scores[t.wallet_id].score) for t in relevant) or 0.0
    wallet_alpha = min(25.0, consensus * (score_weight / max(1, len(relevant))) * 0.1)
    crowd = min(20.0, max(0.0, total - 500) * 0.01)
    toxic = total > 800 and divergence < 0.2
    return WalletSignal(
        market_id=market_id,
        smart_wallet_buy_pressure=buy,
        smart_wallet_sell_pressure=sell,
        smart_wallet_consensus=consensus,
        smart_wallet_divergence=divergence,
        specialist_wallet_activity=score_weight,
        new_smart_wallet_entry=1.0 if total > 0 else 0.0,
        smart_wallet_exit=0.0,
        toxic_informed_flow_flag=toxic,
        copy_latency_penalty_bps=min(10.0, total * 0.005),
        crowding_penalty_bps=crowd,
        wallet_alpha_bps=wallet_alpha,
        smart_wallet_toxicity_adjustment=0.2 if toxic else 0.0,
        confidence=min(1.0, 0.2 + len(relevant) / 20),
        reasons=["wallet_intelligence_conservative"],
    )
