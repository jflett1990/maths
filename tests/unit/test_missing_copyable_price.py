from pathlib import Path

from polymarket_bot.wallets.validation.recorded_dataset import build_validation_rows_from_recorded


def test_missing_copyable_price_explicit(tmp_path) -> None:
    d = tmp_path
    (d / "wallet_observations.jsonl").write_text('{"run_id":"r","schema_version":2,"seq":1,"ts":1000,"wallet_id":"w","market_id":"m","price":0.5,"size":1,"category":"c","liquidity":10,"resolution_clarity":0.5,"resolved":false}\n')
    (d / "market_snapshots.jsonl").write_text('{"run_id":"r","schema_version":2,"seq":1,"ts":900,"market_id":"m","bid":0.4,"ask":0.6,"mid":0.5}\n')
    (d / "resolved_outcomes.jsonl").write_text('')
    rows, _ = build_validation_rows_from_recorded(str(d), [600])
    assert rows[0].copyable_prices["latency_600s"] is None
    assert rows[0].excluded_reason == "missing_copyable_price"
