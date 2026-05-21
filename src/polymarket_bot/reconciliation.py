from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReconciliationAnomaly:
    code: str
    severity: str
    market_id: str | None
    details: str


def reconcile_state(intended_order_ids: list[str], active_order_ids: list[str], recorded_order_ids: list[str], recorded_fill_ids: list[str], stateful_fill_ids: list[str], recorder_seqs: list[int]) -> list[ReconciliationAnomaly]:
    out: list[ReconciliationAnomaly] = []
    if len(active_order_ids) != len(set(active_order_ids)):
        out.append(ReconciliationAnomaly("duplicate_active_orders", "high", None, "duplicate order ids in active state"))
    terminal_ids = set(recorded_fill_ids) | set(stateful_fill_ids)
    for oid in intended_order_ids:
        if oid not in active_order_ids and oid not in terminal_ids:
            out.append(ReconciliationAnomaly("missing_active_order", "high", None, oid))
    for oid in active_order_ids:
        if oid not in intended_order_ids:
            out.append(ReconciliationAnomaly("quote_state_mismatch", "medium", None, oid))
    for fid in stateful_fill_ids:
        if fid not in recorded_fill_ids:
            out.append(ReconciliationAnomaly("filled_not_recorded", "high", None, fid))
    for fid in recorded_fill_ids:
        if fid not in stateful_fill_ids:
            out.append(ReconciliationAnomaly("recorded_not_stateful_fill", "medium", None, fid))
    if recorder_seqs:
        expected = list(range(min(recorder_seqs), max(recorder_seqs) + 1))
        if recorder_seqs != expected:
            out.append(ReconciliationAnomaly("recorder_sequence_gap", "high", None, "seq gap"))
    return out
