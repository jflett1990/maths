from __future__ import annotations

from datetime import datetime, timedelta, timezone

from polymarket_bot.governance.models import PromotionGateDecision

MODES = ["disabled", "observe_only", "risk_filter_only", "ranking_boost_allowed", "edge_contribution_allowed"]


def _min_mode(a: str, b: str) -> str:
    return MODES[min(MODES.index(a), MODES.index(b))]


def evaluate_promotion_gate(report: dict, requested_mode: str, allow_edge_contribution: bool, now_iso: str | None = None) -> tuple[PromotionGateDecision, str]:
    reasons: list[str] = []
    granted = "observe_only"
    if requested_mode not in MODES:
        requested_mode = "observe_only"
    leakage = report.get("leakage_checks", [])
    if leakage != ["ok"]:
        return PromotionGateDecision(requested_mode, "disabled", ["leakage_detected"], False, 0.0), _exp(now_iso)
    ds = report.get("dataset_summary", {})
    if ds.get("test", 0) < 10:
        return PromotionGateDecision(requested_mode, "observe_only", ["insufficient_test_samples"], False, 0.0), _exp(now_iso)
    lat = report.get("latency_stress_results", {})
    if lat.get("edge_latency_30s_bps", -1) <= 0 or lat.get("edge_after_slippage_bps", -1) <= 0:
        granted = "risk_filter_only"
        reasons.append("no_positive_latency_or_cost_edge")
    b = report.get("baseline_comparison", {})
    rand = b.get("random_wallet", {}).get("value", 0.0) * 10000
    edge = lat.get("edge_latency_30s_bps", 0.0)
    if edge <= rand:
        granted = _min_mode(granted, "observe_only")
        reasons.append("no_random_baseline_outperformance")
    uq = lat.get("unavailable_row_rate", 1.0)
    if uq > 0.4:
        granted = _min_mode(granted, "observe_only")
        reasons.append("high_unavailable_rate")
    granted = _min_mode(granted, requested_mode)
    if granted == "edge_contribution_allowed" and not allow_edge_contribution:
        granted = "ranking_boost_allowed"
        reasons.append("edge_contribution_flag_required")
    allow_alpha = granted == "edge_contribution_allowed"
    cap = 10.0 if allow_alpha else 0.0
    return PromotionGateDecision(requested_mode, granted, reasons or ["pass"], allow_alpha, cap), _exp(now_iso)


def _exp(now_iso: str | None) -> str:
    now = datetime.fromisoformat(now_iso) if now_iso else datetime.now(timezone.utc)
    return (now + timedelta(days=14)).isoformat()
