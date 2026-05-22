from prediction_market_bot.adapters.kalshi.client import KalshiAdapter


def test_kalshi_capabilities_wallet_graph_unsupported():
    adapter = KalshiAdapter('https://example.com', fixture_payloads={})
    assert adapter.capabilities.supports_public_wallet_graph is False
    assert adapter.capabilities.supports_live_orders is False
