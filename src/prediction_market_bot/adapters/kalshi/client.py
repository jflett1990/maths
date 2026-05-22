from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx

from prediction_market_bot.adapters.base import AdapterCapabilities
from prediction_market_bot.adapters.kalshi.auth import build_auth_headers, load_credentials_from_env
from prediction_market_bot.adapters.kalshi.normalization import ADAPTER_VERSION, normalize_orderbook
from prediction_market_bot.core.models import Market, Trade


class KalshiAdapter:
    def __init__(self, base_url: str, timeout_sec: float = 5.0, fixture_payloads: dict[str, Any] | None = None, credentials_env_prefix: str = "KALSHI", authenticated_reads_enabled: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=timeout_sec)
        self.fixture_payloads = fixture_payloads or {}
        self.credentials_env_prefix = credentials_env_prefix
        self.authenticated_reads_enabled = authenticated_reads_enabled
        self.capabilities = AdapterCapabilities(
            supports_websocket_market_data=True,
            supports_authenticated_positions=True,
            supports_authenticated_fills=True,
            supports_public_wallet_graph=False,
            supports_rewards_or_incentives=False,
            supports_live_orders=False,
        )

    def _request(self, path: str) -> Any:
        if path in self.fixture_payloads:
            return self.fixture_payloads[path]
        return self.client.get(f"{self.base_url}{path}").json()

    def _request_authenticated(self, path: str) -> Any:
        if not self.authenticated_reads_enabled:
            raise NotImplementedError("Authenticated Kalshi reads are disabled in this migration until production signing is implemented.")
        creds = load_credentials_from_env(self.credentials_env_prefix)
        headers = build_auth_headers(creds, "GET", path, "")
        return self.client.get(f"{self.base_url}{path}", headers=headers).json()

    def discover_markets(self) -> list[Market]:
        rows = self._request("/markets").get("markets", [])
        return [self._parse_market(r) for r in rows]

    def fetch_market_metadata(self, market_ticker: str) -> Market:
        return self._parse_market(self._request(f"/markets/{market_ticker}").get("market", {}))

    def fetch_order_book(self, market_ticker: str):
        payload = self._request(f"/markets/{market_ticker}/orderbook")
        return normalize_orderbook(payload, market_ticker)

    def fetch_trades(self, market_ticker: str, limit: int = 100) -> list[Trade]:
        rows = self._request(f"/markets/{market_ticker}/trades?limit={limit}").get("trades", [])
        out: list[Trade] = []
        for row in rows:
            out.append(
                Trade(
                    platform="kalshi",
                    market_ticker=market_ticker,
                    side=str(row.get("side", "")),
                    price=Decimal(str(row.get("price", 0))) / Decimal("100"),
                    size=Decimal(str(row.get("count", 0))),
                    timestamp=datetime.fromtimestamp(int(row.get("ts", 0)), tz=timezone.utc),
                    source_metadata={"trade_id": row.get("id")},
                )
            )
        return out

    def fetch_historical_trades(self, market_ticker: str, limit: int = 1000) -> list[Trade]:
        return self.fetch_trades(market_ticker, limit=limit)

    def fetch_positions(self):
        return self._request_authenticated("/portfolio/positions").get("positions", [])

    def fetch_fills(self):
        return self._request_authenticated("/portfolio/fills").get("fills", [])

    def fetch_orders(self):
        return self._request_authenticated("/portfolio/orders").get("orders", [])

    def health_check(self) -> dict:
        try:
            self.discover_markets()
            return {"ok": True, "adapter": "kalshi"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "adapter": "kalshi", "error": str(exc)}

    def place_order(self, *args, **kwargs):
        raise RuntimeError("Live order placement disabled in this migration (fail-closed).")

    def cancel_order(self, *args, **kwargs):
        raise RuntimeError("Live order cancel disabled in this migration (fail-closed).")

    def _parse_market(self, row: dict[str, Any]) -> Market:
        yes = Decimal(str(row.get("yes_bid", 50))) / Decimal("100")
        no = Decimal("1") - yes
        return Market(
            platform="kalshi",
            adapter_version=ADAPTER_VERSION,
            market_ticker=str(row.get("ticker", "")),
            event_ticker=str(row.get("event_ticker", "")),
            question=str(row.get("title", "")),
            status=str(row.get("status", "open")),
            yes_price=yes,
            no_price=no,
            source_metadata={"series_ticker": row.get("series_ticker")},
        )
