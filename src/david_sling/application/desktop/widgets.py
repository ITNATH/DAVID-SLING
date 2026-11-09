"""L14 application/desktop/widgets - custom painted widgets for the command center.

GlobeWidget     : 3D liquidity globe (orthographic projection) with drag-rotate,
                  wheel-zoom transitions globe -> 2D heatmap -> order-routing corridors.
EquityWidget    : capital deployment equity curve.
DepthWidget     : liquidity pool depth ladder (SIMULATED, labelled in paint).
BarsWidget      : 9-layer fusion conviction bars.
All painting is QPainter on QWidget - hardware-accelerated, 60+ FPS via QTimer.
"""
from __future__ import annotations

import math
import random

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


def _c(hexs: str) -> QColor:
    return QColor(hexs)


class GlobeWidget(QWidget):
    """Interactive global liquidity core: globe / heatmap / routes modes."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("globe")
        self.setMinimumHeight(240)
        self.mode = "globe"
        self.rot_y = 0.6
        self.rot_x = -0.35
        self.zoom = 1.0
        self._dragging = False
        self._last = None
        self.symbols: list[str] = []
        self.fusion: dict[str, dict] = {}
        self.signals: list[dict] = []
        self._t = 0.0
        self._rng = random.Random(7)
        n = 170
        self._nodes = []
        for i in range(n):  # fibonacci sphere
            y = 1 - (i / (n - 1)) * 2
            r = math.sqrt(max(0.0, 1 - y * y))
            th = i * 2.399963
            self._nodes.append((r * math.cos(th), y, r * math.sin(th)))
        self._arcs = [(self._rng.randrange(n), self._rng.randrange(n), self._rng.random()) for _ in range(26)]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)  # ~60 FPS

    def set_market(self, symbols: list[str], fusion: dict[str, dict], signals: list[dict]) -> None:
        self.symbols = symbols
        self.fusion = fusion
        self.signals = signals
        self.update()

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.zoom = {"globe": 1.0, "heatmap": 1.9, "routes": 2.8}[mode]
        self.update()

    def _tick(self) -> None:
        self._t += 0.016
        if not self._dragging and self.mode == "globe":
            self.rot_y += 0.0022
        self.update()

    def mousePressEvent(self, e) -> None:  # noqa: N802
        self._dragging = True
        self._last = e.position()

    def mouseMoveEvent(self, e) -> None:  # noqa: N802
        if self._dragging and self._last is not None:
            d = e.position() - self._last
            self.rot_y += d.x() * 0.008
            self.rot_x = max(-1.4, min(1.4, self.rot_x + d.y() * 0.008))
            self._last = e.position()
            self.update()

    def mouseReleaseEvent(self, e) -> None:  # noqa: N802
        self._dragging = False

    def wheelEvent(self, e) -> None:  # noqa: N802
        self.zoom = max(0.6, min(3.2, self.zoom * (1.12 if e.angleDelta().y() > 0 else 0.89)))
        self.set_mode("routes" if self.zoom > 2.4 else "heatmap" if self.zoom > 1.5 else "globe")

    def _project(self, p: tuple[float, float, float], R: float, cx: float, cy: float) -> tuple[float, float, float]:
        x, y, z = p
        cy1, sy1 = math.cos(self.rot_y), math.sin(self.rot_y)
        cx1, sx1 = math.cos(self.rot_x), math.sin(self.rot_x)
        X = x * cy1 + z * sy1
        Z = -x * sy1 + z * cy1
        Y2 = y * cx1 - Z * sx1
        Z2 = y * sx1 + Z * cx1
        return cx + X * R, cy - Y2 * R, Z2

    def paintEvent(self, e) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        accent = _c("#00F0FF")
        dim = QColor("#7A8090")
        if self.mode == "globe":
            self._paint_globe(p, w, h, accent, dim)
        elif self.mode == "heatmap":
            self._paint_heatmap(p, w, h)
        else:
            self._paint_routes(p, w, h, accent)
        p.end()

    def _paint_globe(self, p: QPainter, w: int, h: int, accent: QColor, dim: QColor) -> None:
        R = min(w, h) * 0.36 * self.zoom
        cx, cy = w / 2, h / 2
        pen = QPen(dim)
        pen.setWidth(1)
        p.setPen(pen)
        for lat in range(-60, 61, 30):
            p.drawPolyline([QPointF(*self._project((
                math.cos(math.radians(lat)) * math.cos(math.radians(lon)),
                math.sin(math.radians(lat)),
                math.cos(math.radians(lat)) * math.sin(math.radians(lon))), R, cx, cy)[:2])
                for lon in range(0, 361, 12)])
        for lon in range(0, 180, 30):
            p.drawPolyline([QPointF(*self._project((
                math.cos(math.radians(lat)) * math.cos(math.radians(lon)),
                math.sin(math.radians(lat)),
                math.cos(math.radians(lat)) * math.sin(math.radians(lon))), R, cx, cy)[:2])
                for lat in range(-90, 91, 12)])
        pen.setColor(QColor(accent))
        p.setPen(pen)
        for a, b, ph in self._arcs:
            A, B = self._nodes[a], self._nodes[b]
            pts = []
            for s in range(21):
                u = s / 20
                pu = 1 - u
                mid = ((pu * pu * A[0] + 2 * pu * u * (A[0] + B[0]) / 2 + u * u * B[0]) * 1.25,
                       (pu * pu * A[1] + 2 * pu * u * (A[1] + B[1]) / 2 + u * u * B[1]) * 1.25,
                       (pu * pu * A[2] + 2 * pu * u * (A[2] + B[2]) / 2 + u * u * B[2]) * 1.25)
                pts.append(QPointF(*self._project(mid, R, cx, cy)[:2]))
            p.drawPolyline(pts)
            u = (self._t * 0.4 + ph) % 1
            pu = 1 - u
            pk = ((pu * pu * A[0] + 2 * pu * u * (A[0] + B[0]) / 2 + u * u * B[0]) * 1.25,
                  (pu * pu * A[1] + 2 * pu * u * (A[1] + B[1]) / 2 + u * u * B[1]) * 1.25,
                  (pu * pu * A[2] + 2 * pu * u * (A[2] + B[2]) / 2 + u * u * B[2]) * 1.25)
            X, Y, Z = self._project(pk, R, cx, cy)
            if Z > 0:
                p.setBrush(accent)
                p.drawEllipse(QPointF(X, Y), 2.2, 2.2)
        for i, nd in enumerate(self._nodes):
            X, Y, Z = self._project(nd, R, cx, cy)
            if Z <= 0:
                continue
            pulse = 0.5 + 0.5 * math.sin(self._t * 2 + i)
            a = int(64 + 140 * pulse * (Z * 0.5 + 0.5))
            p.setBrush(QColor(accent.red(), accent.green(), accent.blue(), a))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(X, Y), 1 + pulse * 1.6, 1 + pulse * 1.6)
        p.setPen(Qt.PenStyle.NoPen)

    def _paint_heatmap(self, p: QPainter, w: int, h: int) -> None:
        syms = self.symbols or ["—"]
        cols = max(2, math.ceil(math.sqrt(len(syms) * w / max(h, 1))))
        rows = math.ceil(len(syms) / cols)
        cw, ch = w / cols, h / rows
        for i, s in enumerate(syms):
            f = self.fusion.get(s) or {}
            conv = min(1.0, abs(f.get("convergence", 0.3)))
            long = f.get("direction", "long") == "long"
            base = _c("#00F0FF" if long else "#FF2D55")
            x, y = (i % cols) * cw, (i // cols) * ch
            p.setBrush(QColor(base.red(), base.green(), base.blue(), int(20 + 190 * conv)))
            p.setPen(QPen(QColor("#1E222B")))
            p.drawRect(x + 2, y + 2, cw - 4, ch - 4)
            p.setPen(QColor("#E8EAF0"))
            p.drawText(x + 8, y + 18, s)
            p.setPen(base)
            p.drawText(x + 8, y + 18 + min(13, cw * 0.14), f"{'LONG ▲' if long else 'SHORT ▼'} {conv*100:.0f}%")

    def _paint_routes(self, p: QPainter, w: int, h: int, accent: QColor) -> None:
        venues = ["LD4", "NY4", "TY3", "SG1", "FR2"]
        pts = []
        for i, v in enumerate(venues):
            ang = (i / len(venues)) * math.pi * 2 - math.pi / 2
            pts.append((w / 2 + math.cos(ang) * min(w, h) * 0.36,
                        h / 2 + math.sin(ang) * min(w, h) * 0.36, v))
        pen = QPen(QColor("#7A8090"))
        p.setPen(pen)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                p.drawLine(QPointF(pts[i][0], pts[i][1]), QPointF(pts[j][0], pts[j][1]))
        for k, s in enumerate(self.signals[-10:]):
            a, b = pts[k % len(pts)], pts[(k * 2 + 1) % len(pts)]
            ph = (self._t * 0.25 + k * 0.13) % 1
            p.setBrush(_c("#00F0FF" if s.get("direction") == "long" else "#FFB800"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(a[0] + (b[0] - a[0]) * ph, a[1] + (b[1] - a[1]) * ph), 3, 3)
        for x, y, v in pts:
            p.setBrush(QColor("#12141B"))
            p.setPen(QPen(accent))
            p.drawEllipse(QPointF(x, y), 16, 16)
            p.setPen(QColor("#E8EAF0"))
            p.drawText(x - 12, y + 3, v)
        p.setPen(QColor("#7A8090"))
        p.drawText(10, h - 10, "routing corridors · packets = live routed signals · SIMULATED")


class EquityWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("equity")
        self.setMinimumHeight(110)
        self.values: list[float] = []

    def push(self, v: float) -> None:
        self.values.append(v)
        if len(self.values) > 120:
            self.values.pop(0)
        self.update()

    def paintEvent(self, e) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        vals = self.values
        if len(vals) < 2:
            p.end()
            return
        accent = _c("#00F0FF")
        mn, mx = min(vals), max(vals)
        span = (mx - mn) or 1.0
        pts = [QPointF((i / 119) * w, h - ((v - mn) / span) * (h - 14) - 7) for i, v in enumerate(vals)]
        p.setPen(QPen(accent, 1.6))
        p.drawPolyline(pts)
        path = QPainterPath()
        path.moveTo(pts[0])
        for pt in pts[1:]:
            path.lineTo(pt)
        path.lineTo(w, h)
        path.lineTo(0, h)
        path.closeSubpath()
        fill = QColor(accent)
        fill.setAlpha(34)
        p.setBrush(fill)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(path)
        p.end()


class DepthWidget(QWidget):
    """Liquidity pool depth ladder around mid - SIMULATED, labelled in paint."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("depth")
        self.setMinimumHeight(120)
        self.mid = 0.0
        self.symbol = "EURUSD"
        self.step = 0.0

    def set_book(self, mid: float, step: float, symbol: str) -> None:
        self.mid, self.step, self.symbol = mid, step, symbol
        self.update()

    def paintEvent(self, e) -> None:  # noqa: N802
        p = QPainter(self)
        w, h = self.width(), self.height()
        n = 18
        rng = random.Random(int(self._t * 2) if hasattr(self, "_t") else 7)
        for i in range(n):
            size = (1 - i / n) * h * 0.42 * (0.6 + rng.random() * 0.4)
            bid = QColor("#00F0FF")
            bid.setAlpha(140)
            ask = QColor("#FF2D55")
            ask.setAlpha(140)
            p.setBrush(bid)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(w / 2 - 6 - i * w * 0.024, h - 10 - size, i * w * 0.024 + 6, size)
            p.setBrush(ask)
            p.drawRect(w / 2 + i * w * 0.024, h - 10 - size * 0.9, i * w * 0.024 + 6, size * 0.9)
        p.setPen(QColor("#E8EAF0"))
        p.drawText(8, 14, f"mid {self.mid:.5f} · step {self.step:.6f} · {self.symbol} · SIMULATED DEPTH")
        p.end()


class BarsWidget(QWidget):
    """9-layer fusion conviction bars (vertical bars, cyan long / crimson short)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.layers: dict[str, float] = {}

    def set_layers(self, layers: dict[str, float]) -> None:
        self.layers = layers
        self.update()

    def paintEvent(self, e) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        items = list(self.layers.items())
        if not items:
            p.end()
            return
        bw = w / len(items)
        for i, (tf, v) in enumerate(items):
            bh = abs(v) * (h - 20)
            color = _c("#FF2D55" if v < 0 else "#00F0FF")
            p.setBrush(color)
            p.setPen(Qt.PenStyle.NoPen)
            x = i * bw + 2
            p.drawRect(x, h - 14 - bh, bw - 4, max(bh, 2))
            p.setPen(QColor("#7A8090"))
            p.drawText(x, h - 2, tf)
        p.end()
