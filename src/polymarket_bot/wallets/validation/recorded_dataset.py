from __future__ import annotations

import json
from pathlib import Path

from polymarket_bot.core.models import WalletTrade
from polymarket_bot.wallets.performance import attribute_wallet_performance
from polymarket_bot.wallets.scoring import score_wallet
from polymarket_bot.wallets.validation.models import ValidationRow


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def _find_first_price_after(obs: list[dict], t0: int, market_id: str) -> float | None:
    for r in obs:
        if r.get("market_id") == market_id and int(r.get("ts", 0)) >= t0:
            bid, ask = r.get("bid"), r.get("ask")
            if bid is not None and ask is not None and 0 < bid < ask < 1:
                return (float(bid) + float(ask)) / 2
            mid = r.get("mid")
            if mid is not None and 0 < float(mid) < 1:
                return float(mid)
    return None


def build_validation_rows_from_recorded(state_dir: str, latency_scenarios_sec: list[int]) -> tuple[list[ValidationRow], dict[str, int]]:
    p = Path(state_dir)
    wallet_obs = _load(p / "wallet_observations.jsonl")
    market_obs = _load(p / "market_snapshots.jsonl")
    outcome_obs = _load(p / "resolved_outcomes.jsonl")
    outcomes = {x["market_id"]: x.get("outcome") for x in outcome_obs}

    trades = [WalletTrade(
        wallet_id=str(o["wallet_id"]), market_id=str(o["market_id"]), ts=int(o["ts"]), side=str(o.get("side","buy")),
        price=float(o.get("price", 0.5)), size=float(o.get("size", 0.0)), category=str(o.get("category", "unknown")),
        liquidity=float(o.get("liquidity", 0.0)), resolution_clarity=float(o.get("resolution_clarity", 0.5)),
        resolved=bool(o.get("resolved", False)), outcome=o.get("outcome")
    ) for o in wallet_obs]

    rows: list[ValidationRow] = []
    quality_counts: dict[str, int] = {}
    by_wallet: dict[str, list[WalletTrade]] = {}
    for t in sorted(trades, key=lambda x: x.ts):
        hist = by_wallet.get(t.wallet_id, [])
        ws = score_wallet(attribute_wallet_performance(hist)).score if hist else 0.0
        snapshot = next((m for m in market_obs if m.get("market_id") == t.market_id and int(m.get("ts", 0)) <= t.ts), None)
        flags: list[str] = []
        if snapshot is None:
            flags.append("missing_quote_data")
            bid = ask = mid = spread = implied = None
        else:
            bid = snapshot.get("bid")
            ask = snapshot.get("ask")
            mid = snapshot.get("mid")
            implied = mid
            spread = None if bid is None or ask is None else (float(ask) - float(bid)) * 10000
            if bid is None or ask is None:
                flags.append("missing_quote_data")
            elif not (0 < float(bid) < float(ask) < 1):
                flags.append("crossed_or_invalid_book")
            if spread is not None and spread > 300:
                flags.append("excessive_spread")
        copyable: dict[str, float | None] = {}
        for s in latency_scenarios_sec:
            cp = _find_first_price_after(market_obs, t.ts + s, t.market_id)
            copyable[f"latency_{s}s"] = cp
            if cp is None:
                flags.append("missing_copyable_price")
        fwd = {
            "5m": _find_first_price_after(market_obs, t.ts + 300, t.market_id),
            "30m": _find_first_price_after(market_obs, t.ts + 1800, t.market_id),
            "2h": _find_first_price_after(market_obs, t.ts + 7200, t.market_id),
            "24h": _find_first_price_after(market_obs, t.ts + 86400, t.market_id),
        }
        if fwd["30m"] is None:
            flags.append("insufficient_forward_observations")
        if t.liquidity < 1000:
            flags.append("low_liquidity")
        for f in set(flags):
            quality_counts[f] = quality_counts.get(f, 0) + 1
        rows.append(ValidationRow(
            ts=t.ts, wallet_id=t.wallet_id, market_id=t.market_id, category=t.category,
            liquidity_bucket="high" if t.liquidity >= 5000 else "low", resolution_clarity=t.resolution_clarity,
            wallet_score_at_ts=ws, wallet_signal_at_ts=1.0 if ws > 0 else 0.0,
            implied_prob=None if implied is None else float(implied), bid=None if bid is None else float(bid),
            ask=None if ask is None else float(ask), mid=None if mid is None else float(mid),
            spread_bps=None if spread is None else float(spread), copyable_prices=copyable, forward_prices=fwd,
            outcome=outcomes.get(t.market_id), realized_pnl=None, known_wallet=len(hist) > 0,
            market_status="resolved" if outcomes.get(t.market_id) is not None else "open", data_quality_flags=flags,
            excluded_reason="missing_copyable_price" if all(v is None for v in copyable.values()) else None,
        ))
        by_wallet[t.wallet_id] = hist + [t]
    return rows, quality_counts
