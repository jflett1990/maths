from __future__ import annotations

from dataclasses import dataclass, field

from polymarket_bot.governance.guard import guard_signal_runtime


@dataclass(slots=True)
class SignalPermission:
    effective_signal_mode: str
    allow_ranking_boost: bool
    allow_risk_filter: bool
    allow_positive_alpha: bool
    max_alpha_bps: float
    downgrade_reasons: list[str] = field(default_factory=list)
    fatal_errors: list[str] = field(default_factory=list)


def resolve_signal_permission(runtime_mode: str, registry_record: dict | None, dataset_fingerprint: str, report_fingerprint: str) -> SignalPermission:
    try:
        res = guard_signal_runtime(runtime_mode, "observe_only", registry_record, dataset_fingerprint, report_fingerprint)
    except Exception as exc:
        return SignalPermission("disabled", False, False, False, 0.0, [], [str(exc)])
    mode = res["effective_mode"]
    return SignalPermission(
        effective_signal_mode=mode,
        allow_ranking_boost=mode in {"ranking_boost_allowed", "edge_contribution_allowed"},
        allow_risk_filter=mode in {"risk_filter_only", "ranking_boost_allowed", "edge_contribution_allowed"},
        allow_positive_alpha=mode == "edge_contribution_allowed",
        max_alpha_bps=float(res.get("max_wallet_alpha_bps", 0.0)) if mode == "edge_contribution_allowed" else 0.0,
        downgrade_reasons=res.get("warnings", []),
        fatal_errors=[],
    )
