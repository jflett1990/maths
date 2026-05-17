from __future__ import annotations

import random
from collections import Counter, defaultdict

from polymarket_bot.wallets.validation.models import ValidationRow


def _ret(rows: list[ValidationRow]) -> float:
    vals = [((r.forward_prices.get("30m") or r.entry_price if hasattr(r, 'entry_price') else (r.forward_prices.get("30m") or (r.mid or 0))) - (r.copyable_prices.get("latency_30s") or r.mid or 0)) for r in rows if r.excluded_reason is None]
    return sum(vals) / max(1, len(vals))


def baseline_random(rows: list[ValidationRow], seed: int = 42) -> tuple[float, int]:
    rng = random.Random(seed)
    subset = [r for r in rows if rng.random() < 0.5 and r.excluded_reason is None]
    return _ret(subset), len(subset)


def baseline_top_pnl(rows_train: list[ValidationRow], rows_test: list[ValidationRow]) -> tuple[float, int]:
    pnl = defaultdict(float)
    for r in rows_train:
        pnl[r.wallet_id] += (r.realized_pnl or 0.0)
    top = max(pnl, key=pnl.get) if pnl else ""
    subset = [r for r in rows_test if r.wallet_id == top and r.excluded_reason is None]
    return _ret(subset), len(subset)


def baseline_top_roi(rows_train: list[ValidationRow], rows_test: list[ValidationRow]) -> tuple[float, int]:
    d = defaultdict(lambda: [0.0, 0.0])
    for r in rows_train:
        d[r.wallet_id][0] += (r.realized_pnl or 0.0)
        d[r.wallet_id][1] += (r.implied_prob or 0.5)
    top = max(d, key=lambda w: d[w][0] / d[w][1] if d[w][1] else -1e9) if d else ""
    subset = [r for r in rows_test if r.wallet_id == top and r.excluded_reason is None]
    return _ret(subset), len(subset)


def baseline_most_active(rows_train: list[ValidationRow], rows_test: list[ValidationRow]) -> tuple[float, int]:
    c = Counter(r.wallet_id for r in rows_train)
    top = c.most_common(1)[0][0] if c else ""
    subset = [r for r in rows_test if r.wallet_id == top and r.excluded_reason is None]
    return _ret(subset), len(subset)


def baseline_category_specialist(rows_train: list[ValidationRow], rows_test: list[ValidationRow]) -> tuple[float, int]:
    c = Counter((r.wallet_id, r.category) for r in rows_train)
    if not c:
        return 0.0, 0
    (w, cat), _ = c.most_common(1)[0]
    subset = [r for r in rows_test if r.wallet_id == w and r.category == cat and r.excluded_reason is None]
    return _ret(subset), len(subset)
