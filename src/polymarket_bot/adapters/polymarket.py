from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from polymarket_bot.core.models import Market, PriceBar, TradePrint


class AdapterError(Exception):
    pass


class RateLimitError(AdapterError):
    pass


class ParseError(AdapterError):
    pass


class AuthError(AdapterError):
    pass


class ValidationError(AdapterError):
    pass


@dataclass(slots=True)
class RateLimiter:
    min_interval_sec: float
    _last: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        delta = now - self._last
        if delta < self.min_interval_sec:
            time.sleep(self.min_interval_sec - delta)
        self._last = time.monotonic()


class PolymarketRESTAdapter:
    def __init__(self, base_url: str = "https://clob.polymarket.com", timeout_sec: float = 5.0, rate_limit_per_sec: float = 5.0, fixture_payloads: dict[str, Any] | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=timeout_sec)
        self.rate_limiter = RateLimiter(1.0 / rate_limit_per_sec)
        self.fixture_payloads = fixture_payloads or {}

    @retry(
        wait=wait_exponential(multiplier=0.2, min=0.2, max=2),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, TimeoutError)),
        reraise=True,
    )
    def _request(self, path: str) -> Any:
        if path in self.fixture_payloads:
            return self.fixture_payloads[path]
        self.rate_limiter.wait()
        try:
            response = self.client.get(f"{self.base_url}{path}")
        except httpx.TimeoutException as exc:
            raise TimeoutError("timeout") from exc
        if response.status_code == 429:
            raise RateLimitError("rate limited")
        if response.status_code in {401, 403}:
            raise AuthError("auth error")
        if response.status_code == 400:
            raise ValidationError("validation error")
        if response.status_code >= 500:
            raise AdapterError(f"server error {response.status_code}")
        if response.status_code >= 400:
            raise AdapterError(f"http error {response.status_code}")
        return response.json()

    def fetch_active_markets(self) -> list[Market]:
        payload = self._request("/markets")
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return [self._parse_market(r) for r in rows if str(r.get("active", True)).lower() != "false"]

    def fetch_market_metadata(self, market_id: str) -> Market:
        return self._parse_market(self._request(f"/markets/{market_id}"))

    def fetch_price_history(self, market_id: str, limit: int = 100) -> list[PriceBar]:
        payload = self._request(f"/prices-history?market={market_id}&limit={limit}")
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return [PriceBar(market_id=market_id, ts=int(r["t"]), price=float(r["p"]), volume=float(r.get("v", 0.0))) for r in rows]

    def fetch_trades(self, market_id: str, limit: int = 100) -> list[TradePrint]:
        payload = self._request(f"/trades?market={market_id}&limit={limit}")
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return [TradePrint(market_id=market_id, ts=int(r["t"]), side=str(r.get("side", "")), price=float(r["p"]), size=float(r["s"]), wallet=r.get("wallet")) for r in rows]

    def fetch_rewards_config(self, market_id: str) -> float:
        try:
            payload = self._request(f"/rewards?market={market_id}")
        except AdapterError:
            return 0.0
        if isinstance(payload, dict):
            return float(payload.get("reward_bps", 0.0))
        return 0.0

    def _parse_market(self, row: dict[str, Any]) -> Market:
        try:
            yes = float(row.get("yes_price", row.get("bestBid", 0.5)))
            no = float(row.get("no_price", row.get("bestAsk", 1 - yes)))
            return Market(
                market_id=str(row.get("id", row.get("market_id", ""))),
                question=str(row.get("question", "")),
                category=str(row.get("category", "unknown")),
                yes_price=yes,
                no_price=no,
                spread_bps=float(row.get("spread_bps", abs(no - yes) * 10000)),
                liquidity=float(row.get("liquidity", 0.0)),
                open_interest=float(row.get("open_interest", 0.0)),
                event_ts=int(row.get("event_ts", time.time() + 3600)),
                rules_text=str(row.get("rules_text", row.get("description", ""))),
                reward_bps=float(row.get("reward_bps", 0.0)),
                holder_concentration=float(row.get("holder_concentration", 0.3)),
                volatility=float(row.get("volatility", 0.1)),
                status=str(row.get("status", "active")),
                last_update_ts=int(row.get("last_update_ts", time.time())),
                yes_token_id=row.get("yes_token_id"),
                no_token_id=row.get("no_token_id"),
            )
        except (TypeError, ValueError, KeyError) as exc:
            raise ParseError(f"market parse failed: {exc}") from exc


class LiveTradingNotArmedError(AdapterError):
    pass


class LiveExecutionAdapter:
    def __init__(self, api_key: str | None, secret: str | None, armed: bool) -> None:
        if not api_key or not secret or not armed:
            raise LiveTradingNotArmedError("live adapter requires credentials and explicit arming")

    def place_live_order(self, *args, **kwargs):
        raise LiveTradingNotArmedError("live placement not implemented; fail-closed")

    def cancel_live_order(self, *args, **kwargs):
        raise LiveTradingNotArmedError("live cancel not implemented; fail-closed")
