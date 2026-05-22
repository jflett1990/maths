import json

from prediction_market_bot.recorder.jsonl import PlatformJsonlRecorder


def test_platform_recorder_envelope(tmp_path):
    rec = PlatformJsonlRecorder(str(tmp_path), run_id='r1', platform='kalshi', adapter_version='kalshi-v1')
    rec.write('run_report', {'ok': True})
    line = (tmp_path / 'run_report.jsonl').read_text().strip()
    row = json.loads(line)
    assert row['schema_version'] == 1
    assert row['platform'] == 'kalshi'
    assert row['adapter_version'] == 'kalshi-v1'
    assert row['record_type'] == 'run_report'
