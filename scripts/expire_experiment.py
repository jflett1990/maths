from __future__ import annotations

import argparse
import json
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
    reg.state_path.write_text(json.dumps({"experiments": {**reg.materialize_state()["experiments"], a.experiment_id: rec}}, indent=2, sort_keys=True))
    print(a.experiment_id)
