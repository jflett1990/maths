from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationRow:
    ts: int
    wallet_id: str
    market_id: str
    category: str
    liquidity_bucket: str
    resolution_clarity: float
    wallet_score_at_ts: float
    wallet_signal_at_ts: float
    implied_prob: float | None
    bid: float | None
    ask: float | None
    mid: float | None
    spread_bps: float | None
    copyable_prices: dict[str, float | None]
    forward_prices: dict[str, float | None]
    outcome: int | None
    realized_pnl: float | None
    known_wallet: bool
    market_status: str
    data_quality_flags: list[str] = field(default_factory=list)
    excluded_reason: str | None = None


@dataclass(slots=True)
class SplitResult:
    name: str
    train_n: int
    val_n: int
    test_n: int


@dataclass(slots=True)
class PromotionDecision:
    mode: str
    reasons: list[str]
