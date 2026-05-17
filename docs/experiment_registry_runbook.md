# Experiment Registry Runbook
1. Run recorded validation.
2. Register validation with `scripts/register_validation_run.py`.
3. Evaluate gate with `scripts/evaluate_promotion_gate.py`.
4. Check runtime guard with `scripts/check_config_registry.py`.
5. Expire records using `scripts/expire_experiment.py` when stale.
