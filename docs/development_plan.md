# Updated Development Plan

## Phase 0: Verification and stabilization

**Objective:**
Make the repo testable and prevent safety claims from being false.

**Why this phase comes now:**
Current integration tests depend on live network, and P0 safety behavior cannot be trusted until the app runner is hermetic.

**Tasks:**
- Refactor `run_once()` into an injectable runner: `run_once(config_path, market_adapter=None, wallet_adapter=None, broker=None, recorder=None, clock=None)` or introduce `AppRunner`.
- Add fixture-backed app integration tests with fake market and wallet adapters.
- Enforce global kill switch before any order placement.
- Enforce per-market kill switch before signal evaluation or before order validation.
- Make adapter errors trip `cb_adapter_error_stop` and produce a run report rather than crash blindly, except where fail-closed should raise in live mode.
- Make recorder errors trip `cb_recorder_failure_stop` when `fail_on_error` is true.

**Target files/modules:**
- `src/polymarket_bot/app.py`
- `src/polymarket_bot/core/safety.py`
- `src/polymarket_bot/risk/engine.py`
- `tests/integration/test_paper_run.py`
- `tests/integration/test_safety_breakers.py`
- `tests/integration/test_app_permission_report.py`

**Dependencies:** None.

**Risks:**
Refactor could accidentally weaken live fail-closed behavior. Add regression tests before extending behavior.

**Acceptance criteria:**
- Full test suite runs without live network.
- `kill_switch.global_enabled: true` produces `placed == 0`.
- Per-market disabled IDs produce no decisions/orders for that market.
- Run report includes breaker reasons and rejected counts.
- No test requires public internet.

**Tests to add/update:**
- `test_global_kill_switch_blocks_fixture_orders`
- `test_per_market_kill_switch_blocks_only_disabled_market`
- `test_adapter_error_trips_fail_closed_report`
- `test_run_once_uses_injected_adapters_no_network`

## Phase 1: Close recorder/replay/schema inconsistencies

**Objective:**
Create one canonical event contract for paper/shadow/replay.

**Why this phase comes now:**
Replay, validation, governance, and safety audits depend on trustworthy recorded state. Right now, the output streams are a bag of names, some documented and some actual.

**Tasks:**
- Define canonical stream schemas:
  - `market_snapshots.jsonl`
  - `wallet_observations.jsonl`
  - `signals.jsonl` (or keep `wallet_signals.jsonl` but update docs)
  - `decisions.jsonl`
  - `orders.jsonl`
  - `fills.jsonl`
  - `pnl.jsonl`
  - `run.jsonl`
  - `run_report.jsonl`
  - `reconciliation_anomalies.jsonl`
- Update `run_once()` to write actual `decisions.jsonl`, `orders.jsonl`, `pnl.jsonl`, and `run.jsonl`.
- Update `replay_compare()` to consume actual produced streams.
- Decide schema version. Current recorder writes `schema_version: 1`; fixtures use `schema_version: 2`. Pick one and migrate tests.
- Add monotonic clock injection to make replay deterministic.
- Use `recorder.flush_every` or remove it from config.

**Target files/modules:**
- `src/polymarket_bot/recorder/jsonl.py`
- `src/polymarket_bot/replay.py`
- `src/polymarket_bot/app.py`
- `docs/runbook_paper.md`
- `docs/replay_debugging.md`
- `tests/integration/test_replay.py`
- `tests/unit/test_replay_corruption.py`

**Dependencies:**
Phase 0 injection/clock support.

**Risks:**
Changing stream names can break validation scripts. Provide a compatibility layer or update all scripts in one PR.

**Acceptance criteria:**
- A paper fixture run that places fills replays with `mismatches == 0`.
- Replay fails on malformed JSONL unless `skip_malformed=True`.
- Docs match produced files exactly.
- Shadow required-stream test checks actual canonical streams.

**Tests to add/update:**
- `test_replay_matches_fixture_run_with_fills`
- `test_run_writes_decisions_orders_pnl_run_streams`
- `test_schema_versions_consistent_across_recorded_outputs`

## Phase 2: Finish core execution, order lifecycle, and risk paths

**Objective:**
Make paper mode a credible simulator rather than immediate-fill bookkeeping.

**Why this phase comes now:**
Execution realism and risk enforcement are prerequisites before wallet alpha, reward modeling, or live scaffolding means anything.

**Tasks:**
- Replace `QuoteOrder` with an `Order` model containing status: `created`, `open`, `partially_filled`, `filled`, `cancelled`, `expired`, `rejected`.
- Track completed fills separately from active orders so reconciliation stops flagging filled orders as missing active orders.
- Implement quote ladder generation using `execution.quote_levels`, `tick_size`, `quote_size`, `post_only`, and toxicity width/size adjustments.
- Implement stale quote cancellation using `execution.stale_quote_sec`.
- Enforce `execution.max_orders_per_run`.
- Enforce aggregate `execution.max_order_notional_per_run` as aggregate run notional, or rename it if intended scope is per order.
- Add portfolio/risk state: per-market position, event exposure, category exposure, daily realized/unrealized loss, drawdown.
- Enforce:
  - `risk.max_position_per_market`
  - `risk.max_event_exposure`
  - `risk.max_category_exposure`
  - `risk.max_daily_loss`
  - `risk.max_drawdown`
- Implement slippage/taker checks only if aggressive mode is introduced. Otherwise keep aggressive mode disabled and document it as unsupported.

**Target files/modules:**
- `src/polymarket_bot/execution/paper_broker.py`
- `src/polymarket_bot/core/models.py`
- `src/polymarket_bot/risk/engine.py`
- `src/polymarket_bot/risk/validation.py`
- `src/polymarket_bot/reconciliation.py`
- `src/polymarket_bot/app.py`
- `tests/unit/test_quote_lifecycle.py`
- `tests/unit/test_order_validation.py`
- `tests/unit/test_reconciliation.py`

**Dependencies:**
Phase 1 event schemas.

**Risks:**
If you overbuild execution, you’ll stall. Keep it paper-only and deterministic first. No live signing yet.

**Acceptance criteria:**
- Filled orders are not counted as missing active orders.
- Partial fills are represented correctly.
- Max order count breaker trips before placement.
- Aggregate notional breaker trips before placement.
- Position/event/category limits are enforced.
- Stale quotes are cancelled and recorded.
- Paper PnL rows are emitted for every fill.

**Tests to add/update:**
- `test_filled_order_not_missing_active_in_reconciliation`
- `test_max_orders_per_run_blocks_extra_orders`
- `test_aggregate_notional_limit_blocks_run`
- `test_stale_quotes_cancelled_and_recorded`
- `test_event_and_category_exposure_limits`

## Phase 3: Finish wallet intelligence and governance wiring

**Objective:**
Make wallet intelligence usable only in the modes justified by validation.

**Why this phase comes now:**
The repo already has the governance machinery, but runtime wiring is incomplete and config is not authoritative.

**Tasks:**
- Make `signals.wallet_intelligence.requested_mode` flow into `resolve_signal_permission()` and `guard_signal_runtime()`.
- Use runtime config to clamp requested mode to registry grant. Runtime must never exceed registry permission.
- Fix `guard_signal_runtime(config_requested_mode=...)` so it actually uses the requested mode.
- Make wallet IDs/configurable wallet universe part of config instead of hardcoded `"smart1"`.
- Remove the hardcoded empty wallet fixture from production app construction.
- Use wallet_validation config in validation scripts:
  - `train_frac`
  - `val_frac`
  - `min_samples`
  - `latency_scenarios_sec`
  - `baselines`
  - `leakage_strict`
- Normalize baseline names between config, reports, docs, and gate policy.
- Fix `scripts/register_validation_run.py` so it accepts YAML config directly (`--config configs/base.yaml`).
- Fix `scripts/expire_experiment.py` by appending an expiration/revocation event to the registry log instead of mutating state only.

**Target files/modules:**
- `src/polymarket_bot/core/config.py`
- `src/polymarket_bot/app.py`
- `src/polymarket_bot/governance/guard.py`
- `src/polymarket_bot/governance/permissions.py`
- `src/polymarket_bot/governance/registry.py`
- `src/polymarket_bot/wallets/validation/harness.py`
- `scripts/register_validation_run.py`
- `scripts/expire_experiment.py`
- `scripts/check_config_registry.py`
- `docs/signal_permission_matrix.md`
- `docs/experiment_registry_runbook.md`

**Dependencies:**
Phase 0 injection and Phase 1 recording.

**Risks:**
The temptation will be to allow wallet alpha too early. Keep default `observe_only`, then `risk_filter_only`, then `ranking`, then capped alpha only after recorded validation.

**Acceptance criteria:**
- Runtime wallet signal mode equals the minimum of config request and registry grant.
- Unregistered/expired/fingerprint-mismatched signals downgrade in paper/shadow and fail closed in live.
- `allow_edge_contribution: false` prevents positive alpha even if registry grants stronger mode.
- Wallet validation scripts use config values.
- Experiment expiration is durable through `ExperimentRegistry.get()`.

**Tests to add/update:**
- `test_runtime_requested_mode_clamped_to_registry_grant`
- `test_config_requested_mode_used_by_guard`
- `test_expire_experiment_appends_durable_event`
- `test_validation_harness_uses_config_min_samples_and_baselines`
- `test_wallet_universe_config_replaces_smart1_hardcode`

## Phase 4: Implement inferred feature hardening and observability

**Objective:**
Make shadow mode operationally useful and prepare for a future live-capable boundary without enabling live trading prematurely.

**Why this phase comes now:**
After schemas/risk/governance are coherent, shadow reporting and observability become useful instead of theatrical paperwork.

**Tasks:**
- Improve shadow daily report with fields from `docs/shadow_live_wallet_protocol.md`: markets observed, wallet events, top signals, ignored signals, improved/harmed trades, blocked bad trades, false positives, latency decay, baseline comparison, recommendation, anomalies.
- Record `resolved_outcomes.jsonl` through a controlled ingestion path, not manually.
- Add data-quality metrics to run report: missing quotes, crossed books, stale snapshots, unavailable copyable prices, insufficient forward observations.
- Add market staleness checks using `Market.last_update_ts` and `execution.stale_quote_sec`.
- Add reward config ingestion and conservative reward alpha tests.
- Add CI config (if this repo is meant to leave the sandbox): run unit tests, fixture integration tests, type check, lint, and no live network in CI.

**Target files/modules:**
- `scripts/run_shadow_wallet_daily.py`
- `src/polymarket_bot/wallets/validation/recorded_dataset.py`
- `src/polymarket_bot/app.py`
- `src/polymarket_bot/adapters/polymarket.py`
- `src/polymarket_bot/signals/edge.py`
- `src/polymarket_bot/risk/engine.py`
- `docs/shadow_live_wallet_protocol.md`
- `docs/live_readiness_checklist.md`

**Dependencies:**
Phases 1–3.

**Risks:**
Reward alpha can create fake edge if modeled too generously. Keep it capped, haircutted, and disabled unless verified.

**Acceptance criteria:**
- Shadow daily report fields match protocol.
- Data quality gates can downgrade wallet signal permission.
- Stale market data trips a breaker.
- Reward alpha is only included when reward data is present and conservative assumptions pass validation.
- CI runs without network.

**Tests to add/update:**
- `test_shadow_daily_report_protocol_fields`
- `test_stale_market_snapshot_trips_breaker`
- `test_reward_alpha_requires_reward_config`
- `test_data_quality_downgrades_signal_permission`
