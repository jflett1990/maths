from polymarket_bot.wallets.validation.models import ValidationRow
from polymarket_bot.wallets.validation.splits import walk_forward_split


def test_time_split_correctness() -> None:
    rows = [ValidationRow(i, "w", "m", "c", 1, 1, 0.5, 0.5, None, None, None, None, None, None, 0, 0, False, 0, 0.5, 0, "open") for i in range(10)]
    train, val, test, split = walk_forward_split(rows)
    assert split.train_n == len(train)
    assert split.test_n == len(test)
    assert train[-1].ts < test[0].ts
