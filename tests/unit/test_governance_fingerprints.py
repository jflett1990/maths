from polymarket_bot.governance.fingerprints import fingerprint_obj


def test_fingerprint_deterministic() -> None:
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert fingerprint_obj(a) == fingerprint_obj(b)
