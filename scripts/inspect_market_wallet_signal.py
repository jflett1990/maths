from __future__ import annotations

import argparse
import json
from pathlib import Path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state-dir", required=True)
    p.add_argument("--market-id", required=True)
    a = p.parse_args()
    fp = Path(a.state_dir) / "wallet_signals.jsonl"
    rows = [json.loads(x) for x in fp.read_text().splitlines() if x.strip()]
    out = [r for r in rows if str(r.get("market_id")) == a.market_id]
    print(json.dumps(out, indent=2, sort_keys=True))
