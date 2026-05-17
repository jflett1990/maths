from pathlib import Path

import pytest

from polymarket_bot.core.config import load_config


def test_missing_signal_mapping_live_fails(tmp_path) -> None:
    cfg = Path('configs/base.yaml').read_text()
    cfg = cfg.replace('mode: paper', 'mode: live')
    cfg = cfg.replace('allow_live_orders: false', 'allow_live_orders: true')
    cfg = cfg.replace('live_confirmation:', 'live_confirmation: I_ACKNOWLEDGE_LIVE_TRADING')
    cfg = cfg.replace('global_enabled: false', 'global_enabled: true')
    cfg = cfg.replace('registry_path: state/registry_events.jsonl', 'registry_path:')
    p = tmp_path / 'c.yaml'
    p.write_text(cfg)
    with pytest.raises(Exception):
        load_config(str(p))
