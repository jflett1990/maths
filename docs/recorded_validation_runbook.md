# Recorded-data Wallet Validation Runbook
1. Capture `market_snapshots.jsonl`, `wallet_observations.jsonl`, `resolved_outcomes.jsonl` with UTC `ts`.
2. Run `python scripts/run_wallet_validation_recorded.py --state-dir <dir>`.
3. Review JSON/MD report and promotion mode.
4. If mode is `observe_only` or `risk_filter_only`, do not enable wallet alpha in production.
