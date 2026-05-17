from __future__ import annotations

import argparse

from polymarket_bot.app import run_once


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    result = run_once(args.config)
    print(f"placed_orders={result}")
