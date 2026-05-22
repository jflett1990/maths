from __future__ import annotations

from decimal import Decimal

from prediction_market_bot.core.models import OrderBook, OrderBookLevel


ADAPTER_VERSION = "kalshi-v1"


def _dollars_from_cents(value: int | float | str | Decimal) -> Decimal:
    return Decimal(str(value)) / Decimal("100")


def normalize_orderbook(payload: dict, market_ticker: str) -> OrderBook:
    yes_rows = payload.get("yes", [])
    no_rows = payload.get("no", [])
    yes_bids = [OrderBookLevel(price=_dollars_from_cents(p), quantity=Decimal(str(q))) for p, q in yes_rows]
    no_bids = [OrderBookLevel(price=_dollars_from_cents(p), quantity=Decimal(str(q))) for p, q in no_rows]

    best_yes_bid = max((x.price for x in yes_bids), default=None)
    best_no_bid = max((x.price for x in no_bids), default=None)
    derived_yes_ask = (Decimal("1") - best_no_bid) if best_no_bid is not None else None
    derived_no_ask = (Decimal("1") - best_yes_bid) if best_yes_bid is not None else None
    midpoint = None
    spread = None
    if best_yes_bid is not None and derived_yes_ask is not None:
        midpoint = (best_yes_bid + derived_yes_ask) / Decimal("2")
        spread = derived_yes_ask - best_yes_bid

    flags: list[str] = []
    if not yes_bids or not no_bids:
        flags.append("missing_side")
    if spread is not None and spread < 0:
        flags.append("crossed_book")

    return OrderBook(
        platform="kalshi",
        adapter_version=ADAPTER_VERSION,
        market_ticker=market_ticker,
        yes_bid_ladder=yes_bids,
        no_bid_ladder=no_bids,
        derived_yes_ask=derived_yes_ask,
        derived_no_ask=derived_no_ask,
        best_yes_bid=best_yes_bid,
        best_yes_ask=derived_yes_ask,
        best_no_bid=best_no_bid,
        best_no_ask=derived_no_ask,
        midpoint=midpoint,
        spread=spread,
        data_quality_flags=flags,
        source_metadata={"raw_present": True},
    )
