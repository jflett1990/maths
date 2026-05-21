from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ExperimentSpec:
    experiment_id: str
    signal_name: str
    signal_version: str
    requested_mode: str


@dataclass(slots=True)
class DatasetSpec:
    dataset_fingerprint: str
    validation_window: str
    sample_count: int
    data_quality_summary: dict[str, int]


@dataclass(slots=True)
class SignalSpec:
    signal_name: str
    signal_version: str
    config_fingerprint: str
    code_fingerprint: str


@dataclass(slots=True)
class BaselineResult:
    name: str
    value: float
    n: int


@dataclass(slots=True)
class MetricSummary:
    leakage_status: str
    latency_metrics: dict[str, float]
    baseline_results: list[BaselineResult]


@dataclass(slots=True)
class ExpirationPolicy:
    ttl_days: int
    expires_at: str


@dataclass(slots=True)
class ApprovalRecord:
    approver: str | None
    approved_at: str | None


@dataclass(slots=True)
class PromotionGateDecision:
    requested_mode: str
    granted_mode: str
    reasons: list[str]
    allow_wallet_alpha_bps: bool
    max_wallet_alpha_bps: float


@dataclass(slots=True)
class ValidationRunRecord:
    schema_version: int
    run_id: str
    seq: int
    created_at: str
    experiment: ExperimentSpec
    dataset: DatasetSpec
    signal: SignalSpec
    metrics: MetricSummary
    gate: PromotionGateDecision
    expiration: ExpirationPolicy
    approval: ApprovalRecord
    report_paths: dict[str, str]
    immutable_fingerprints: dict[str, str] = field(default_factory=dict)
