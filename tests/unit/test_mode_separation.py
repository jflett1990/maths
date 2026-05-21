import pytest

from polymarket_bot.core.config import AppConfig, load_config


def test_live_mode_requires_explicit_confirmation(tmp_path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text("""
mode: live
poll_interval_sec: 1
min_expected_edge_bps: 1
max_markets_per_cycle: 1
risk: {max_position_per_market: 1, max_event_exposure: 1, max_category_exposure: 1, max_daily_loss: 1, max_drawdown: 1, min_liquidity: 1, max_spread_for_aggressive_bps: 1, resolution_risk_max: 0.5, toxicity_max: 0.5}
execution: {mode: passive, tick_size: 0.01, quote_levels: 1, quote_size: 1, post_only: true, stale_quote_sec: 1, slippage_bps_limit: 1, gtd_minutes_before_catalyst: 1, max_orders_per_run: 1, max_order_notional_per_run: 1}
penalties: {uncertainty_haircut: 0.5, reward_haircut: 0.5, toxicity_scale: 1, resolution_scale: 1}
recorder: {output_dir: state, flush_every: 1}
mode_controls: {allow_live_orders: false, require_kill_switch_armed: true}
kill_switch: {global_enabled: false, per_market_disabled: []}
""")
    with pytest.raises(Exception):
        load_config(str(cfg))


def test_shadow_observe_only_default() -> None:
    cfg = load_config("configs/base.yaml")
    assert cfg.mode_controls.shadow_observe_only
