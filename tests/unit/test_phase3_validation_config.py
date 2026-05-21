from pathlib import Path

from polymarket_bot.core.config import load_config
from polymarket_bot.wallets.validation.harness import run_wallet_validation_from_recorded


def test_validation_harness_uses_config_min_samples_and_baselines(tmp_path: Path) -> None:
    cfg = load_config("configs/base.yaml")
    cfg.wallet_validation.min_samples = 999
    cfg.wallet_validation.baselines = ["random_wallet", "no_wallet_signal"]
    rep = run_wallet_validation_from_recorded(
        "tests/fixtures/recorded_state",
        str(tmp_path / "out.json"),
        str(tmp_path / "out.md"),
        cfg.wallet_validation.latency_scenarios_sec,
        train_frac=cfg.wallet_validation.train_frac,
        val_frac=cfg.wallet_validation.val_frac,
        min_samples=cfg.wallet_validation.min_samples,
        baselines=cfg.wallet_validation.baselines,
    )
    assert set(rep["baseline_comparison"].keys()) == {"random_wallet", "no_wallet_signal"}
    assert rep["promotion"]["mode"] == "observe_only"
