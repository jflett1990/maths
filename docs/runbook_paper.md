# Paper Mode Runbook
- Set `mode: paper`.
- Ensure `mode_controls.allow_live_orders: false`.
- Run `python scripts/run_paper.py --config configs/base.yaml`.
- Inspect `state/run_report.json`, `state/signals.jsonl`, `state/quotes.jsonl`, `state/pnl.jsonl`.
