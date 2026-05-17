from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from polymarket_bot.governance.models import ValidationRunRecord


class RegistryError(Exception):
    pass


class ExperimentRegistry:
    def __init__(self, log_path: str = "state/registry_events.jsonl", state_path: str = "state/registry_state.json") -> None:
        self.log_path = Path(log_path)
        self.state_path = Path(state_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_events(self) -> list[dict]:
        if not self.log_path.exists():
            return []
        out: list[dict] = []
        for ln, line in enumerate(self.log_path.read_text().splitlines(), start=1):
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RegistryError(f"corrupted registry at line {ln}") from exc
        return out

    def append(self, rec: ValidationRunRecord) -> None:
        events = self._read_events()
        payload = asdict(rec)
        for e in events:
            if e["experiment"]["experiment_id"] == rec.experiment.experiment_id and e["immutable_fingerprints"] != payload["immutable_fingerprints"]:
                raise RegistryError("conflicting experiment_id fingerprints")
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, sort_keys=True) + "\n")
        self.materialize_state()

    def materialize_state(self) -> dict:
        events = self._read_events()
        by_id = {e["experiment"]["experiment_id"]: e for e in sorted(events, key=lambda x: (x["created_at"], x["seq"]))}
        state = {"experiments": by_id}
        self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True))
        return state

    def list_experiments(self) -> list[str]:
        return sorted(self.materialize_state()["experiments"].keys())

    def get(self, experiment_id: str) -> dict | None:
        return self.materialize_state()["experiments"].get(experiment_id)
