# Polymarket Structural Edge System

Safety-first paper/shadow/live-separated architecture.

## Quickstart
```bash
make setup
pytest
python scripts/run_paper.py --config configs/base.yaml
```

## Modes
- `paper`: simulated execution only.
- `shadow`: observe/scoring only, no order placement.
- `live`: requires explicit enablement + confirmation + armed kill switch.

## Runbooks
- `docs/runbook_paper.md`
- `docs/runbook_shadow.md`
- `docs/live_readiness_checklist.md`
- `docs/risk_controls.md`
- `docs/replay_debugging.md`
- `docs/config_reference.md`
