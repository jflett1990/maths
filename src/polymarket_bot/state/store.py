from __future__ import annotations

import json
from abc import ABC, abstractmethod


class StateStore(ABC):
    @abstractmethod
    def put(self, key: str, value: dict) -> None:
        raise NotImplementedError


class InMemoryStateStore(StateStore):
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}

    def put(self, key: str, value: dict) -> None:
        self.items[key] = value


class RedisStateStore(StateStore):
    """
    Redis-backed state store with lazy import so Redis dependency is optional.
    """

    def __init__(self, url: str) -> None:
        import redis

        self._client = redis.Redis.from_url(url, decode_responses=True)

    def put(self, key: str, value: dict) -> None:
        self._client.set(key, json.dumps(value, sort_keys=True))
