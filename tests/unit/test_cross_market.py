from polymarket_bot.core.models import Market
from polymarket_bot.signals.cross_market import build_constraints, evaluate_constraints


def test_cross_market_violation_detects_gap() -> None:
    ms = [
        Market("a", "q", "c", 0.7, 0.3, 50, 1e4, 2e4, 1, "official ET"),
        Market("b", "q", "c", 0.5, 0.5, 50, 1e4, 2e4, 1, "official ET"),
    ]
    violations = evaluate_constraints(ms, build_constraints(ms))
    assert violations["a"].violated
    assert violations["a"].alpha_bps > 0
