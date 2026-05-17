from polymarket_bot.wallets.validation.policy import promote_policy


def test_policy_downgrades_bad_quality() -> None:
    d = promote_policy({"data_quality_score":0.2,"edge_after_latency_bps":10,"after_cost_edge_bps":10,"baseline_outperformance_bps":10,"category_concentration":0.1,"wallet_concentration":0.1,"drawdown_contrib":0,"false_positive_rate":0.1,"signal_stability":0.9}, True, 10, 20)
    assert d.mode == "observe_only"
