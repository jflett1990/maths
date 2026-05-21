from __future__ import annotations

import time
from polymarket_bot.core.models import Decision, Fill, Order


class PaperBroker:
    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._completed: dict[str, Order] = {}
        self._counter = 0

    def place(self, decision: Decision, gtd_sec: int = 60) -> str:
        self._counter += 1
        oid = f"paper-{self._counter}"
        now = int(time.time())
        self._orders[oid] = Order(oid, decision.market_id, decision.side, decision.price, decision.size, now, now + gtd_sec, status="open")
        return oid

    def reconcile_market(self, market_id: str, now_ts: int) -> list[str]:
        cancelled: list[str] = []
        for oid, o in list(self._orders.items()):
            if o.market_id == market_id and o.expires_ts <= now_ts:
                o.status = "expired"
                self._completed[oid] = o
                cancelled.append(oid)
                self._orders.pop(oid)
        return cancelled

    def replace_quotes(self, market_id: str, decisions: list[Decision], gtd_sec: int = 60) -> list[str]:
        for oid, o in list(self._orders.items()):
            if o.market_id == market_id:
                self._orders.pop(oid)
        return [self.place(d, gtd_sec=gtd_sec) for d in decisions]

    def cancel(self, order_id: str) -> bool:
        order = self._orders.pop(order_id, None)
        if order is None:
            return False
        order.status = "cancelled"
        self._completed[order_id] = order
        return True

    def cancel_all(self) -> int:
        n = len(self._orders)
        self._orders = {}
        return n

    def mark_fill(self, order_id: str, ts: int | None = None) -> Fill | None:
        order = self._orders.pop(order_id, None)
        if not order:
            return None
        order.status = "filled"
        order.filled_size = order.size
        self._completed[order_id] = order
        return Fill(order_id, order.market_id, "buy" if order.side == "yes" else "sell", order.price, order.size, ts or int(time.time()))
