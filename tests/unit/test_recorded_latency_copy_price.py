from polymarket_bot.wallets.validation.recorded_dataset import build_validation_rows_from_recorded


def test_copyable_price_after_latency() -> None:
    rows, _ = build_validation_rows_from_recorded("tests/fixtures/recorded_state", [30])
    assert rows[0].copyable_prices["latency_30s"] == 0.51
