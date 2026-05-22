from __future__ import annotations

import json
from pathlib import Path


class LegacySchemaError(ValueError):
    pass


def read_records(path: str) -> list[dict]:
    rows: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if "record_type" not in row or "platform" not in row:
            raise LegacySchemaError("Unsupported legacy/Polymarket record schema")
        rows.append(row)
    return rows
