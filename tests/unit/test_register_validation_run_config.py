import json
import os
import subprocess
import sys
from pathlib import Path


def test_register_validation_run_accepts_yaml_config(tmp_path: Path) -> None:
    report = {
        "leakage_checks": ["ok"],
        "dataset_summary": {"rows": 10, "test": 10},
        "latency_stress_results": {"edge_latency_30s_bps": 1.0, "edge_after_slippage_bps": 1.0, "unavailable_row_rate": 0.0},
        "baseline_comparison": {"random_wallet": {"value": 0.0, "n": 10}},
    }
    report_path = tmp_path / "report.json"
    report_path.write_text(json.dumps(report))
    repo = Path.cwd()
    cfg = repo / "configs/base.yaml"
    dataset = repo / "tests/fixtures/recorded_state/market_snapshots.jsonl"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}
    subprocess.check_call([
        sys.executable,
        str(Path.cwd() / "scripts" / "register_validation_run.py"),
        "--experiment-id", "exp_cfg",
        "--report-json", str(report_path),
        "--dataset-files", str(dataset),
        "--config", str(cfg),
    ], cwd=tmp_path, env=env)
    assert (tmp_path / "state" / "registry_events.jsonl").exists()
