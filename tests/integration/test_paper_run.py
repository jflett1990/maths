from polymarket_bot.app import run_once


def test_paper_run_executes() -> None:
    placed = run_once("configs/base.yaml")
    assert placed >= 0
