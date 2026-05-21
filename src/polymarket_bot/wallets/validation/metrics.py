from __future__ import annotations

from polymarket_bot.wallets.validation.models import ValidationRow


def latency_stress(rows: list[ValidationRow]) -> dict[str, float]:
    out: dict[str, float] = {}
    valid_rows = [r for r in rows if r.excluded_reason is None]
    unavailable = 0
    for k in ["latency_0s", "latency_30s", "latency_120s", "latency_600s"]:
        vals = []
        for r in valid_rows:
            cp = r.copyable_prices.get(k)
            fp = r.forward_prices.get("30m")
            if cp is None or fp is None:
                unavailable += 1
                continue
            vals.append(fp - cp)
        out[f"edge_{k}_bps"] = (sum(vals) / max(1, len(vals))) * 10000
    out["unavailable_row_rate"] = unavailable / max(1, len(valid_rows) * 4)
    out["edge_after_spread_bps"] = out.get("edge_latency_30s_bps", 0.0) - 2.0
    out["edge_after_slippage_bps"] = out.get("edge_after_spread_bps", 0.0) - 2.0
    out["edge_after_crowding_bps"] = out.get("edge_after_slippage_bps", 0.0) - 1.0
    return out


def compute_metrics(rows: list[ValidationRow]) -> dict[str, float]:
    valid = [r for r in rows if r.excluded_reason is None]
    pos = [r for r in valid if r.wallet_signal_at_ts > 0]
    improved = sum(1 for r in pos if (r.forward_prices.get("30m") or 0) > (r.copyable_prices.get("latency_30s") or 1e9))
    fp = sum(1 for r in pos if (r.forward_prices.get("30m") or 0) <= (r.copyable_prices.get("latency_30s") or 1e9))
    return {
        "precision_positive": improved / max(1, len(pos)),
        "false_positive_rate": fp / max(1, len(pos)),
        "drawdown_contrib": min([0.0] + [((r.forward_prices.get("30m") or 0) - (r.copyable_prices.get("latency_30s") or 0)) for r in valid]),
    }
