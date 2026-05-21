from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RecorderError(Exception):
    pass


class JsonlRecorder:
    def __init__(self, output_dir: str, run_id: str, fsync: bool = False, fail_on_error: bool = True) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.fsync = fsync
        self.fail_on_error = fail_on_error
        self.seq = 0

    def write(self, stream: str, payload: dict[str, Any]) -> None:
        self.seq += 1
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        record = {"schema_version": 2, "run_id": self.run_id, "seq": self.seq, "ts": int(now.timestamp()), "timestamp": now.isoformat(), **payload}
        fp = self.output_dir / f"{stream}.jsonl"
        try:
            with fp.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")
                f.flush()
                if self.fsync:
                    import os
                    os.fsync(f.fileno())
        except Exception as exc:
            if self.fail_on_error:
                raise RecorderError(str(exc)) from exc
