from datetime import datetime, timedelta, timezone

from polymarket_bot.governance.permissions import resolve_signal_permission


def _rec(mode: str):
    return {
        "gate": {"granted_mode": mode, "max_wallet_alpha_bps": 7},
        "expiration": {"expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()},
        "immutable_fingerprints": {"dataset_fingerprint": "d", "report_fingerprint": "r"},
    }


def test_mapping_modes() -> None:
    p = resolve_signal_permission("paper", _rec("risk_filter_only"), "d", "r")
    assert p.allow_risk_filter and not p.allow_positive_alpha
    p2 = resolve_signal_permission("paper", _rec("ranking_boost_allowed"), "d", "r")
    assert p2.allow_ranking_boost and not p2.allow_positive_alpha
    p3 = resolve_signal_permission("paper", _rec("edge_contribution_allowed"), "d", "r")
    assert p3.allow_positive_alpha and p3.max_alpha_bps == 7
