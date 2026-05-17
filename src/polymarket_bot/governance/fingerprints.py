from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def _stable(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def fingerprint_obj(obj: Any) -> str:
    return hashlib.sha256(_stable(obj)).hexdigest()


def fingerprint_files(paths: list[str]) -> str:
    acc: list[dict[str, str]] = []
    for p in sorted(paths):
        data = Path(p).read_bytes()
        acc.append({"path": p, "sha256": hashlib.sha256(data).hexdigest()})
    return fingerprint_obj(acc)


def git_code_fingerprint() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return out
    except Exception:
        return "unknown"
