from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator


class RiskConfig(BaseModel):
    max_position_per_market: float
    max_event_exposure: float
    max_category_exposure: float
    max_daily_loss: float
    max_drawdown: float
    min_liquidity: float
    max_spread_for_aggressive_bps: float
    resolution_risk_max: float
    toxicity_max: float


class ExecutionConfig(BaseModel):
    mode: str
    tick_size: float
    quote_levels: int
    quote_size: float
    post_only: bool
    stale_quote_sec: int
    slippage_bps_limit: float
    gtd_minutes_before_catalyst: int
    max_orders_per_run: int = 100
    max_order_notional_per_run: float = 50000


class PenaltyConfig(BaseModel):
    uncertainty_haircut: float = Field(ge=0, le=1)
    reward_haircut: float = Field(ge=0, le=1)
    toxicity_scale: float
    resolution_scale: float


class RecorderConfig(BaseModel):
    output_dir: str
    flush_every: int
    fsync: bool = False
    fail_on_error: bool = True


class AdapterConfig(BaseModel):
    clob_base_url: str = "https://clob.polymarket.com"
    rate_limit_per_sec: float = 5.0
    timeout_sec: float = 5.0
    retries: int = 3
    poly_address_env: str = "POLY_ADDRESS"
    poly_api_key_env: str = "POLY_API_KEY"
    poly_passphrase_env: str = "POLY_PASSPHRASE"
    poly_signature_env: str = "POLY_SIGNATURE"
    poly_timestamp_env: str = "POLY_TIMESTAMP"


class CostConfig(BaseModel):
    fee_bps: float = 0.0
    reward_bps_placeholder: float = 0.0


class ModeConfig(BaseModel):
    allow_live_orders: bool = False
    live_confirmation: str | None = None
    require_kill_switch_armed: bool = True
    shadow_observe_only: bool = True


class KillSwitchConfig(BaseModel):
    global_enabled: bool = False
    per_market_disabled: list[str] = Field(default_factory=list)


class ReplayConfig(BaseModel):
    skip_malformed_lines: bool = False


class WalletValidationConfig(BaseModel):
    train_frac: float = 0.6
    val_frac: float = 0.2
    min_samples: int = 10
    latency_scenarios_sec: list[int] = Field(default_factory=lambda: [0, 30, 120, 600])
    baselines: list[str] = Field(default_factory=lambda: ["random_wallet", "top_pnl_wallet", "top_roi_wallet", "market_prior_only", "category_only", "momentum", "no_wallet_signal"])
    leakage_strict: bool = True
    report_json_path: str = "state/wallet_validation_report.json"
    report_md_path: str = "state/wallet_validation_report.md"


class SignalGovernanceConfig(BaseModel):
    enabled: bool = True
    signal_name: str
    signal_version: str
    experiment_id: str
    requested_mode: str
    registry_path: str
    validation_report_path: str
    dataset_paths: list[str]
    allow_edge_contribution: bool = False


class SentimentConfig(BaseModel):
    enabled: bool = False


class EdgeWeightConfig(BaseModel):
    orderbook: float = 1.0
    sentiment: float = 0.0
    oracle_divergence: float = 0.0


class SignalsConfig(BaseModel):
    wallet_intelligence: SignalGovernanceConfig | None = None
    sentiment: SentimentConfig = SentimentConfig()
    wallet_universe: list[str] = Field(default_factory=lambda: ["smart1"])


class OraclesConfig(BaseModel):
    enabled: bool = False



class AppConfig(BaseModel):
    mode: str
    poll_interval_sec: int
    min_expected_edge_bps: float
    max_markets_per_cycle: int
    risk: RiskConfig
    execution: ExecutionConfig
    penalties: PenaltyConfig
    recorder: RecorderConfig
    adapters: AdapterConfig = AdapterConfig()
    costs: CostConfig = CostConfig()
    mode_controls: ModeConfig = ModeConfig()
    kill_switch: KillSwitchConfig = KillSwitchConfig()
    replay: ReplayConfig = ReplayConfig()
    wallet_validation: WalletValidationConfig = WalletValidationConfig()
    signals: SignalsConfig = SignalsConfig()
    oracles: OraclesConfig = OraclesConfig()
    edge_weights: EdgeWeightConfig = EdgeWeightConfig()

    @model_validator(mode="after")
    def validate_safety(self) -> "AppConfig":
        if self.mode not in {"paper", "shadow", "live"}:
            raise ValueError("mode must be paper|shadow|live")
        if self.mode == "live":
            if not self.mode_controls.allow_live_orders:
                raise ValueError("live mode requires allow_live_orders=true")
            if self.mode_controls.live_confirmation != "I_ACKNOWLEDGE_LIVE_TRADING":
                raise ValueError("live mode requires explicit live_confirmation")
            if self.mode_controls.require_kill_switch_armed and not self.kill_switch.global_enabled:
                raise ValueError("live mode requires global kill switch armed")
        sig = self.signals.wallet_intelligence
        if sig and sig.enabled and self.mode == "live":
            if not sig.registry_path:
                raise ValueError("live mode requires wallet signal registry path")
            if not sig.validation_report_path or not sig.dataset_paths or not sig.experiment_id:
                raise ValueError("live mode requires complete wallet governance mapping")
        return self


def load_config(path: str) -> AppConfig:
    data = yaml.safe_load(Path(path).read_text())
    return AppConfig.model_validate(data)
