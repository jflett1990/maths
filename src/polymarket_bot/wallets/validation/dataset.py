from __future__ import annotations

from collections import defaultdict

from polymarket_bot.core.models import WalletTrade
from polymarket_bot.wallets.performance import attribute_wallet_performance
from polymarket_bot.wallets.scoring import score_wallet
from polymarket_bot.wallets.validation.models import ValidationRow


def build_validation_rows(trades: list[WalletTrade], latency_sec: int = 30) -> list[ValidationRow]:
    rows: list[ValidationRow] = []
    by_wallet: dict[str, list[WalletTrade]] = defaultdict(list)
    for t in sorted(trades, key=lambda x: x.ts):
        hist = by_wallet[t.wallet_id]
        perf = attribute_wallet_performance(hist)
        score = score_wallet(perf).score if hist else 0.0
        copy_price = min(0.99, t.price + 0.01) if latency_sec > 0 else t.price
        realized = None
        if t.resolved and t.outcome is not None:
            realized = (1 - t.price if t.outcome == 1 and t.side == "buy" else -t.price * 0.5) * t.size
        rows.append(
            ValidationRow(
                ts=t.ts,
                wallet_id=t.wallet_id,
                market_id=t.market_id,
                category=t.category,
                liquidity_bucket="high" if t.liquidity >= 5000 else "low",
                resolution_clarity=t.resolution_clarity,
                wallet_score_at_ts=score,
                wallet_signal_at_ts=1.0 if score > 0 else 0.0,
                implied_prob=t.price,
                bid=t.price - 0.01,
                ask=t.price + 0.01,
                mid=t.price,
                spread_bps=200,
                copyable_prices={f"latency_{latency_sec}s": copy_price},
                forward_prices={"5m": min(0.99, t.price + 0.005), "30m": min(0.99, t.price + 0.01), "2h": min(0.99, t.price + 0.02), "24h": min(0.99, t.price + 0.03)},
                outcome=t.outcome,
                realized_pnl=realized,
                known_wallet=len(hist) > 0,
                market_status="resolved" if t.resolved else "open",
            )
        )
        by_wallet[t.wallet_id].append(t)
    return rows
