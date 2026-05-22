from prediction_market_bot.adapters.kalshi.auth import KalshiCredentials, build_auth_headers


def test_kalshi_auth_header_names_present():
    headers = build_auth_headers(KalshiCredentials(api_key_id='kid', private_key_pem='pem'), 'GET', '/api_keys')
    assert 'KALSHI-ACCESS-KEY' in headers
    assert 'KALSHI-ACCESS-SIGNATURE' in headers
    assert 'KALSHI-ACCESS-TIMESTAMP' in headers
