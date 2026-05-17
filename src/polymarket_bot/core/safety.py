from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CircuitState:
    halted_global: bool = False
    halted_markets: set[str] = field(default_factory=set)
    reasons: list[str] = field(default_factory=list)

    def trip(self, reason: str, market_id: str | None = None) -> None:
        self.reasons.append(reason)
        if market_id:
            self.halted_markets.add(market_id)
        else:
            self.halted_global = True
