from datetime import datetime, timedelta, timezone

import pytest

from polymarket_bot.governance.gate import evaluate_promotion_gate
from polymarket_bot.governance.guard import guard_signal_runtime


def test_gate_no_higher_than_requested() -> None:
    rep = {"leakage_checks": ["ok"], "dataset_summary": {"test": 20}, "latency_stress_results": {"edge_latency_30s_bps": 10, "edge_after_slippage_bps": 5, "unavailable_row_rate": 0.1}, "baseline_comparison": {"random_wallet": {"value": 0.0, "n": 10}}}
    d, _ = evaluate_promotion_gate(rep, "observe_only", False)
    assert d.granted_mode == "observe_only"


def test_edge_contribution_requires_flag() -> None:
    rep = {"leakage_checks": ["ok"], "dataset_summary": {"test": 20}, "latency_stress_results": {"edge_latency_30s_bps": 10, "edge_after_slippage_bps": 5, "unavailable_row_rate": 0.1}, "baseline_comparison": {"random_wallet": {"value": -0.001, "n": 10}}}
    d, _ = evaluate_promotion_gate(rep, "edge_contribution_allowed", False)
    assert d.granted_mode != "edge_contribution_allowed"


def test_guard_blocks_unregistered_live() -> None:
    with pytest.raises(ValueError):
        guard_signal_runtime("live", "observe_only", None, "d", "r")


def test_guard_blocks_expired() -> None:
    rec = {"gate": {"granted_mode": "edge_contribution_allowed", "max_wallet_alpha_bps": 10}, "expiration": {"expires_at": (datetime.now(timezone.utc)-timedelta(days=1)).isoformat()}, "immutable_fingerprints": {"dataset_fingerprint": "d", "report_fingerprint": "r"}}
    out = guard_signal_runtime("paper", "observe_only", rec, "d", "r")
    assert out["effective_mode"] == "observe_only"
