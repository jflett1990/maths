from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from polymarket_bot.core.config import load_config

from polymarket_bot.governance.fingerprints import fingerprint_files, fingerprint_obj, git_code_fingerprint
from polymarket_bot.governance.gate import evaluate_promotion_gate
from polymarket_bot.governance.models import (
    ApprovalRecord,
    BaselineResult,
    DatasetSpec,
    ExperimentSpec,
    ExpirationPolicy,
    MetricSummary,
    SignalSpec,
    ValidationRunRecord,
)
from polymarket_bot.governance.registry import ExperimentRegistry


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--experiment-id", required=True)
    p.add_argument("--signal-name", default="wallet_intelligence")
    p.add_argument("--signal-version", default="v1")
    p.add_argument("--requested-mode", default="observe_only")
    p.add_argument("--report-json", required=True)
    p.add_argument("--dataset-files", nargs="+", required=True)
    p.add_argument("--config-json", default=None)
    p.add_argument("--config", default=None)
    p.add_argument("--allow-edge-contribution", action="store_true")
    args = p.parse_args()

    report = json.loads(open(args.report_json).read())
    gate, expires_at = evaluate_promotion_gate(report, args.requested_mode, args.allow_edge_contribution)
    dataset_fp = fingerprint_files(args.dataset_files)
    if args.config:
        config_payload = json.loads(Path(args.config).read_text()) if args.config.endswith(".json") else json.loads(json.dumps(load_config(args.config).model_dump(mode="json")))
    elif args.config_json:
        config_payload = json.loads(open(args.config_json).read())
    else:
        raise SystemExit("one of --config or --config-json is required")
    config_fp = fingerprint_obj(config_payload)
    report_fp = fingerprint_files([args.report_json])
    code_fp = git_code_fingerprint()
    now = datetime.now(timezone.utc).isoformat()
    baselines = [BaselineResult(k, float(v["value"]), int(v["n"])) for k, v in report.get("baseline_comparison", {}).items() if isinstance(v, dict)]
    rec = ValidationRunRecord(
        schema_version=1,
        run_id=args.experiment_id,
        seq=1,
        created_at=now,
        experiment=ExperimentSpec(args.experiment_id, args.signal_name, args.signal_version, args.requested_mode),
        dataset=DatasetSpec(dataset_fp, "train/val/test", int(report.get("dataset_summary", {}).get("rows", 0)), report.get("data_quality_summary", {})),
        signal=SignalSpec(args.signal_name, args.signal_version, config_fp, code_fp),
        metrics=MetricSummary("ok" if report.get("leakage_checks") == ["ok"] else "fail", report.get("latency_stress_results", {}), baselines),
        gate=gate,
        expiration=ExpirationPolicy(ttl_days=14, expires_at=expires_at),
        approval=ApprovalRecord(None, None),
        report_paths={"json": args.report_json},
        immutable_fingerprints={"dataset_fingerprint": dataset_fp, "config_fingerprint": config_fp, "report_fingerprint": report_fp},
    )
    reg = ExperimentRegistry()
    reg.append(rec)
    print(json.dumps({"experiment_id": args.experiment_id, "granted_mode": gate.granted_mode, "expires_at": expires_at}, sort_keys=True))
