from polymarket_bot.core.config import load_config
from polymarket_bot.core.models import Market
from polymarket_bot.signals.edge import evaluate_market


def test_uncertainty_penalty_applied() -> None:
    cfg = load_config("configs/base.yaml")
    m = Market("x", "q", "c", 0.5, 0.5, 50, 10000, 10000, 1, "official ET", volatility=0.4)
    sig = evaluate_market(m, cfg)
    assert sig.uncertainty_penalty_bps > 0
