from polymarket_bot.app import run_once
from polymarket_bot.replay import replay_compare


def test_replay_determinism() -> None:
    run_once("configs/base.yaml")
    cmp = replay_compare("state")
    assert cmp["mismatches"] == 0
