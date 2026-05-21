from __future__ import annotations

import argparse
from polymarket_bot.core.config import load_config

from polymarket_bot.wallets.validation.harness import run_wallet_validation_from_recorded


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state-dir", required=True)
    p.add_argument("--out-json", default="state/wallet_validation_report.json")
    p.add_argument("--out-md", default="state/wallet_validation_report.md")
    p.add_argument("--config", default=None)
    args = p.parse_args()
    latency = [0, 30, 120, 600]
    out_json = args.out_json
    out_md = args.out_md
    if args.config:
        cfg = load_config(args.config)
        latency = cfg.wallet_validation.latency_scenarios_sec
        out_json = cfg.wallet_validation.report_json_path
        out_md = cfg.wallet_validation.report_md_path
    report = run_wallet_validation_from_recorded(args.state_dir, out_json, out_md, latency)
    print(report["promotion"]) 
