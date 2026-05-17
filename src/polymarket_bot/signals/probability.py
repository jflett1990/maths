from polymarket_bot.core.models import Market, ProbabilityEstimate


def fair_probability(market: Market, exogenous: float | None = None) -> ProbabilityEstimate:
    prior = market.yes_price
    point = prior if exogenous is None else (0.8 * prior + 0.2 * exogenous)
    uncertainty = min(0.45, 0.1 + market.volatility + market.holder_concentration * 0.2)
    band = max(0.02, uncertainty * 0.5)
    lower = max(0.0, point - band)
    upper = min(1.0, point + band)
    conf = max(0.0, 1 - uncertainty)
    return ProbabilityEstimate(market.market_id, point, lower, upper, uncertainty, conf, "prior_blend")
