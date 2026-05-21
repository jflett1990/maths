from polymarket_bot.core.config import load_config
from polymarket_bot.core.models import Market
from polymarket_bot.signals.edge import evaluate_market
from polymarket_bot.risk.engine import allow_trade


def test_resolution_risk_blocks_trade() -> None:
    cfg = load_config("configs/base.yaml")
    m = Market("x", "Will major event happen?", "news", 0.5, 0.49, 60, 10000, 10000, 1, "Likely based on reports")
    sig = evaluate_market(m, cfg)
    ok, reason = allow_trade(m, sig, cfg)
    assert not ok
    assert reason == "resolution_risk_gate"
