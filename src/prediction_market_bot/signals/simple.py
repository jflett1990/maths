from __future__ import annotations


def compute_signal(yes_price: float, no_price: float) -> dict:
    spread_bps = abs(no_price - yes_price) * 10000
    expected_edge_bps = max(0.0, (0.5 - yes_price) * 10000)
    return {"expected_edge_bps": expected_edge_bps, "spread_bps": spread_bps}
