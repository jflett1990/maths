from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from prediction_market_bot.core.models import Market, OrderBook, Trade


@dataclass(slots=True)
class AdapterCapabilities:
    supports_public_markets: bool = True
    supports_order_books: bool = True
    supports_public_trades: bool = True
    supports_historical_trades: bool = True
    supports_websocket_market_data: bool = False
    supports_authenticated_positions: bool = False
    supports_authenticated_fills: bool = False
    supports_public_wallet_graph: bool = False
    supports_rewards_or_incentives: bool = False
    supports_live_orders: bool = False
    supports_demo_environment: bool = True
    supports_order_groups_or_kill_switches: bool = False


class PlatformAdapter(Protocol):
    capabilities: AdapterCapabilities

    def discover_markets(self) -> list[Market]: ...
    def fetch_market_metadata(self, market_ticker: str) -> Market: ...
    def fetch_order_book(self, market_ticker: str) -> OrderBook: ...
    def fetch_trades(self, market_ticker: str, limit: int = 100) -> list[Trade]: ...
    def fetch_historical_trades(self, market_ticker: str, limit: int = 1000) -> list[Trade]: ...
    def fetch_positions(self): ...
    def fetch_fills(self): ...
    def fetch_orders(self): ...
    def health_check(self) -> dict: ...
