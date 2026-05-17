from polymarket_bot.wallets.validation.policy import promote_policy


def test_policy_conservative_downgrade() -> None:
    d = promote_policy({"edge_after_latency_bps": -1, "precision_positive": 0.9, "drawdown_contrib": 0}, leakage_ok=True, min_samples=10, sample_count=20)
    assert d.mode == "risk_filter_only"
