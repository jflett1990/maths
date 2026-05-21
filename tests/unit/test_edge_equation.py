from polymarket_bot.core.config import load_config
from polymarket_bot.core.models import Market
from polymarket_bot.signals.edge import evaluate_market


def test_expected_edge_computed() -> None:
    cfg = load_config("configs/base.yaml")
    m = Market("m", "Will A happen by 11:59 PM ET per official source?", "cat", 0.4, 0.59, 80, 15000, 20000, 1, "official ET")
    sig = evaluate_market(m, cfg)
    lhs = sig.forecast_alpha_bps + sig.cross_market_alpha_bps + sig.spread_reward_alpha_bps
    rhs = sig.execution_cost_bps + sig.uncertainty_penalty_bps + sig.toxicity_penalty_bps + sig.resolution_penalty_bps
    assert round(sig.expected_edge_bps, 8) == round(lhs - rhs, 8)
