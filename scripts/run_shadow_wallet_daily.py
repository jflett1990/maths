from __future__ import annotations

import argparse
import json
from pathlib import Path

from polymarket_bot.wallets.validation.harness import run_wallet_validation_from_recorded


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state-dir", required=True)
    p.add_argument("--out", default="state/shadow_wallet_daily.json")
    a = p.parse_args()
    rep = run_wallet_validation_from_recorded(a.state_dir, "state/_tmp_val.json", "state/_tmp_val.md", [0, 30, 120, 600])
    daily = {
        "markets_observed": rep["dataset_summary"]["rows"],
        "wallet_events_observed": rep["dataset_summary"]["rows"],
        "top_wallet_signals": [],
        "signals_ignored": rep["promotion"]["reasons"],
        "trades_would_improve": rep["metrics"].get("precision_positive", 0),
        "trades_would_harm": rep["metrics"].get("false_positive_rate", 0),
        "bad_trades_blocked": rep["metrics"].get("false_positive_rate", 0),
        "latency_decay": rep["latency_stress_results"],
        "baseline_comparison": rep["baseline_comparison"],
        "promotion_recommendation": rep["promotion"],
        "anomalies": rep.get("data_quality_summary", {}),
    }
    Path(a.out).write_text(json.dumps(daily, indent=2, sort_keys=True))
    print(a.out)
