"""L12 broker/fix_adapter - FIX 4.4 protocol execution adapter (stdlib only).

Real FIX session over TCP: Logon (35=A), NewOrderSingle (35=D), ExecutionReport
(35=8) parsing, Heartbeat (35=0), TestRequest (35=1), orderly Logout (35=5).
Message builder/parser are complete; connect() requires host/port and
sender/target comp IDs from account config or DAVID_SLING_FIX_* env.
"""
from __future__ import annotations

import os
import socket
import time

from david_sling.broker.adapter import BrokerAdapter
from david_sling.core.errors import ExecutionError, SecurityError
from david_sling.core.schemas import (
    ExecutionReport,
    OrderIntent,
    OrderSide,
    OrderType,
    PositionState,
    SymbolSpec,
)
from david_sling.core.utils import new_id, utc_now

SOH = "\x01"


def _checksum(msg_body: str) -> str:
    return f"{sum(msg_body.encode()) % 256:03d}"


def build_message(msg_type: str, fields: dict[int, str], seq: int, sender: str, target: str) -> bytes:
    """Build a complete FIX message: 8/9/35/.../10=checksum."""
    body_fields = f"35={msg_type}{SOH}49={sender}{SOH}56={target}{SOH}34={seq}{SOH}52={_utc_stamp()}{SOH}"
    for tag in sorted(fields):
        body_fields += f"{tag}={fields[tag]}{SOH}"
    header = f"8=FIX.4.4{SOH}9={len(body_fields)}{SOH}"
    return (header + body_fields + f"10={_checksum(header + body_fields)}{SOH}").encode()


def _utc_stamp() -> str:
    t = time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())
    return t + ".000"


def parse_message(raw: bytes) -> dict[int, str]:
    """Parse a FIX message into {tag: value}; validates the 10= checksum."""
    text = raw.decode(errors="replace")
    parts = [p for p in text.split(SOH) if p]
    fields: dict[int, str] = {}
    for p in parts:
        if "=" in p:
            tag, _, val = p.partition("=")
            if tag.isdigit():
                fields[int(tag)] = val
    if 10 in fields:
        body = text.split("10=")[0]
        if _checksum(body) != fields[10]:
            raise ExecutionError("FIX checksum mismatch - message rejected")
    return fields


class FixAdapter(BrokerAdapter):
    def __init__(self, specs: dict[str, SymbolSpec], account_cfg: dict) -> None:
        self.specs = specs
        self.cfg = account_cfg
        self._sock: socket.socket | None = None
        self._seq = 1
        self._positions: dict[str, PositionState] = {}
        self._reports: list[ExecutionReport] = []
        self._last_exec: dict[int, str] = {}

    def connect(self) -> None:
        host = self.cfg.get("host") or os.environ.get("DAVID_SLING_FIX_HOST", "")
        port = int(self.cfg.get("port") or os.environ.get("DAVID_SLING_FIX_PORT", "0"))
        self.sender = self.cfg.get("sender_comp_id") or os.environ.get("DAVID_SLING_FIX_SENDER", "")
        self.target = self.cfg.get("target_comp_id") or os.environ.get("DAVID_SLING_FIX_TARGET", "")
        if not (host and port and self.sender and self.target):
            raise SecurityError("FIX adapter requires host/port/sender_comp_id/target_comp_id "
                                "(config or DAVID_SLING_FIX_* env)")
        self._sock = socket.create_connection((host, port), timeout=10.0)
        sock = self._sock
        logon = build_message("A", {98: "0", 108: "30", 141: "Y", 553: self.cfg.get("username", ""),
                                     554: self.cfg.get("password", "")}, self._seq, self.sender, self.target)
        self._seq += 1
        sock.sendall(logon)
        resp = parse_message(self._recv())
        if resp.get(35) != "A":
            raise ExecutionError(f"FIX logon rejected: {resp}")

    def disconnect(self) -> None:
        sock = self._sock
        if sock is not None:
            try:
                sock.sendall(build_message("5", {}, self._seq, self.sender, self.target))
            finally:
                sock.close()
                self._sock = None

    def _recv(self) -> bytes:
        data = self._require().recv(65536)
        if not data:
            raise ExecutionError("FIX connection closed by counterparty")
        return data

    def _require(self) -> socket.socket:
        if self._sock is None:
            raise ExecutionError("FIX adapter not connected - call connect() first")
        return self._sock

    def submit(self, intent: OrderIntent) -> ExecutionReport:
        sock = self._require()
        # 35=D NewOrderSingle: 11=ClOrdID 21=1 55=symbol 54=side 38=volume 40=ordertype 44=price 60=time
        side = "1" if intent.side == OrderSide.BUY else "2"
        otype = {OrderType.MARKET: "1", OrderType.LIMIT: "2", OrderType.STOP: "3"}.get(intent.order_type, "1")
        fields = {11: intent.intent_id, 21: "1", 55: intent.symbol, 54: side, 38: f"{intent.volume:.8f}",
                  40: otype, 60: _utc_stamp()}
        if intent.price is not None:
            fields[44] = f"{intent.price:.8f}"
        if intent.stop_loss is not None:
            fields[58] = f"SL={intent.stop_loss:.8f}"
        sock.sendall(build_message("D", fields, self._seq, self.sender, self.target))  # type: ignore[union-attr]
        self._seq += 1
        # wait for ExecutionReport (35=8) with this ClOrdID
        deadline = time.time() + 10.0
        while time.time() < deadline:
            f = parse_message(self._recv())
            if f.get(35) == "8" and f.get(11) == intent.intent_id:
                exec_type = f.get(150, "0")
                if exec_type not in ("2", "F"):  # 2=Fill, F=Trade
                    raise ExecutionError(f"FIX order not filled: ExecType={exec_type} {f.get(58, '')}")
                fill = float(f.get(31, f.get(44, "0")))
                pos = PositionState(position_id=new_id("pos"), symbol=intent.symbol, side=intent.side,
                                    volume=float(f.get(38, intent.volume)), entry_price=fill, open_ts=utc_now())
                self._positions[pos.position_id] = pos
                rep = ExecutionReport(intent_id=intent.intent_id, status="FILLED", fill_price=fill,
                                      volume=pos.volume, position_id=pos.position_id, ts=utc_now())
                self._reports.append(rep)
                return rep
            if f.get(35) == "1":
                sock.sendall(build_message("0", {}, self._seq, self.sender, self.target))  # type: ignore[union-attr]
                self._seq += 1
        raise ExecutionError(f"FIX no ExecutionReport for {intent.intent_id} within 10s")

    def close(self, position_id: str, volume: float | None = None) -> tuple[PositionState, float, float]:
        sock = self._require()
        pos = self._positions.get(position_id)
        if pos is None:
            raise ExecutionError(f"position {position_id} not found")
        # 35=F OrderCancelReplace is overkill; use a market close order (35=D opposite side)
        side = "2" if pos.side == OrderSide.BUY else "1"
        clord = new_id("cls")
        sock.sendall(build_message("D", {11: clord, 21: "1", 55: pos.symbol, 54: side,
                                               38: f"{volume or pos.volume:.8f}", 40: "1", 60: _utc_stamp()},
                                         self._seq, self.sender, self.target))  # type: ignore[union-attr]
        self._seq += 1
        f = parse_message(self._recv())
        if f.get(35) != "8":
            raise ExecutionError(f"FIX close rejected: {f}")
        pnl = float(f.get(6, "0"))  # 6=AvgPx PnL tag on trade confirms
        del self._positions[position_id]
        return pos, pnl, 0.0

    def modify(self, position_id: str, *, sl: float | None = None, tp: float | None = None) -> PositionState:
        sock = self._require()
        pos = self._positions[position_id]
        # 35=G OrderCancelReplaceRequest with new SL/TP (tags 1=ClOrdID 41=OrigClOrdID 38 55 54 40 44 58)
        clord = new_id("mod")
        fields = {11: clord, 41: pos.position_id, 55: pos.symbol, 54: "1" if pos.side == OrderSide.BUY else "2",
                  38: f"{pos.volume:.8f}", 40: "1", 60: _utc_stamp()}
        if sl is not None:
            fields[58] = f"SL={sl:.8f}"
        if tp is not None:
            fields[58] = (fields.get(58, "") + f" TP={tp:.8f}").strip()
        sock.sendall(build_message("G", fields, self._seq, self.sender, self.target))  # type: ignore[union-attr]
        self._seq += 1
        f = parse_message(self._recv())
        if f.get(35) != "9":
            raise ExecutionError(f"FIX modify rejected: {f}")
        if sl is not None:
            pos.stop_loss = sl
        if tp is not None:
            pos.take_profit = tp
        return pos

    def set_price(self, symbol: str, price: float) -> None:
        return None

    def account_snapshot(self, floating_pnl: float) -> dict:
        self._require()
        return {"balance": 0.0, "equity": floating_pnl, "margin": 0.0, "free_margin": 0.0,
                "margin_level_pct": 0.0, "currency": "USD", "leverage": 1.0, "floating_pnl": floating_pnl,
                "note": "FIX adapter: balances come from counterparty reports (35=8/9), not snapshots"}

    def reconcile(self) -> dict:
        return {"positions": len(self._positions), "reports": len(self._reports), "connected": self._sock is not None}
