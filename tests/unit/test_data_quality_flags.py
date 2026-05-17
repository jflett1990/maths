from pathlib import Path

from polymarket_bot.wallets.validation.recorded_dataset import build_validation_rows_from_recorded


def test_stale_crossed_flags(tmp_path) -> None:
    d = tmp_path
    (d / "wallet_observations.jsonl").write_text('{"run_id":"r","schema_version":2,"seq":1,"ts":1000,"wallet_id":"w","market_id":"m","price":0.5,"size":1,"category":"c","liquidity":10,"resolution_clarity":0.5,"resolved":false}\n')
    (d / "market_snapshots.jsonl").write_text('{"run_id":"r","schema_version":2,"seq":1,"ts":999,"market_id":"m","bid":0.7,"ask":0.6,"mid":0.65}\n')
    (d / "resolved_outcomes.jsonl").write_text('')
    rows, _ = build_validation_rows_from_recorded(str(d), [0])
    assert "crossed_or_invalid_book" in rows[0].data_quality_flags
