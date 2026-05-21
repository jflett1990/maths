from __future__ import annotations

from typing import Protocol

from polymarket_bot.sentiment.ingest import NullTextSourceClient, TextSourceClient


class InferenceClient(Protocol):
    async def score_texts(self, texts: list[str]) -> float: ...


class NeutralInferenceClient:
    async def score_texts(self, texts: list[str]) -> float:
        _ = texts
        return 0.0


class SentimentAnalyzer:
    def __init__(self, source: TextSourceClient | None = None, inference: InferenceClient | None = None) -> None:
        self._source = source or NullTextSourceClient()
        self._inference = inference or NeutralInferenceClient()

    async def evaluate_market_context(self, market_id: str) -> float:
        """
        Fails open with neutral sentiment when ingestion/inference has an error.
        """
        try:
            texts = await self._source.fetch_market_context(market_id)
            if not texts:
                return 0.0
            score = await self._inference.score_texts(texts)
            return max(-1.0, min(1.0, float(score)))
        except Exception:  # noqa: BLE001
            return 0.0
