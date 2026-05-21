from __future__ import annotations

import argparse
import json
from pathlib import Path

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--state-dir", required=True)
    p.add_argument("--wallet-id", required=True)
    a = p.parse_args()
    fp = Path(a.state_dir) / "wallet_observations.jsonl"
    rows = [json.loads(x) for x in fp.read_text().splitlines() if x.strip()]
    out = [r for r in rows if str(r.get("wallet_id")) == a.wallet_id]
    print(json.dumps(out, indent=2, sort_keys=True))
