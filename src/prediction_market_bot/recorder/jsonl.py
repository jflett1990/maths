from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RecorderError(Exception):
    pass


class PlatformJsonlRecorder:
    def __init__(self, output_dir: str, run_id: str, platform: str, adapter_version: str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.platform = platform
        self.adapter_version = adapter_version
        self.seq = 0

    def write(self, record_type: str, payload: Any) -> None:
        self.seq += 1
        ts = datetime.now(timezone.utc)
        normalized_payload = asdict(payload) if is_dataclass(payload) else payload
        record = {
            "schema_version": 1,
            "run_id": self.run_id,
            "seq": self.seq,
            "timestamp": ts.isoformat(),
            "platform": self.platform,
            "adapter_version": self.adapter_version,
            "record_type": record_type,
            "payload": normalized_payload,
        }
        with (self.output_dir / f"{record_type}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
