import asyncio

from polymarket_bot.sentiment.inference import SentimentAnalyzer


class BoomSource:
    async def fetch_market_context(self, market_id: str) -> list[str]:
        _ = market_id
        raise TimeoutError("timeout")


class GoodSource:
    async def fetch_market_context(self, market_id: str) -> list[str]:
        return [market_id, "headline"]


class GoodInference:
    async def score_texts(self, texts: list[str]) -> float:
        return 2.0 if texts else 0.0


def test_sentiment_fail_open_returns_neutral() -> None:
    analyzer = SentimentAnalyzer(source=BoomSource())
    assert asyncio.run(analyzer.evaluate_market_context("m1")) == 0.0


def test_sentiment_clamps_range() -> None:
    analyzer = SentimentAnalyzer(source=GoodSource(), inference=GoodInference())
    assert asyncio.run(analyzer.evaluate_market_context("m1")) == 1.0
