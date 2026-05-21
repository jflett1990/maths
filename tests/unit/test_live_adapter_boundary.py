import pytest

from polymarket_bot.adapters.polymarket import LiveExecutionAdapter, LiveTradingNotArmedError


def test_live_adapter_fails_closed() -> None:
    with pytest.raises(LiveTradingNotArmedError):
        LiveExecutionAdapter(None, None, False)
