from polymarket_bot.core.models import ConstraintViolation, CrossMarketConstraint, Market


def build_constraints(markets: list[Market]) -> list[CrossMarketConstraint]:
    constraints: list[CrossMarketConstraint] = []
    ids = [m.market_id for m in markets]
    if len(ids) >= 2:
        constraints.append(CrossMarketConstraint("sum_pair", "complement", ids[:2], "p1+p2~=1"))
    return constraints


def evaluate_constraints(markets: list[Market], constraints: list[CrossMarketConstraint]) -> dict[str, ConstraintViolation]:
    by_id = {m.market_id: m for m in markets}
    out: dict[str, ConstraintViolation] = {}
    for c in constraints:
        if len(c.markets) != 2:
            continue
        a, b = by_id[c.markets[0]], by_id[c.markets[1]]
        total = a.yes_price + b.yes_price
        gap = abs(total - 1.0)
        alpha_bps = max(0.0, (gap - 0.02) * 10000 * 0.25)
        out[a.market_id] = ConstraintViolation(c.constraint_id, gap > 0.02, alpha_bps, max(0.1, 1 - gap), f"complement gap={gap:.4f}")
        out[b.market_id] = out[a.market_id]
    return out
