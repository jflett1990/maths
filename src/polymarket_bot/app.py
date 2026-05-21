from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
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
from polymarket_bot.recorder.jsonl import JsonlRecorder, RecorderError
from polymarket_bot.risk.engine import allow_trade
from polymarket_bot.risk.pnl import pnl_for_fill
from polymarket_bot.risk.validation import validate_order
from polymarket_bot.oracles.base import NullOracle
from polymarket_bot.sentiment.inference import SentimentAnalyzer
from polymarket_bot.state.store import InMemoryStateStore
from polymarket_bot.signals.cross_market import build_constraints, evaluate_constraints
from polymarket_bot.signals.edge import evaluate_market
from polymarket_bot.signals.toxicity import toxicity_penalty
from polymarket_bot.signals.universe import rank_universe
from polymarket_bot.wallets.clustering import heuristic_clusters
from polymarket_bot.wallets.performance import attribute_wallet_performance
from polymarket_bot.wallets.scoring import score_wallet
from polymarket_bot.wallets.signals import wallet_signal_for_market


logger = logging.getLogger(__name__)


def _fingerprint_config(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def run_once(
    config_path: str,
    market_adapter: PolymarketRESTAdapter | None = None,
    wallet_adapter: WalletAdapter | None = None,
    broker: PaperBroker | None = None,
    recorder: JsonlRecorder | None = None,
    clock: callable | None = None,
) -> int:
    cfg = load_config(config_path)
    run_id = str(uuid.uuid4())
    circuit = CircuitState()
    now = clock or (lambda: int(time.time()))
    if market_adapter is None:
        fixture_payloads = {}
        fixture = Path("tests/fixtures/markets.json")
        if fixture.exists():
            fixture_payloads["/markets"] = json.loads(fixture.read_text())
        poly_headers = {}
        env_map = {
            "POLY_ADDRESS": cfg.adapters.poly_address_env,
            "POLY_API_KEY": cfg.adapters.poly_api_key_env,
            "POLY_PASSPHRASE": cfg.adapters.poly_passphrase_env,
            "POLY_SIGNATURE": cfg.adapters.poly_signature_env,
            "POLY_TIMESTAMP": cfg.adapters.poly_timestamp_env,
        }
        for header, env_name in env_map.items():
            v = os.getenv(env_name)
            if v:
                poly_headers[header] = v
        market_adapter = PolymarketRESTAdapter(
            base_url=cfg.adapters.clob_base_url,
            rate_limit_per_sec=cfg.adapters.rate_limit_per_sec,
            timeout_sec=cfg.adapters.timeout_sec,
            fixture_payloads=fixture_payloads,
            poly_headers=poly_headers,
        )
    wallet_ids = cfg.signals.wallet_universe or ["smart1"]
    if wallet_adapter is None:
        fixture_payloads = {f"/wallet-trades?wallet={wid}&limit=500": [] for wid in wallet_ids}
        wallet_adapter = WalletAdapter(rate_limit_per_sec=cfg.adapters.rate_limit_per_sec, timeout_sec=cfg.adapters.timeout_sec, fixture_payloads=fixture_payloads)
    broker = broker or PaperBroker()
    recorder = recorder or JsonlRecorder(cfg.recorder.output_dir, run_id=run_id, fsync=cfg.recorder.fsync, fail_on_error=cfg.recorder.fail_on_error)
    sentiment = SentimentAnalyzer()
    canonical_streams = [
        "market_snapshots",
        "wallet_observations",
        "signals",
        "decisions",
        "orders",
        "fills",
        "pnl",
        "run",
        "run_report",
        "reconciliation_anomalies",
    ]
    for stream in canonical_streams:
        Path(cfg.recorder.output_dir, f"{stream}.jsonl").touch(exist_ok=True)
    oracle = NullOracle()
    state_store = InMemoryStateStore()

    sigcfg = cfg.signals.wallet_intelligence
    perm_reasons: list[str] = []
    if sigcfg and sigcfg.enabled:
        rec = ExperimentRegistry(sigcfg.registry_path, Path(sigcfg.registry_path).with_name("registry_state.json").as_posix()).get(sigcfg.experiment_id)
        dataset_fp = fingerprint_files(sigcfg.dataset_paths)
        report_fp = fingerprint_files([sigcfg.validation_report_path]) if Path(sigcfg.validation_report_path).exists() else "missing"
        perm = resolve_signal_permission(cfg.mode, rec, dataset_fp, report_fp, requested_mode=sigcfg.requested_mode)
        if perm.fatal_errors and cfg.mode == "live":
            raise RuntimeError("live fail-closed signal governance")
        perm_reasons = perm.downgrade_reasons
    else:
        perm = resolve_signal_permission(cfg.mode, None, "", "")
        perm_reasons = ["signal_disabled_or_missing_mapping"]

    def safe_record(stream: str, payload: dict) -> bool:
        try:
            recorder.write(stream, payload)
            return True
        except Exception:
            logger.exception("Recorder failed on stream %s", stream)
            circuit.trip("cb_recorder_failure_stop")
            return False

    try:
        raw_markets = market_adapter.fetch_active_markets()
        wallet_trades = []
        for wid in wallet_ids:
            wallet_trades.extend(wallet_adapter.fetch_wallet_trades(wid))
    except AdapterError:
        circuit.trip("cb_adapter_error_stop")
        summary = {
            "top_smart_wallets_observed": [],
            "run_id": run_id,
            "mode": cfg.mode,
            "wallet_signal_permission": perm.effective_signal_mode,
            "wallet_signal_downgrade_reasons": perm_reasons,
            "reconciliation_anomalies": [],
            "circuit_breakers_triggered": circuit.reasons,
            "markets_rejected_by_reason": {"adapter_error": 1},
            "wallet_derived_opportunities": 0,
            "pnl_total": 0.0,
        }
        if cfg.mode == "live":
            raise RuntimeError("live fail-closed adapter error")
        safe_record("run_report", summary)
        Path(cfg.recorder.output_dir, "run_report.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    performance = attribute_wallet_performance(wallet_trades)
    scores = {performance.wallet_id: score_wallet(performance)} if performance.wallet_id else {}
    clusters = heuristic_clusters(wallet_trades)
    markets = rank_universe(raw_markets, cfg.max_markets_per_cycle)
    violations = evaluate_constraints(markets, build_constraints(markets))

    placed = 0
    run_notional = 0.0
    position_by_market: dict[str, float] = {}
    exposure_by_category: dict[str, float] = {}
    rejected: Counter[str] = Counter()
    decisions_ids: list[str] = []
    recorded_fill_ids: list[str] = []
    stateful_fill_ids: list[str] = []
    pnl_rows: list[PnLBreakdown] = []

    if cfg.kill_switch.global_enabled:
        circuit.trip("cb_global_kill_switch")

    sentiment_scores: dict[str, float] = {}
    if cfg.signals.sentiment.enabled and markets:
        async def _collect_sentiment() -> dict[str, float]:
            tasks = [sentiment.evaluate_market_context(m.market_id) for m in markets]
            vals = await asyncio.gather(*tasks, return_exceptions=True)
            out: dict[str, float] = {}
            for market, val in zip(markets, vals):
                if isinstance(val, Exception):
                    out[market.market_id] = 0.0
                else:
                    out[market.market_id] = float(val)
            return out

        sentiment_scores = asyncio.run(_collect_sentiment())

    for m in markets:
        if m.market_id in cfg.kill_switch.per_market_disabled:
            rejected["market_kill_switch"] += 1
            continue
        w_signal = wallet_signal_for_market(m.market_id, wallet_trades, scores)
        edge_contribution_enabled = bool(sigcfg and sigcfg.allow_edge_contribution)
        if not perm.allow_positive_alpha or not edge_contribution_enabled:
            w_signal.wallet_alpha_bps = 0.0
        else:
            w_signal.wallet_alpha_bps = min(w_signal.wallet_alpha_bps, perm.max_alpha_bps)
        if not perm.allow_risk_filter:
            w_signal.toxic_informed_flow_flag = False
            w_signal.smart_wallet_toxicity_adjustment = 0.0

        sentiment_score = sentiment_scores.get(m.market_id, 0.0)
        oracle_probability = oracle.get_probability(m.market_id) if cfg.oracles.enabled else None
        state_store.put(f"market:{m.market_id}", {"market_id": m.market_id, "sentiment": sentiment_score, "oracle_probability": oracle_probability})
        signal = evaluate_market(m, cfg, cross=violations.get(m.market_id), wallet_signal=w_signal, sentiment_score=sentiment_score, oracle_probability=oracle_probability)
        ok, reason = allow_trade(m, signal, cfg)
        if not safe_record("market_snapshots", {"ts": now(), "market_id": m.market_id, "bid": m.yes_price, "ask": m.no_price, "mid": (m.yes_price + m.no_price) / 2}) and cfg.recorder.fail_on_error:
            break
        if not safe_record("wallet_observations", {"ts": now(), "wallet_id": wallet_ids[0], "market_id": m.market_id, "price": m.yes_price, "size": cfg.execution.quote_size, "category": m.category, "liquidity": m.liquidity, "resolution_clarity": 1.0}) and cfg.recorder.fail_on_error:
            break
        safe_record("signals", {"market_id": m.market_id, "wallet_signal": asdict(w_signal)})
        if not ok:
            rejected[reason] += 1
            continue
        if "cb_global_kill_switch" in circuit.reasons:
            rejected["global_kill_switch"] += 1
            continue
        if cfg.mode in {"shadow", "live"}:
            rejected[f"{cfg.mode}_observe_only"] += 1
            continue
        d = Decision(m.market_id, "quote_passive", "yes", cfg.execution.quote_size, m.yes_price, "maker", signal)
        safe_record("decisions", asdict(d))
        if placed >= cfg.execution.max_orders_per_run:
            circuit.trip("cb_max_orders_per_run")
            rejected["max_orders_per_run"] += 1
            continue
        order_notional = d.price * d.size
        if run_notional + order_notional > cfg.execution.max_order_notional_per_run:
            circuit.trip("cb_max_order_notional_per_run")
            rejected["max_order_notional_per_run"] += 1
            continue
        next_position = position_by_market.get(m.market_id, 0.0) + d.size
        if abs(next_position) > cfg.risk.max_position_per_market:
            circuit.trip("cb_max_position_per_market")
            rejected["max_position_per_market"] += 1
            continue
        next_category = exposure_by_category.get(m.category, 0.0) + order_notional
        if next_category > cfg.risk.max_category_exposure:
            circuit.trip("cb_max_category_exposure")
            rejected["max_category_exposure"] += 1
            continue
        v = validate_order(d, m, signal, cfg)
        if not v.ok:
            rejected[v.reason or "order_validation_failed"] += 1
            continue
        oid = broker.place(d)
        safe_record("orders", {"order_id": oid, "market_id": d.market_id, "side": d.side, "price": d.price, "size": d.size})
        decisions_ids.append(oid)
        fill = broker.mark_fill(oid)
        if fill:
            stateful_fill_ids.append(fill.order_id)
            recorded_fill_ids.append(fill.order_id)
            safe_record("fills", asdict(fill))
            pnl = pnl_for_fill(fill, m.yes_price, signal, cfg.costs.fee_bps, cfg.costs.reward_bps_placeholder)
            pnl_rows.append(pnl)
            safe_record("pnl", asdict(pnl))
            placed += 1
            run_notional += order_notional
            position_by_market[m.market_id] = next_position
            exposure_by_category[m.category] = next_category

    active_ids = list(broker._orders.keys())  # noqa: SLF001
    seqs = list(range(1, recorder.seq + 1))
    recon = reconcile_state(decisions_ids, active_ids, decisions_ids, recorded_fill_ids, stateful_fill_ids, seqs)
    if any(a.severity == "high" for a in recon):
        circuit.trip("cb_reconciliation_high")
    safe_record("reconciliation_anomalies", {"items": [asdict(a) for a in recon]})

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
        "config_fingerprint": _fingerprint_config(config_path),
    }
    safe_record("run", {"placed": placed, "markets": len(markets)})
    safe_record("run_report", summary)
    Path(cfg.recorder.output_dir, "run_report.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    return placed
