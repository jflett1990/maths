from decimal import Decimal

from prediction_market_bot.adapters.kalshi.normalization import normalize_orderbook


def test_derived_asks_from_complement():
    ob = normalize_orderbook({"yes": [[55, 10]], "no": [[40, 8]]}, "KXTEST")
    assert ob.best_yes_bid == Decimal('0.55')
    assert ob.derived_yes_ask == Decimal('0.60')
    assert ob.derived_no_ask == Decimal('0.45')


def test_data_quality_flags_for_missing_and_crossed():
    ob_missing = normalize_orderbook({"yes": [], "no": [[70, 1]]}, "KXTEST")
    assert "missing_side" in ob_missing.data_quality_flags

    ob_crossed = normalize_orderbook({"yes": [[70, 1]], "no": [[40, 1]]}, "KXTEST")
    assert "crossed_book" in ob_crossed.data_quality_flags
