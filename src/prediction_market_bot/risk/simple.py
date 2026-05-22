from __future__ import annotations


def allow_trade(signal: dict, min_expected_edge_bps: float, max_spread_for_aggressive_bps: float) -> tuple[bool, str]:
    ok = signal["spread_bps"] <= max_spread_for_aggressive_bps and signal["expected_edge_bps"] >= min_expected_edge_bps
    return ok, "ok" if ok else "risk_or_edge_reject"


def validate_decision(status: str, size: float, price: float) -> tuple[bool, str | None]:
    valid = size > 0 and 0.0 <= price <= 1.0 and status.lower() in {"open", "active"}
    return valid, None if valid else "validation_failed"
