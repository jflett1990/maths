from polymarket_bot.reconciliation import reconcile_state


def test_reconciliation_flags() -> None:
    an = reconcile_state(["o1"], ["o1", "o1"], [], ["f1"], [], [1, 3])
    codes = {a.code for a in an}
    assert "duplicate_active_orders" in codes
    assert "recorded_not_stateful_fill" in codes
    assert "recorder_sequence_gap" in codes
