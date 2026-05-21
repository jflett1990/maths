from __future__ import annotations

from abc import ABC, abstractmethod


class Oracle(ABC):
    @abstractmethod
    def get_probability(self, market_id: str) -> float | None:
        raise NotImplementedError


class NullOracle(Oracle):
    def get_probability(self, market_id: str) -> float | None:
        _ = market_id
        return None
