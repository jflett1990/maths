from polymarket_bot.core.models import Decision, SignalResult
from polymarket_bot.execution.paper_broker import PaperBroker


def test_cancel_replace_lifecycle() -> None:
    broker = PaperBroker()
    sig = SignalResult("m", 0, 0, 0, 0, 0, 0, 0, 50, 0.1, 0.9)
    d = Decision("m", "quote_passive", "yes", 10, 0.5, "r", sig)
    first = broker.place(d, gtd_sec=1)
    second = broker.replace_quotes("m", [d], gtd_sec=10)
    assert first not in second
    assert len(second) == 1
