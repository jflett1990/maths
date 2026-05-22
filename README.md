# Prediction Market Bot Framework

Safety-first prediction-market research framework with paper/shadow/live separation. Kalshi is the first concrete adapter.

## Quickstart
```bash
python -m pip install -e '.[dev]'
pytest
python scripts/run_paper.py --config configs/kalshi_paper.yaml
python scripts/run_shadow.py --config configs/kalshi_shadow.yaml
```

## Safety Defaults
- `paper`: simulated execution only.
- `shadow`: observe/scoring only, no order placement.
- `live`: fail-closed unless explicitly enabled and armed.
- Kalshi live order placement/cancel is disabled in this migration.

## Runbooks
- `docs/kalshi_migration.md`
- `docs/kalshi_adapter.md`
- `docs/replit_runbook.md`
- `docs/secrets_setup.md`
