import json
from pathlib import Path

from polymarket_bot.adapters.wallets import WalletAdapter


def test_wallet_trade_normalization() -> None:
    payload = json.loads(Path("tests/fixtures/wallet_trades.json").read_text())
    adapter = WalletAdapter(fixture_payloads={"/wallet-trades?wallet=w1&limit=500": payload})
    out = adapter.fetch_wallet_trades("w1")
    assert out[0].wallet_id == "w1"
    assert out[0].market_id == "m1"
