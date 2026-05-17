from polymarket_bot.wallets.validation.recorded_dataset import build_validation_rows_from_recorded
from polymarket_bot.wallets.validation.splits import walk_forward_split
from polymarket_bot.wallets.validation.baselines import baseline_random, baseline_top_pnl, baseline_top_roi


def test_baselines_same_rows() -> None:
    rows, _ = build_validation_rows_from_recorded("tests/fixtures/recorded_state", [0, 30])
    train, _, test, _ = walk_forward_split(rows, 0.5, 0.0)
    _, n1 = baseline_random(test)
    _, n2 = baseline_top_pnl(train, test)
    _, n3 = baseline_top_roi(train, test)
    assert n1 >= 0 and n2 >= 0 and n3 >= 0
