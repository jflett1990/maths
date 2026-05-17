# Signal Permission Matrix
- disabled: signal off
- observe_only: log only
- risk_filter_only: may block/widen only
- ranking_boost_allowed: ranking impact, no edge term
- edge_contribution_allowed: can affect edge term (capped)

Runtime enforcement:
- unregistered/expired/mismatch => observe_only (paper/shadow) or fail-closed (live).
- ranking_boost_allowed cannot add wallet alpha.
- risk_filter_only cannot add wallet alpha.
- edge_contribution_allowed required for wallet_alpha_bps and capped.
