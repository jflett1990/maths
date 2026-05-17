import pytest

from polymarket_bot.replay import ReplayCorruptionError, replay_compare


def test_replay_corruption_fails(tmp_path) -> None:
    p = tmp_path / "run.jsonl"
    p.write_text('{bad json}\n')
    with pytest.raises(ReplayCorruptionError):
        replay_compare(str(tmp_path), skip_malformed=False)
