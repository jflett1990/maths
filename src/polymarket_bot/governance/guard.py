from __future__ import annotations

from datetime import datetime, timezone

MODES = ["disabled", "observe_only", "risk_filter_only", "ranking_boost_allowed", "edge_contribution_allowed"]


def _clamp_mode(granted: str, requested: str) -> str:
    try:
        gi = MODES.index(granted)
    except ValueError:
        gi = 0
    try:
        ri = MODES.index(requested)
    except ValueError:
        ri = 1
    return MODES[min(gi, ri)]


def guard_signal_runtime(mode: str, config_requested_mode: str, registry_record: dict | None, dataset_fingerprint: str, report_fingerprint: str) -> dict:
    warnings: list[str] = []
    if registry_record is None:
        eff = "disabled" if mode == "live" else "observe_only"
        if mode == "live":
            raise ValueError("live mode: unregistered signal")
        return {"effective_mode": eff, "allow_wallet_alpha": False, "warnings": ["unregistered_signal"]}
    gate = registry_record["gate"]
    exp = datetime.fromisoformat(registry_record["expiration"]["expires_at"])
    if datetime.now(timezone.utc) > exp:
        if mode == "live":
            raise ValueError("live mode: expired validation")
        return {"effective_mode": "observe_only", "allow_wallet_alpha": False, "warnings": ["expired_validation"]}
    imm = registry_record.get("immutable_fingerprints", {})
    if imm.get("dataset_fingerprint") != dataset_fingerprint or imm.get("report_fingerprint") != report_fingerprint:
        if mode == "live":
            raise ValueError("live mode: fingerprint mismatch")
        warnings.append("fingerprint_mismatch")
        return {"effective_mode": "observe_only", "allow_wallet_alpha": False, "warnings": warnings}
    granted = _clamp_mode(gate["granted_mode"], config_requested_mode)
    if granted == "risk_filter_only":
        return {"effective_mode": "risk_filter_only", "allow_wallet_alpha": False, "warnings": warnings}
    if granted == "ranking_boost_allowed":
        return {"effective_mode": "ranking_boost_allowed", "allow_wallet_alpha": False, "warnings": warnings}
    if granted == "edge_contribution_allowed":
        return {"effective_mode": "edge_contribution_allowed", "allow_wallet_alpha": True, "max_wallet_alpha_bps": gate.get("max_wallet_alpha_bps", 0.0), "warnings": warnings}
    return {"effective_mode": granted, "allow_wallet_alpha": False, "warnings": warnings}
