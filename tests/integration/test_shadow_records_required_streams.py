from pathlib import Path

from polymarket_bot.app import run_once


def test_shadow_records_streams(tmp_path) -> None:
    cfg = Path('configs/base.yaml').read_text().replace('mode: paper', 'mode: shadow').replace('output_dir: state', f'output_dir: {tmp_path / "state"}')
    p = tmp_path / 'c.yaml'
    p.write_text(cfg)
    run_once(str(p))
    for f in ['market_snapshots.jsonl','wallet_observations.jsonl','signals.jsonl','decisions.jsonl','orders.jsonl','fills.jsonl','pnl.jsonl','run.jsonl','run_report.jsonl','reconciliation_anomalies.jsonl']:
        assert (tmp_path / 'state' / f).exists()
