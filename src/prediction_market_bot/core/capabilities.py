from __future__ import annotations

from prediction_market_bot.adapters.base import AdapterCapabilities


def require_capability(capabilities: AdapterCapabilities, capability_name: str) -> None:
    if not hasattr(capabilities, capability_name):
        raise ValueError(f"Unknown capability: {capability_name}")
    if not getattr(capabilities, capability_name):
        raise RuntimeError(f"Capability not supported: {capability_name}")
