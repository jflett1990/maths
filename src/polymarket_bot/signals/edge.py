from polymarket_bot.core.config import AppConfig
from polymarket_bot.core.models import Market, SignalResult, WalletSignal
from polymarket_bot.signals.cross_market import ConstraintViolation
from polymarket_bot.signals.probability import fair_probability
from polymarket_bot.signals.resolution import resolution_risk_score
from polymarket_bot.signals.toxicity import toxicity_penalty


def evaluate_market(market: Market, cfg: AppConfig, cross: ConstraintViolation | None = None, exogenous: float | None = None, wallet_signal: WalletSignal | None = None) -> SignalResult:
    prob = fair_probability(market, exogenous=exogenous)
    forecast_alpha = (prob.point - market.yes_price) * 10000
    cross_market_alpha = 0.0 if cross is None else cross.alpha_bps
    wallet_alpha = 0.0 if wallet_signal is None else wallet_signal.wallet_alpha_bps
    spread_reward_alpha = (market.spread_bps * 0.2) + (market.reward_bps * cfg.penalties.reward_haircut)
    execution_cost = market.spread_bps * 0.5
    uncertainty_penalty = prob.uncertainty * cfg.penalties.uncertainty_haircut * 100
    tox_adj = 0.0 if wallet_signal is None else wallet_signal.smart_wallet_toxicity_adjustment
    tox, _, _, _ = toxicity_penalty(market, smart_wallet_toxicity_adjustment=tox_adj)
    res = resolution_risk_score(market)
    expected_edge = forecast_alpha + cross_market_alpha + wallet_alpha + spread_reward_alpha - execution_cost - uncertainty_penalty - tox * 100 - res * 100
    return SignalResult(
        market_id=market.market_id,
        forecast_alpha_bps=forecast_alpha,
        cross_market_alpha_bps=cross_market_alpha,
        wallet_alpha_bps=wallet_alpha,
        spread_reward_alpha_bps=spread_reward_alpha,
        execution_cost_bps=execution_cost,
        uncertainty_penalty_bps=uncertainty_penalty,
        toxicity_penalty_bps=tox * 100,
        resolution_penalty_bps=res * 100,
        expected_edge_bps=expected_edge,
        uncertainty=prob.uncertainty,
        confidence=min(prob.confidence, max(0.0, 1 - (tox + res) / 2)),
        reasons=["structural_edge_model", prob.source] + ([] if cross is None else [cross.explanation]),
    )
