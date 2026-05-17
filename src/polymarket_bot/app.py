from __future__ import annotations

import hashlib
import json
import time
import uuid
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from polymarket_bot.adapters.polymarket import AdapterError, PolymarketRESTAdapter
from polymarket_bot.adapters.wallets import WalletAdapter
from polymarket_bot.core.config import load_config
from polymarket_bot.core.models import Decision, PnLBreakdown
from polymarket_bot.core.safety import CircuitState
from polymarket_bot.execution.paper_broker import PaperBroker
from polymarket_bot.governance.fingerprints import fingerprint_files
from polymarket_bot.governance.permissions import resolve_signal_permission
from polymarket_bot.governance.registry import ExperimentRegistry
from polymarket_bot.reconciliation import reconcile_state
from polymarket_bot.recorder.jsonl import JsonlRecorder
from polymarket_bot.risk.engine import allow_trade
from polymarket_bot.risk.pnl import pnl_for_fill
from polymarket_bot.risk.validation import validate_order
from polymarket_bot.signals.cross_market import build_constraints, evaluate_constraints
from polymarket_bot.signals.edge import evaluate_market
from polymarket_bot.signals.toxicity import toxicity_penalty
from polymarket_bot.signals.universe import rank_universe
from polymarket_bot.wallets.clustering import heuristic_clusters
from polymarket_bot.wallets.performance import attribute_wallet_performance
from polymarket_bot.wallets.scoring import score_wallet
from polymarket_bot.wallets.signals import wallet_signal_for_market


def _fingerprint_config(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def run_once(config_path: str) -> int:
    cfg = load_config(config_path)
    run_id = str(uuid.uuid4())
    circuit = CircuitState()
    adapter = PolymarketRESTAdapter(rate_limit_per_sec=cfg.adapters.rate_limit_per_sec, timeout_sec=cfg.adapters.timeout_sec)
    wallet_adapter = WalletAdapter(rate_limit_per_sec=cfg.adapters.rate_limit_per_sec, timeout_sec=cfg.adapters.timeout_sec, fixture_payloads={"/wallet-trades?wallet=smart1&limit=500": []})
    broker = PaperBroker()
    recorder = JsonlRecorder(cfg.recorder.output_dir, run_id=run_id, fsync=cfg.recorder.fsync, fail_on_error=cfg.recorder.fail_on_error)

    sigcfg = cfg.signals.wallet_intelligence
    perm_reasons: list[str] = []
    if sigcfg and sigcfg.enabled:
        rec = ExperimentRegistry(sigcfg.registry_path, Path(sigcfg.registry_path).with_name("registry_state.json").as_posix()).get(sigcfg.experiment_id)
        dataset_fp = fingerprint_files(sigcfg.dataset_paths)
        report_fp = fingerprint_files([sigcfg.validation_report_path]) if Path(sigcfg.validation_report_path).exists() else "missing"
        perm = resolve_signal_permission(cfg.mode, rec, dataset_fp, report_fp)
        if perm.fatal_errors and cfg.mode == "live":
            raise RuntimeError("live fail-closed signal governance")
        perm_reasons = perm.downgrade_reasons
    else:
        perm = resolve_signal_permission(cfg.mode, None, "", "")
        perm_reasons = ["signal_disabled_or_missing_mapping"]

    raw_markets = adapter.fetch_active_markets()
    wallet_trades = wallet_adapter.fetch_wallet_trades("smart1")
    scores = {p.wallet_id: score_wallet(p) for p in [attribute_wallet_performance(wallet_trades)] if p.wallet_id}
    clusters = heuristic_clusters(wallet_trades)
    markets = rank_universe(raw_markets, cfg.max_markets_per_cycle)
    violations = evaluate_constraints(markets, build_constraints(markets))

    placed = 0
    rejected: Counter[str] = Counter()
    decisions_ids: list[str] = []
    recorded_fill_ids: list[str] = []
    stateful_fill_ids: list[str] = []
    pnl_rows: list[PnLBreakdown] = []

    if cfg.kill_switch.global_enabled:
        circuit.trip("cb_global_kill_switch")
    for m in markets:
        w_signal = wallet_signal_for_market(m.market_id, wallet_trades, scores)
        if not perm.allow_positive_alpha:
            w_signal.wallet_alpha_bps = 0.0
        else:
            w_signal.wallet_alpha_bps = min(w_signal.wallet_alpha_bps, perm.max_alpha_bps)
        if not perm.allow_risk_filter:
            w_signal.toxic_informed_flow_flag = False
            w_signal.smart_wallet_toxicity_adjustment = 0.0

        signal = evaluate_market(m, cfg, cross=violations.get(m.market_id), wallet_signal=w_signal)
        ok, reason = allow_trade(m, signal, cfg)
        recorder.write("market_snapshots", {"ts": int(time.time()), "market_id": m.market_id, "bid": m.yes_price, "ask": m.no_price, "mid": (m.yes_price + m.no_price) / 2})
        recorder.write("wallet_observations", {"ts": int(time.time()), "wallet_id": "smart1", "market_id": m.market_id, "price": m.yes_price, "size": cfg.execution.quote_size, "category": m.category, "liquidity": m.liquidity, "resolution_clarity": 1.0})
        recorder.write("wallet_signals", {"market_id": m.market_id, "wallet_signal": asdict(w_signal)})
        recorder.write("decision_context", {"market_id": m.market_id, "gate": reason, "would_place": ok and cfg.mode == "paper"})
        if not ok:
            rejected[reason] += 1
            continue
        if cfg.mode in {"shadow", "live"}:
            rejected[f"{cfg.mode}_observe_only"] += 1
            continue
        d = Decision(m.market_id, "quote_passive", "yes", cfg.execution.quote_size, m.yes_price, "maker", signal)
        if not validate_order(d, m, signal, cfg).ok:
            continue
        oid = broker.place(d)
        decisions_ids.append(oid)
        fill = broker.mark_fill(oid)
        if fill:
            stateful_fill_ids.append(fill.order_id)
            recorded_fill_ids.append(fill.order_id)
            recorder.write("fills", asdict(fill))
            pnl = pnl_for_fill(fill, m.yes_price, signal, cfg.costs.fee_bps, cfg.costs.reward_bps_placeholder)
            pnl_rows.append(pnl)
            placed += 1

    active_ids = list(broker._orders.keys())  # noqa: SLF001
    seqs = list(range(1, recorder.seq + 1))
    recon = reconcile_state(decisions_ids, active_ids, decisions_ids, recorded_fill_ids, stateful_fill_ids, seqs)
    if any(a.severity == "high" for a in recon):
        circuit.trip("cb_reconciliation_high")
    recorder.write("reconciliation_anomalies", {"items": [asdict(a) for a in recon]})
    recorder.write("wallet_scores", {"scores": [asdict(s) for s in scores.values()]})
    recorder.write("wallet_clusters", {"clusters": [asdict(c) for c in clusters]})
    recorder.write("signal_permissions", {"effective_mode": perm.effective_signal_mode, "downgrade_reasons": perm_reasons})

    summary = {
        "top_smart_wallets_observed": [asdict(s) for s in sorted(scores.values(), key=lambda x: x.score, reverse=True)[:3]],
        "run_id": run_id,
        "mode": cfg.mode,
        "wallet_signal_permission": perm.effective_signal_mode,
        "wallet_signal_downgrade_reasons": perm_reasons,
        "reconciliation_anomalies": [asdict(a) for a in recon],
        "circuit_breakers_triggered": circuit.reasons,
        "markets_rejected_by_reason": dict(rejected),
        "wallet_derived_opportunities": sum(1 for _m in markets),
        "pnl_total": sum(p.total for p in pnl_rows),
    }
    recorder.write("run_metadata", {"config_fingerprint": _fingerprint_config(config_path)})
    recorder.write("run_report", summary)
    Path(cfg.recorder.output_dir, "run_report.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    return placed
