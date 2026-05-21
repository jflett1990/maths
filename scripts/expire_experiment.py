from __future__ import annotations

import argparse
from datetime import datetime, timezone

from polymarket_bot.governance.registry import ExperimentRegistry

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--experiment-id", required=True)
    a = p.parse_args()
    reg = ExperimentRegistry()
    rec = reg.get(a.experiment_id)
    if not rec:
        raise SystemExit(1)
    rec["expiration"]["expires_at"] = datetime.now(timezone.utc).isoformat()
    rec["seq"] = int(rec.get("seq", 1)) + 1
    rec["created_at"] = datetime.now(timezone.utc).isoformat()
    with reg.log_path.open("a", encoding="utf-8") as f:
        import json
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    reg.materialize_state()
    print(a.experiment_id)
