import json
from pathlib import Path

from polymarket_bot.app import run_once


def test_run_report_has_permission(tmp_path) -> None:
    cfg = Path('configs/base.yaml').read_text().replace('output_dir: state', f'output_dir: {tmp_path / "state"}')
    p = tmp_path / 'c.yaml'
    p.write_text(cfg)
    run_once(str(p))
    rep = json.loads((tmp_path / 'state' / 'run_report.json').read_text())
    assert 'wallet_signal_permission' in rep
    assert 'reconciliation_anomalies' in rep
