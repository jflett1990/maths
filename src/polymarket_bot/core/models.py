from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Market:
    market_id: str
    question: str
    category: str
    yes_price: float
    no_price: float
    spread_bps: float
    liquidity: float
    open_interest: float
    event_ts: int
    rules_text: str
    reward_bps: float = 0.0
    holder_concentration: float = 0.0
    volatility: float = 0.0
    status: str = "active"
    last_update_ts: int = 0
    yes_token_id: str | None = None
    no_token_id: str | None = None


@dataclass(slots=True)
class PriceBar:
    market_id: str
    ts: int
    price: float
    volume: float


@dataclass(slots=True)
class TradePrint:
    market_id: str
    ts: int
    side: str
    price: float
    size: float
    wallet: str | None = None


@dataclass(slots=True)
class WalletTrade:
    wallet_id: str
    market_id: str
    ts: int
    side: str
    price: float
    size: float
    category: str
    liquidity: float
    resolution_clarity: float
    resolved: bool
    outcome: int | None = None


@dataclass(slots=True)
class WalletScore:
    wallet_id: str
    score: float
    confidence: float
    specialties: list[str]
    reason_codes: list[str]
    risk_flags: list[str]
    sample_warning: str | None


@dataclass(slots=True)
class WalletSignal:
    market_id: str
    smart_wallet_buy_pressure: float
    smart_wallet_sell_pressure: float
    smart_wallet_consensus: float
    smart_wallet_divergence: float
    specialist_wallet_activity: float
    new_smart_wallet_entry: float
    smart_wallet_exit: float
    toxic_informed_flow_flag: bool
    copy_latency_penalty_bps: float
    crowding_penalty_bps: float
    wallet_alpha_bps: float
    smart_wallet_toxicity_adjustment: float
    confidence: float
    reasons: list[str]


@dataclass(slots=True)
class WalletCluster:
    cluster_id: str
    wallet_ids: list[str]
    confidence: float
    heuristic_labels: list[str]


@dataclass(slots=True)
class ProbabilityEstimate:
    market_id: str
    point: float
    lower: float
    upper: float
    uncertainty: float
    confidence: float
    source: str


@dataclass(slots=True)
class CrossMarketConstraint:
    constraint_id: str
    kind: str
    markets: list[str]
    relation: str


@dataclass(slots=True)
class ConstraintViolation:
    constraint_id: str
    violated: bool
    alpha_bps: float
    confidence: float
    explanation: str


@dataclass(slots=True)
class SignalResult:
    market_id: str
    forecast_alpha_bps: float
    cross_market_alpha_bps: float
    spread_reward_alpha_bps: float
    execution_cost_bps: float
    uncertainty_penalty_bps: float
    toxicity_penalty_bps: float
    resolution_penalty_bps: float
    expected_edge_bps: float
    uncertainty: float
    confidence: float
    wallet_alpha_bps: float = 0.0
    sentiment_alpha_bps: float = 0.0
    oracle_divergence_alpha_bps: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Decision:
    market_id: str
    action: str
    side: str
    size: float
    price: float
    reason: str
    signal: SignalResult
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Fill:
    order_id: str
    market_id: str
    side: str
    price: float
    size: float
    ts: int


@dataclass(slots=True)
class PnLBreakdown:
    market_id: str
    forecast_alpha: float
    spread_capture: float
    adverse_selection: float
    slippage: float
    fees: float
    reward: float
    inventory_mtm: float
    total: float


@dataclass(slots=True)
class RunSnapshot:
    ts: int
    markets: list[Market]
    signals: list[SignalResult]
    decisions: list[Decision]
    risk_state: dict[str, Any]
