from polymarket_bot.core.models import Fill, PnLBreakdown, SignalResult


def pnl_for_fill(fill: Fill, mark: float, signal: SignalResult, fee_bps: float, reward_bps: float) -> PnLBreakdown:
    direction = 1 if fill.side == "buy" else -1
    inventory_mtm = direction * (mark - fill.price) * fill.size
    spread_capture = max(0.0, abs(mark - fill.price) * fill.size * 0.5)
    adverse = max(0.0, -inventory_mtm * 0.2)
    slippage = abs(mark - fill.price) * fill.size * 0.1
    fees = fill.price * fill.size * fee_bps / 10000
    reward = fill.price * fill.size * reward_bps / 10000
    forecast_alpha = signal.forecast_alpha_bps / 10000 * fill.size
    total = forecast_alpha + spread_capture - adverse - slippage - fees + reward + inventory_mtm
    return PnLBreakdown(fill.market_id, forecast_alpha, spread_capture, adverse, slippage, fees, reward, inventory_mtm, total)
