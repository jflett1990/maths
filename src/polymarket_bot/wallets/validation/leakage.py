from __future__ import annotations

from polymarket_bot.wallets.validation.models import ValidationRow


class LeakageError(Exception):
    pass


def run_leakage_checks(rows: list[ValidationRow]) -> list[str]:
    issues: list[str] = []
    for r in rows:
        if not r.known_wallet and r.wallet_score_at_ts != 0:
            issues.append("future_trades_in_score")
        if r.market_status == "open" and r.realized_pnl is not None:
            issues.append("realized_before_resolution")
    if issues:
        raise LeakageError(",".join(sorted(set(issues))))
    return ["ok"]
