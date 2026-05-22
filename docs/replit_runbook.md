# Replit/Local Runbook

Safe commands:

```bash
python -m pip install -e '.[dev]'
pytest
python scripts/run_paper.py --config configs/kalshi_paper.yaml
python scripts/run_shadow.py --config configs/kalshi_shadow.yaml
python scripts/run_kalshi_shadow_daily.py --config configs/kalshi_shadow.yaml
python scripts/run_validation.py --config configs/kalshi_shadow.yaml
```

No command here should place live orders.
