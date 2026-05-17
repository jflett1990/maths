from __future__ import annotations

from polymarket_bot.wallets.validation.models import PromotionDecision


def promote_policy(metrics: dict[str, float], leakage_ok: bool, min_samples: int, sample_count: int) -> PromotionDecision:
    if not leakage_ok:
        return PromotionDecision("disabled", ["leakage_detected"])
    if sample_count < min_samples:
        return PromotionDecision("observe_only", ["insufficient_samples"])
    if metrics.get("data_quality_score", 1.0) < 0.6:
        return PromotionDecision("observe_only", ["poor_data_quality"])
    if metrics.get("edge_after_latency_bps", 0.0) <= 0 or metrics.get("after_cost_edge_bps", 0.0) <= 0:
        return PromotionDecision("risk_filter_only", ["no_positive_latency_or_cost_edge"])
    if metrics.get("baseline_outperformance_bps", 0.0) <= 0:
        return PromotionDecision("observe_only", ["no_baseline_outperformance"])
    if metrics.get("category_concentration", 0.0) > 0.8 or metrics.get("wallet_concentration", 0.0) > 0.8:
        return PromotionDecision("risk_filter_only", ["concentration_risk"])
    if metrics.get("drawdown_contrib", 0.0) < -0.03 or metrics.get("false_positive_rate", 1.0) > 0.5:
        return PromotionDecision("risk_filter_only", ["risk_metrics_failed"])
    if metrics.get("signal_stability", 0.0) < 0.4:
        return PromotionDecision("observe_only", ["unstable_signal"])
    return PromotionDecision("ranking_boost_allowed", ["passes_conservative_thresholds"])
