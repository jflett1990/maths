from polymarket_bot.core.config import AppConfig
from polymarket_bot.core.models import Market, SignalResult
from polymarket_bot.signals.resolution import resolution_risk_score
from polymarket_bot.signals.toxicity import toxicity_penalty


def allow_trade(market: Market, signal: SignalResult, cfg: AppConfig) -> tuple[bool, str]:
    res = resolution_risk_score(market)
    tox, _, _, no_trade = toxicity_penalty(market)
    if res > cfg.risk.resolution_risk_max:
        return False, "resolution_risk_gate"
    if tox > cfg.risk.toxicity_max or no_trade:
        return False, "toxicity_gate"
    if market.liquidity < cfg.risk.min_liquidity:
        return False, "liquidity_gate"
    if signal.expected_edge_bps < cfg.min_expected_edge_bps:
        return False, "edge_gate"
    return True, "ok"
