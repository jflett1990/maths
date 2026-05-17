from __future__ import annotations

from polymarket_bot.core.models import WalletTrade
from polymarket_bot.wallets.validation.baselines import (
    baseline_category_specialist,
    baseline_most_active,
    baseline_random,
    baseline_top_pnl,
    baseline_top_roi,
)
from polymarket_bot.wallets.validation.dataset import build_validation_rows
from polymarket_bot.wallets.validation.leakage import LeakageError, run_leakage_checks
from polymarket_bot.wallets.validation.metrics import compute_metrics, latency_stress
from polymarket_bot.wallets.validation.policy import promote_policy
from polymarket_bot.wallets.validation.recorded_dataset import build_validation_rows_from_recorded
from polymarket_bot.wallets.validation.report import write_validation_report
from polymarket_bot.wallets.validation.splits import walk_forward_split


def _report(rows, train, test, leakage_ok, leakage_flags):
    m = compute_metrics(test)
    ls = latency_stress(test)
    b_rand, n_rand = baseline_random(test, seed=42)
    b_pnl, n_pnl = baseline_top_pnl(train, test)
    b_roi, n_roi = baseline_top_roi(train, test)
    b_act, n_act = baseline_most_active(train, test)
    b_cat, n_cat = baseline_category_specialist(train, test)
    baselines = {
        "random_wallet": {"value": b_rand, "n": n_rand},
        "top_raw_pnl": {"value": b_pnl, "n": n_pnl},
        "top_roi": {"value": b_roi, "n": n_roi},
        "most_active": {"value": b_act, "n": n_act},
        "category_specialist": {"value": b_cat, "n": n_cat},
        "market_prior_only": {"value": 0.0, "n": len(test)},
        "momentum": {"value": 0.0, "n": len(test)},
        "no_wallet_signal": {"value": 0.0, "n": len(test)},
    }
    policy = promote_policy(
        metrics={**m, "edge_after_latency_bps": ls.get("edge_latency_30s_bps", 0.0), "data_quality_score": 1.0 - ls.get("unavailable_row_rate", 1.0), "after_cost_edge_bps": ls.get("edge_after_slippage_bps", 0.0), "baseline_outperformance_bps": ls.get("edge_latency_30s_bps", 0.0) - b_rand * 10000, "category_concentration": 0.0, "wallet_concentration": 0.0, "signal_stability": 0.5},
        leakage_ok=leakage_ok,
        min_samples=10,
        sample_count=len(test),
    )
    return {
        "dataset_summary": {"rows": len(rows), "train": len(train), "test": len(test)},
        "leakage_checks": leakage_flags,
        "baseline_comparison": baselines,
        "latency_stress_results": ls,
        "metrics": m,
        "promotion": {"mode": policy.mode, "reasons": policy.reasons},
    }


def run_wallet_validation(trades: list[WalletTrade], output_json: str, output_md: str) -> dict:
    rows = build_validation_rows(trades, latency_sec=120)
    train, _, test, _ = walk_forward_split(rows)
    try:
        leakage_flags = run_leakage_checks(rows)
        leakage_ok = True
    except LeakageError as exc:
        leakage_flags, leakage_ok = [str(exc)], False
    report = _report(rows, train, test, leakage_ok, leakage_flags)
    write_validation_report(output_json, output_md, report)
    return report


def run_wallet_validation_from_recorded(state_dir: str, output_json: str, output_md: str, latency_scenarios_sec: list[int]) -> dict:
    rows, q = build_validation_rows_from_recorded(state_dir, latency_scenarios_sec)
    train, _, test, _ = walk_forward_split(rows)
    try:
        leakage_flags = run_leakage_checks(rows)
        leakage_ok = True
    except LeakageError as exc:
        leakage_flags, leakage_ok = [str(exc)], False
    report = _report(rows, train, test, leakage_ok, leakage_flags)
    report["data_quality_summary"] = q
    write_validation_report(output_json, output_md, report)
    return report
