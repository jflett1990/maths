from __future__ import annotations

import argparse

from polymarket_bot.wallets.validation.harness import run_wallet_validation_from_recorded


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state-dir", required=True)
    p.add_argument("--out-json", default="state/wallet_validation_report.json")
    p.add_argument("--out-md", default="state/wallet_validation_report.md")
    args = p.parse_args()
    report = run_wallet_validation_from_recorded(args.state_dir, args.out_json, args.out_md, [0, 30, 120, 600])
    print(report["promotion"]) 
