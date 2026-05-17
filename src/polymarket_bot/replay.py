from __future__ import annotations

import json
from pathlib import Path


class ReplayCorruptionError(Exception):
    pass


def _load_jsonl(path: Path, skip_malformed: bool) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for ln, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            if skip_malformed:
                continue
            raise ReplayCorruptionError(f"Malformed JSONL at {path}:{ln}") from exc
    return out


def replay_compare(output_dir: str, skip_malformed: bool = False) -> dict[str, int]:
    base = Path(output_dir)
    decisions = _load_jsonl(base / "decisions.jsonl", skip_malformed)
    fills = _load_jsonl(base / "fills.jsonl", skip_malformed)
    run = _load_jsonl(base / "run.jsonl", skip_malformed)
    placed = run[-1]["placed"] if run else 0
    mismatches = 0 if placed == len(fills) else 1
    return {"placed": placed, "fills": len(fills), "decisions": len(decisions), "mismatches": mismatches}
