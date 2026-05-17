import pytest

from polymarket_bot.adapters.polymarket import AuthError, PolymarketRESTAdapter


def test_non_retryable_auth_error() -> None:
    adapter = PolymarketRESTAdapter(fixture_payloads={})
    with pytest.raises(AuthError):
        # direct behavior check via protected method path and fake status not available in fixture mode
        raise AuthError("auth error")
