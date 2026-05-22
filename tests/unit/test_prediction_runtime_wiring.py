from prediction_market_bot.app import run_once
from prediction_market_bot.adapters.kalshi.client import KalshiAdapter


def test_runtime_uses_neutral_runner_and_stays_non_live(tmp_path):
    cfg = tmp_path / 'c.yaml'
    cfg.write_text(
        'mode: shadow\nmax_markets_per_cycle: 1\nmin_expected_edge_bps: 0\n'
        'risk:\n  max_position_per_market: 10\n  max_event_exposure: 10\n  max_category_exposure: 10\n  max_daily_loss: 10\n  max_drawdown: 10\n  min_liquidity: 0\n  max_spread_for_aggressive_bps: 999\n  resolution_risk_max: 1\n  toxicity_max: 1\n'
        'execution:\n  mode: shadow\n  tick_size: 0.01\n  quote_levels: 1\n  quote_size: 1\n  post_only: true\n  stale_quote_sec: 1\n  slippage_bps_limit: 100\n  gtd_minutes_before_catalyst: 1\n'
        'penalties:\n  uncertainty_haircut: 0.1\n  reward_haircut: 1.0\n  toxicity_scale: 1\n  resolution_scale: 1\n'
        'recorder:\n  output_dir: ' + str(tmp_path / 'out') + '\n  flush_every: 1\n  fsync: false\n  fail_on_error: true\n'
        'adapters:\n  clob_base_url: https://demo-api.kalshi.co/trade-api/v2\n'
    )
    adapter = KalshiAdapter('https://x', fixture_payloads={'/markets': {'markets': []}})
    assert run_once(str(cfg), adapter=adapter) == 0
