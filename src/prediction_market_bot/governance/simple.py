from __future__ import annotations


def resolve_signal_permissions(signals_cfg: dict) -> dict:
    account_cfg = (signals_cfg or {}).get("account_intelligence") or (signals_cfg or {}).get("wallet_intelligence") or {}
    enabled = bool(account_cfg.get("enabled", False))
    allow_edge = bool(account_cfg.get("allow_edge_contribution", False))
    if enabled and allow_edge:
        return {
            "effective_signal_mode": "observe_only",
            "allow_positive_alpha": False,
            "downgrade_reasons": ["kalshi_public_wallet_graph_unsupported"],
        }
    return {
        "effective_signal_mode": "observe_only" if enabled else "disabled",
        "allow_positive_alpha": False,
        "downgrade_reasons": ["signal_disabled_or_observe_only"],
    }
