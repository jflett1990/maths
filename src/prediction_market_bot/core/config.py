from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class PlatformConfig(BaseModel):
    name: str = "kalshi"
    mode: str = "paper"
    adapter: str = "kalshi"
    base_url: str = "https://demo-api.kalshi.co/trade-api/v2"
    enable_live_orders: bool = False
    allow_order_placement: bool = False
    allow_order_cancel: bool = False


class ExecutionConfig(BaseModel):
    quote_size: float = 10.0
    max_orders_per_run: int = 100


class RecorderConfig(BaseModel):
    output_dir: str = "state/recorded"


class RiskConfig(BaseModel):
    min_liquidity: float = 0.0
    max_spread_for_aggressive_bps: float = 1000.0


class AppConfig(BaseModel):
    mode: str = "paper"
    max_markets_per_cycle: int = 20
    min_expected_edge_bps: float = 0.0
    platform: PlatformConfig = PlatformConfig()
    execution: ExecutionConfig = ExecutionConfig()
    recorder: RecorderConfig = RecorderConfig()
    risk: RiskConfig = RiskConfig()
    signals: dict = Field(default_factory=dict)


def load_config(path: str) -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text())
    if "platform" in raw:
        return AppConfig.model_validate(raw)
    # compatibility: map old schema into new
    raw = dict(raw)
    raw["platform"] = {
        "name": "kalshi",
        "mode": raw.get("mode", "paper"),
        "adapter": "kalshi",
        "base_url": raw.get("adapters", {}).get("clob_base_url", "https://demo-api.kalshi.co/trade-api/v2"),
        "enable_live_orders": raw.get("mode_controls", {}).get("allow_live_orders", False),
        "allow_order_placement": False,
        "allow_order_cancel": False,
    }
    return AppConfig.model_validate(raw)
