# Replay and Debugging
- Use `replay_compare(output_dir, skip_malformed=False)` for strict replay.
- Corrupt JSONL raises `ReplayCorruptionError`.
- Optional `skip_malformed=True` skips malformed lines.

## Wallet validation from recorded state
Use deterministic recorded-state files and `scripts/run_wallet_validation_recorded.py`.
