import pytest

from prediction_market_bot.adapters.kalshi.client import KalshiAdapter
from prediction_market_bot.core.capabilities import require_capability
from prediction_market_bot.governance.simple import resolve_signal_permissions


def test_require_capability_rejects_unsupported():
    adapter = KalshiAdapter('https://example.com', fixture_payloads={})
    with pytest.raises(RuntimeError):
        require_capability(adapter.capabilities, 'supports_public_wallet_graph')


def test_authenticated_reads_disabled_fail_closed():
    adapter = KalshiAdapter('https://example.com', fixture_payloads={})
    with pytest.raises(NotImplementedError):
        adapter.fetch_positions()


def test_governance_downgrades_account_intelligence():
    perm = resolve_signal_permissions({'account_intelligence': {'enabled': True, 'allow_edge_contribution': True}})
    assert perm['allow_positive_alpha'] is False
    assert perm['effective_signal_mode'] == 'observe_only'
