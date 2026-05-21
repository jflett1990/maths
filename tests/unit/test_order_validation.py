from polymarket_bot.core.config import load_config
from polymarket_bot.core.models import Decision, Market, SignalResult
from polymarket_bot.risk.validation import validate_order


def test_order_validation_rejects_tick_and_size() -> None:
    cfg = load_config("configs/base.yaml")
    m = Market("m", "q", "c", 0.5, 0.5, 50, 1e4, 1e4, 9999999999, "official ET", yes_token_id="y", no_token_id="n")
    sig = SignalResult("m", 0, 0, 0, 0, 0, 0, 0, 100, 0.1, 0.9)
    d = Decision("m", "quote", "yes", -1, 0.503, "r", sig)
    vr = validate_order(d, m, sig, cfg)
    assert not vr.ok
    assert "invalid_size" in vr.reasons
    assert "tick_size_violation" in vr.reasons
