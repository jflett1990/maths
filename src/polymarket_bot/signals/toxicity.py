from polymarket_bot.core.models import Market


def toxicity_penalty(market: Market, smart_wallet_toxicity_adjustment: float = 0.0) -> tuple[float, float, float, bool]:
    penalty = min(1.0, market.holder_concentration * 0.8 + market.volatility * 0.7 + smart_wallet_toxicity_adjustment)
    width_adj = 1.0 + penalty
    size_adj = max(0.1, 1.0 - penalty)
    no_trade = penalty > 0.8
    return penalty, width_adj, size_adj, no_trade
