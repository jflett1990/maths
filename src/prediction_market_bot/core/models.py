from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Event:
    event_ticker: str
    title: str
    close_time: datetime | None = None
    expiration_time: datetime | None = None
    status: str = "open"
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ContractSelection:
    market_ticker: str
    side: str
    platform: str


@dataclass(slots=True)
class Market:
    platform: str
    adapter_version: str
    market_ticker: str
    event_ticker: str
    question: str
    status: str
    yes_price: Decimal
    no_price: Decimal
    close_time: datetime | None = None
    expiration_time: datetime | None = None
    series_ticker: str | None = None
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OrderBookLevel:
    price: Decimal
    quantity: Decimal


@dataclass(slots=True)
class OrderBook:
    platform: str
    adapter_version: str
    market_ticker: str
    yes_bid_ladder: list[OrderBookLevel]
    no_bid_ladder: list[OrderBookLevel]
    derived_yes_ask: Decimal | None
    derived_no_ask: Decimal | None
    best_yes_bid: Decimal | None
    best_yes_ask: Decimal | None
    best_no_bid: Decimal | None
    best_no_ask: Decimal | None
    midpoint: Decimal | None
    spread: Decimal | None
    data_quality_flags: list[str] = field(default_factory=list)
    source_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Trade:
    platform: str
    market_ticker: str
    side: str
    price: Decimal
    size: Decimal
    timestamp: datetime
    source_metadata: dict[str, Any] = field(default_factory=dict)
