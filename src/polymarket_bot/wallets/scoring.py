from __future__ import annotations

from polymarket_bot.core.models import WalletScore
from polymarket_bot.wallets.performance import WalletPerformance


def score_wallet(perf: WalletPerformance) -> WalletScore:
    reasons: list[str] = []
    risks: list[str] = []
    sample_warning = None
    sample_factor = min(1.0, perf.resolved_market_count / 25)
    if perf.resolved_market_count < 10:
        sample_warning = "small_sample"
        reasons.append("small_sample_penalty")
    if perf.resolved_market_count == 0:
        reasons.append("unresolved_only_penalty")
        risks.append("unresolved_only")
    raw = (perf.liquidity_adjusted_return * 100) + (perf.ambiguity_adjusted_return * 100) + perf.sharpe_like * 10
    score = raw * sample_factor
    confidence = min(1.0, 0.2 + sample_factor * 0.8)
    if perf.ambiguity_adjusted_return < 0:
        risks.append("ambiguous_market_exposure")
    return WalletScore(perf.wallet_id, score, confidence, perf.category_specialization, reasons or ["balanced"], risks, sample_warning)
