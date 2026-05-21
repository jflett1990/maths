import pytest

from polymarket_bot.governance.registry import ExperimentRegistry, RegistryError


def test_corrupted_registry_detection(tmp_path) -> None:
    p = tmp_path / "e.jsonl"
    p.write_text('{bad json}\n')
    reg = ExperimentRegistry(str(p), str(tmp_path / "s.json"))
    with pytest.raises(RegistryError):
        reg.materialize_state()
