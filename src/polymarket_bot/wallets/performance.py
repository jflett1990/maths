from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from polymarket_bot.core.models import WalletTrade


@dataclass(slots=True)
class WalletPerformance:
    wallet_id: str
    realized_pnl: float
    unrealized_pnl: float
    roi: float
    hit_rate: float
    avg_entry_edge: float
    avg_exit_quality: float
    holding_period: float
    turnover: float
    max_drawdown: float
    sharpe_like: float
    market_count: int
    resolved_market_count: int
    category_specialization: list[str]
    liquidity_adjusted_return: float
    ambiguity_adjusted_return: float
    reward_adjusted_return: float


def attribute_wallet_performance(trades: list[WalletTrade]) -> WalletPerformance:
    if not trades:
        return WalletPerformance("", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, [], 0, 0, 0)
    wallet_id = trades[0].wallet_id
    realized = 0.0
    wins = 0
    resolved = 0
    liq = 0.0
    ambiguity_adj = 0.0
    cat = Counter[str]()
    for t in trades:
        cat[t.category] += 1
        liq += t.liquidity
        if t.resolved and t.outcome is not None:
            resolved += 1
            ret = (1 - t.price if t.outcome == 1 and t.side == "buy" else -t.price * 0.5) * t.size
            realized += ret
            ambiguity_adj += ret * t.resolution_clarity
            wins += 1 if ret > 0 else 0
    notional = sum(t.price * t.size for t in trades) or 1.0
    roi = realized / notional
    hit = wins / resolved if resolved else 0.0
    sample_penalty = min(1.0, resolved / 30)
    liq_adj = roi * min(1.0, (liq / max(1, len(trades))) / 5000)
    sharpe = roi * sample_penalty * 3
    return WalletPerformance(
        wallet_id=wallet_id,
        realized_pnl=realized,
        unrealized_pnl=0.0,
        roi=roi,
        hit_rate=hit,
        avg_entry_edge=roi * 100,
        avg_exit_quality=hit,
        holding_period=0.0,
        turnover=notional,
        max_drawdown=max(0.0, -realized),
        sharpe_like=sharpe,
        market_count=len({t.market_id for t in trades}),
        resolved_market_count=resolved,
        category_specialization=[k for k, _ in cat.most_common(2)],
        liquidity_adjusted_return=liq_adj,
        ambiguity_adjusted_return=ambiguity_adj / notional,
        reward_adjusted_return=roi,
    )
