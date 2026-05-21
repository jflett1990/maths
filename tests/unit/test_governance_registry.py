from datetime import datetime, timezone

import pytest

from polymarket_bot.governance.models import ApprovalRecord, DatasetSpec, ExperimentSpec, ExpirationPolicy, MetricSummary, PromotionGateDecision, SignalSpec, ValidationRunRecord
from polymarket_bot.governance.registry import ExperimentRegistry, RegistryError


def _rec(exp_id: str, fp: str) -> ValidationRunRecord:
    return ValidationRunRecord(
        1, exp_id, 1, datetime.now(timezone.utc).isoformat(),
        ExperimentSpec(exp_id, "wallet", "v1", "observe_only"),
        DatasetSpec(fp, "w", 10, {}),
        SignalSpec("wallet", "v1", "c", "code"),
        MetricSummary("ok", {}, []),
        PromotionGateDecision("observe_only", "observe_only", ["pass"], False, 0.0),
        ExpirationPolicy(14, datetime.now(timezone.utc).isoformat()),
        ApprovalRecord(None, None),
        {"json": "r"},
        {"dataset_fingerprint": fp, "config_fingerprint": "c", "report_fingerprint": "r"},
    )


def test_registry_conflict_detection(tmp_path) -> None:
    reg = ExperimentRegistry(str(tmp_path / "e.jsonl"), str(tmp_path / "s.json"))
    reg.append(_rec("e1", "x"))
    with pytest.raises(RegistryError):
        reg.append(_rec("e1", "y"))
