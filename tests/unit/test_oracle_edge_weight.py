import pytest
from polymarket_bot.core.config import load_config
from polymarket_bot.core.models import Market
from polymarket_bot.signals.edge import evaluate_market


def test_oracle_and_sentiment_contribute_to_edge(tmp_path) -> None:
    cfg_path = tmp_path / "cfg.yaml"
    cfg_path.write_text(
        """
mode: paper
poll_interval_sec: 1
min_expected_edge_bps: 0
max_markets_per_cycle: 1
risk: {max_position_per_market: 1, max_event_exposure: 1, max_category_exposure: 1, max_daily_loss: 1, max_drawdown: 1, min_liquidity: 1, max_spread_for_aggressive_bps: 1000, resolution_risk_max: 1, toxicity_max: 1}
execution: {mode: passive, tick_size: 0.01, quote_levels: 1, quote_size: 1, post_only: true, stale_quote_sec: 1, slippage_bps_limit: 1, gtd_minutes_before_catalyst: 1}
penalties: {uncertainty_haircut: 0.0, reward_haircut: 0.0, toxicity_scale: 1.0, resolution_scale: 1.0}
recorder: {output_dir: state, flush_every: 1, fsync: false, fail_on_error: true}
edge_weights: {orderbook: 1.0, sentiment: 2.0, oracle_divergence: 1.0}
"""
    )
    cfg = load_config(cfg_path.as_posix())
    market = Market("m1", "q", "c", 0.5, 0.5, 10, 10000, 1, 0, "rules")
    signal = evaluate_market(market, cfg, sentiment_score=0.5, oracle_probability=0.6)
    assert signal.sentiment_alpha_bps == 100.0
    assert signal.oracle_divergence_alpha_bps == pytest.approx(1000.0)
