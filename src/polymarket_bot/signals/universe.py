from polymarket_bot.core.models import Market


def rank_universe(markets: list[Market], top_n: int) -> list[Market]:
    def score(m: Market) -> float:
        return (m.liquidity / 1000) + (m.open_interest / 5000) + m.reward_bps - (m.spread_bps / 50)

    return sorted(markets, key=score, reverse=True)[:top_n]
