import pytest

from polymarket_bot.wallets.validation.leakage import LeakageError, run_leakage_checks
from polymarket_bot.wallets.validation.models import ValidationRow


def test_leakage_detection_fails_loudly() -> None:
    rows = [ValidationRow(1, "w", "m", "c", 1, 1, 0.5, 0.5, None, None, None, None, None, 1.0, 1.0, 1.0, False, 0, 0.5, 0, "open")]
    with pytest.raises(LeakageError):
        run_leakage_checks(rows)
