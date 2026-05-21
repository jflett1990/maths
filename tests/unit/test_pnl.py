from polymarket_bot.core.models import Fill, SignalResult
from polymarket_bot.risk.pnl import pnl_for_fill


def test_pnl_arithmetic() -> None:
    sig = SignalResult("m", 100, 0, 0, 0, 0, 0, 0, 0, 0.1, 0.9)
    pnl = pnl_for_fill(Fill("o", "m", "buy", 0.5, 100, 1), mark=0.55, signal=sig, fee_bps=10, reward_bps=5)
    assert round(pnl.total, 6) == round(pnl.forecast_alpha + pnl.spread_capture - pnl.adverse_selection - pnl.slippage - pnl.fees + pnl.reward + pnl.inventory_mtm, 6)
