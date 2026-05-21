from __future__ import annotations

from typing import Protocol


class TextSourceClient(Protocol):
    async def fetch_market_context(self, market_id: str) -> list[str]: ...


class NullTextSourceClient:
    async def fetch_market_context(self, market_id: str) -> list[str]:
        _ = market_id
        return []
