from __future__ import annotations

import uuid
from pathlib import Path

from prediction_market_bot.adapters.kalshi.client import KalshiAdapter
from prediction_market_bot.core.config import AppConfig, load_config
from prediction_market_bot.recorder.jsonl import PlatformJsonlRecorder


def run_once(config_path: str, adapter: KalshiAdapter | None = None) -> int:
    cfg: AppConfig = load_config(config_path)
    if cfg.mode == "live" or cfg.platform.enable_live_orders:
        raise RuntimeError("Live mode is disabled fail-closed for Kalshi migration")

    run_id = str(uuid.uuid4())
    adapter = adapter or KalshiAdapter(base_url=cfg.platform.base_url)
    recorder = PlatformJsonlRecorder(cfg.recorder.output_dir, run_id=run_id, platform="kalshi", adapter_version="kalshi-v1")

    raw_markets = adapter.discover_markets()[: cfg.max_markets_per_cycle]

    decisions = 0
    for pm in raw_markets:
        yes = float(pm.yes_price)
        no = float(pm.no_price)
        spread_bps = abs(no - yes) * 10000
        expected_edge_bps = max(0.0, (0.5 - yes) * 10000)
        signal = {"market_ticker": pm.market_ticker, "expected_edge_bps": expected_edge_bps, "spread_bps": spread_bps}
        ok = spread_bps <= cfg.risk.max_spread_for_aggressive_bps and expected_edge_bps >= cfg.min_expected_edge_bps
        reason = "ok" if ok else "risk_or_edge_reject"
        recorder.write("market_snapshot", {"market_ticker": pm.market_ticker, "event_ticker": pm.event_ticker, "status": pm.status})
        recorder.write("signal_result", signal)
        if not ok:
            recorder.write("decision_context", {"market_ticker": pm.market_ticker, "reason": reason, "allowed": False})
            continue
        decision = {
            "market_id": pm.market_ticker,
            "action": "quote_passive",
            "side": "yes",
            "size": cfg.execution.quote_size,
            "price": yes,
        }
        valid = decision["size"] > 0 and 0.0 <= decision["price"] <= 1.0 and pm.status.lower() in {"open", "active"}
        recorder.write("decision_context", {"market_ticker": pm.market_ticker, "allowed": valid, "reason": None if valid else "validation_failed"})
        if valid and cfg.mode == "paper":
            recorder.write("order_intent", decision)
            recorder.write("paper_fill", {**decision, "fill_price": decision["price"], "fill_size": decision["size"]})
            decisions += 1

    recorder.write("run_report", {"mode": cfg.mode, "platform": "kalshi", "orders_placed": 0, "paper_fills": decisions, "run_safety_status": "observe_only" if cfg.mode == "shadow" else "paper_only"})
    Path(cfg.recorder.output_dir, "run_report.json").write_text('{"orders_placed": 0, "live_orders_enabled": false}')
    return decisions
