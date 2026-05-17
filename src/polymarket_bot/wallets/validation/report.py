from __future__ import annotations

import json
from pathlib import Path


def write_validation_report(path_json: str, path_md: str, report: dict) -> None:
    Path(path_json).write_text(json.dumps(report, indent=2, sort_keys=True))
    md = ["# Wallet Validation Report", "", f"promotion: {report['promotion']['mode']}"]
    Path(path_md).write_text("\n".join(md))
