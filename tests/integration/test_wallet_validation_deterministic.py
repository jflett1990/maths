import json
from pathlib import Path

from polymarket_bot.adapters.wallets import WalletAdapter
from polymarket_bot.wallets.validation.harness import run_wallet_validation


def test_wallet_validation_deterministic(tmp_path) -> None:
    payload = json.loads(Path("tests/fixtures/wallet_trades.json").read_text())
    ad = WalletAdapter(fixture_payloads={"/wallet-trades?wallet=w1&limit=500": payload})
    trades = ad.fetch_wallet_trades("w1")
    r1 = run_wallet_validation(trades, str(tmp_path / "a.json"), str(tmp_path / "a.md"))
    r2 = run_wallet_validation(trades, str(tmp_path / "b.json"), str(tmp_path / "b.md"))
    assert r1 == r2
