import pytest

from prediction_market_bot.replay.reader import LegacySchemaError, read_records


def test_replay_rejects_legacy_schema(tmp_path):
    p = tmp_path / 'legacy.jsonl'
    p.write_text('{"ts": 1, "market_id": "x"}\n')
    with pytest.raises(LegacySchemaError):
        read_records(str(p))
