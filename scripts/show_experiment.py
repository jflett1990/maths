from __future__ import annotations

import argparse
import json

from polymarket_bot.governance.registry import ExperimentRegistry

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--experiment-id", required=True)
    a = p.parse_args()
    print(json.dumps(ExperimentRegistry().get(a.experiment_id), indent=2, sort_keys=True))
