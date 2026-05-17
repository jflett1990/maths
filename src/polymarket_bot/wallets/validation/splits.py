from __future__ import annotations

from polymarket_bot.wallets.validation.models import SplitResult, ValidationRow


def walk_forward_split(rows: list[ValidationRow], train_frac: float = 0.6, val_frac: float = 0.2) -> tuple[list[ValidationRow], list[ValidationRow], list[ValidationRow], SplitResult]:
    rows = sorted(rows, key=lambda r: r.ts)
    n = len(rows)
    t = int(n * train_frac)
    v = int(n * (train_frac + val_frac))
    train, val, test = rows[:t], rows[t:v], rows[v:]
    return train, val, test, SplitResult("main", len(train), len(val), len(test))
