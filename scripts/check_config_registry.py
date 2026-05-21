from __future__ import annotations

import argparse
import json

from polymarket_bot.core.config import load_config
from polymarket_bot.governance.fingerprints import fingerprint_files
from polymarket_bot.governance.guard import guard_signal_runtime
from polymarket_bot.governance.registry import ExperimentRegistry

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--experiment-id", required=True)
    p.add_argument("--mode", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--dataset-files", nargs="+", required=True)
    p.add_argument("--report-json", required=True)
    a = p.parse_args()
    rec = ExperimentRegistry().get(a.experiment_id)
    cfg = load_config(a.config)
    requested_mode = cfg.signals.wallet_intelligence.requested_mode if cfg.signals.wallet_intelligence else "observe_only"
    ds = fingerprint_files(a.dataset_files)
    rf = fingerprint_files([a.report_json])
    out = guard_signal_runtime(a.mode, requested_mode, rec, ds, rf)
    print(json.dumps(out, sort_keys=True))
