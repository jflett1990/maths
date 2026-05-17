from polymarket_bot.wallets.validation.recorded_dataset import build_validation_rows_from_recorded


def test_recorded_row_construction() -> None:
    rows, q = build_validation_rows_from_recorded("tests/fixtures/recorded_state", [0, 30, 120, 600])
    assert len(rows) == 1
    r = rows[0]
    assert r.mid == 0.5
    assert "latency_30s" in r.copyable_prices
    assert isinstance(q, dict)
