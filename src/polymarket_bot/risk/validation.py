from __future__ import annotations

import time

from polymarket_bot.core.config import AppConfig
from polymarket_bot.core.models import Decision, Market, SignalResult
from polymarket_bot.core.safety import ValidationResult


def validate_order(decision: Decision, market: Market, signal: SignalResult, cfg: AppConfig, position: float = 0.0) -> ValidationResult:
    reasons: list[str] = []
    if market.status != "active":
        reasons.append("market_not_active")
    if market.yes_token_id is None or market.no_token_id is None:
        reasons.append("missing_token_ids")
    if decision.side not in {"yes", "no"}:
        reasons.append("invalid_side")
    if not (0.0 < decision.price < 1.0):
        reasons.append("invalid_price_bounds")
    if decision.size <= 0:
        reasons.append("invalid_size")
    if round(decision.price / cfg.execution.tick_size) * cfg.execution.tick_size != decision.price:
        reasons.append("tick_size_violation")
    if abs(position + decision.size) > cfg.risk.max_position_per_market:
        reasons.append("inventory_limit")
    catalyst_cutoff = market.event_ts - cfg.execution.gtd_minutes_before_catalyst * 60
    if int(time.time()) >= catalyst_cutoff:
        reasons.append("catalyst_blackout")
    if signal.expected_edge_bps < cfg.min_expected_edge_bps:
        reasons.append("edge_below_threshold")
    return ValidationResult(ok=not reasons, reasons=reasons)
