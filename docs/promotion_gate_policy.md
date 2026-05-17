# Promotion Gate Policy
- Fail closed on leakage.
- Expired or missing validation -> observe_only/disabled.
- No positive latency/cost edge -> risk_filter_only.
- Must outperform random baseline.
- edge_contribution_allowed requires explicit flag.
