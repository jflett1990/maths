import json
from pathlib import Path

from polymarket_bot.adapters.polymarket import PolymarketRESTAdapter


def test_adapter_fixture_parse() -> None:
    payload = json.loads(Path("tests/fixtures/markets.json").read_text())
    adapter = PolymarketRESTAdapter(fixture_payloads={"/markets": payload})
    markets = adapter.fetch_active_markets()
    assert markets[0].market_id == "m1"
