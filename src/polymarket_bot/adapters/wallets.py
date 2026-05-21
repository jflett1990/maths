from __future__ import annotations

from typing import Any

from polymarket_bot.adapters.polymarket import AdapterError, PolymarketRESTAdapter
from polymarket_bot.core.models import WalletTrade


class WalletAdapter(PolymarketRESTAdapter):
    def __init__(self, *args: Any, fixture_payloads: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(*args, fixture_payloads=fixture_payloads, **kwargs)

    def fetch_wallet_trades(self, wallet_id: str, limit: int = 500) -> list[WalletTrade]:
        payload = self._request(f"/wallet-trades?wallet={wallet_id}&limit={limit}")
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return [
            WalletTrade(
                wallet_id=wallet_id,
                market_id=str(r["market_id"]),
                ts=int(r["ts"]),
                side=str(r["side"]),
                price=float(r["price"]),
                size=float(r["size"]),
                category=str(r.get("category", "unknown")),
                liquidity=float(r.get("liquidity", 0.0)),
                resolution_clarity=float(r.get("resolution_clarity", 0.5)),
                resolved=bool(r.get("resolved", False)),
                outcome=None if r.get("outcome") is None else int(r["outcome"]),
            )
            for r in rows
        ]

    def fetch_wallet_positions(self, wallet_id: str) -> dict[str, float]:
        payload = self._request(f"/wallet-positions?wallet={wallet_id}")
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return {str(r["market_id"]): float(r["position"]) for r in rows}

    def fetch_wallet_market_exposures(self, wallet_id: str) -> dict[str, float]:
        try:
            payload = self._request(f"/wallet-exposure?wallet={wallet_id}")
        except AdapterError:
            return {}
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return {str(r["market_id"]): float(r["notional"]) for r in rows}
