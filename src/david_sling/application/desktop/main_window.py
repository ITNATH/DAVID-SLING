"""L14 application/desktop/main_window - PySide6 Main Window for DAVID SLING IATOS.

Mirrors the web command-center shell 1:1 (same sections, same information, same
11-color XDR palette via QSS): top command bar, global KPI strip, left rail
(monitoring + protections + health + signals), center market core (interactive
globe/heatmap/routes + awareness + scenario + fusion + engines), right rail
(omni-trade execution tabs, engine control panel, positions/PnL, equity curve),
bottom tabbed console (trade journal, system logs, infrastructure, depth).

Every input/toggle/button is bound to the ServiceFacade backend; execution
commands run on the Mt5Worker thread (low-latency, GUI never blocks).
Destructive actions use press-and-hold 2s (HoldButton). Light/Dark via QSS swap.
"""
from __future__ import annotations

import json
import random
from datetime import UTC, datetime
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from david_sling.application.desktop.mt5_worker import Mt5Worker
from david_sling.application.desktop.qss import stylesheet
from david_sling.application.desktop.widgets import (
    BarsWidget,
    DepthWidget,
    EquityWidget,
    GlobeWidget,
)

MONO = QFont("JetBrains Mono", 9)


class HoldButton(QPushButton):
    """Press-and-hold 2s confirmation for destructive actions."""

    def __init__(self, text: str, hold_ms: int = 2000, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.addClass = "hold"
        self._hold_ms = hold_ms
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fire)
        self._fired = False
        self._held_cb = None

    def on_held(self, cb) -> None:
        self._held_cb = cb

    def mousePressEvent(self, e) -> None:  # noqa: N802
        self._fired = False
        self._timer.start(self._hold_ms)
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e) -> None:  # noqa: N802
        self._timer.stop()
        super().mouseReleaseEvent(e)

    def _fire(self) -> None:
        self._fired = True
        if self._held_cb:
            self._held_cb()


class MainWindow(QMainWindow):
    """DAVID SLING desktop command center - fully wired to the backend facade."""

    def __init__(self, facade, mode: str = "sim", parent: QWidget | None = None,
                 loop=None) -> None:
        super().__init__(parent)
        self.facade = facade
        self.mode = mode
        self.theme = "dark"
        self.selected = "EURUSD"
        self.symbols: list[str] = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "V75", "V25", "STEP"]
        self.worker = Mt5Worker(facade, self, loop=loop)
        self.worker.result.connect(self._on_result)
        self.worker.error.connect(lambda m: self.statusBar().showMessage(f"⚠ {m}", 6000))
        self.worker.connected.connect(self._on_link)
        self.worker.start()
        self._build_ui()
        self.apply_theme("dark")
        self._poll = QTimer(self)
        self._poll.timeout.connect(self.refresh)
        self._poll.start(500)
        self._journal_timer = QTimer(self)
        self._journal_timer.timeout.connect(self._refresh_journal)
        self._journal_timer.start(3000)
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick_clock)
        self._clock.start(1000)
        self._refresh_symbols()
        self.refresh()
        self._refresh_journal()

    # ================================================================ UI build
    def _build_ui(self) -> None:
        self.setWindowTitle("DAVID SLING — Global Overview & Execution Command Center")
        self.resize(1600, 950)
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(8)
        root.addWidget(self._build_topbar())
        root.addWidget(self._build_kpi_strip())
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self._build_main_grid())
        splitter.addWidget(self._build_console())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        root.addWidget(splitter, 1)
        self.setCentralWidget(central)
        self.statusBar().showMessage("DAVID SLING IATOS · pure Python · L0–L14 zero-circular · SIMULATED FEED unless MT5 live")

    def _build_topbar(self) -> QWidget:
        bar = QWidget(self)
        bar.setObjectName("topbar")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 6, 12, 6)
        logo = QLabel("◆")
        logo.setObjectName("logo")
        lay.addWidget(logo)
        brand = QLabel("DAVID SLING")
        brand.setObjectName("brandName")
        lay.addWidget(brand)
        sub = QLabel("IATOS · Global Overview & Execution Command Center")
        sub.setObjectName("brandSub")
        sub.setProperty("class", "dim")
        lay.addWidget(sub)
        lay.addStretch(1)
        self.conn_pill = QLabel("● connecting…")
        self.conn_pill.setObjectName("connPill")
        self.conn_pill.setProperty("class", "pill")
        lay.addWidget(self.conn_pill)
        self.boot_pill = QLabel("boot …")
        self.boot_pill.setProperty("class", "pill")
        lay.addWidget(self.boot_pill)
        self.session_pill = QLabel("—")
        self.session_pill.setProperty("class", "pill")
        lay.addWidget(self.session_pill)
        self.clock_lbl = QLabel("--:--:--")
        self.clock_lbl.setProperty("class", "pill mono")
        lay.addWidget(self.clock_lbl)
        self.theme_btn = QPushButton("🌙 Dark")
        self.theme_btn.clicked.connect(self._toggle_theme)
        lay.addWidget(self.theme_btn)
        return bar

    def _kpi(self, k: str) -> tuple[QLabel, QLabel]:
        kk = QLabel(k)
        kk.setProperty("class", "kpiK")
        vv = QLabel("—")
        vv.setProperty("class", "kpiV mono")
        box = QVBoxLayout()
        box.setSpacing(1)
        box.addWidget(kk)
        box.addWidget(vv)
        w = QWidget()
        w.setLayout(box)
        return vv, w

    def _build_kpi_strip(self) -> QWidget:
        strip = QWidget(self)
        strip.setObjectName("kpiStrip")
        lay = QHBoxLayout(strip)
        lay.setContentsMargins(12, 8, 12, 8)
        self.kpis: dict[str, QLabel] = {}
        self.kpi_boxes: dict[str, tuple[QLabel, QLabel]] = {}
        for k in ["Balance", "Equity", "Floating PnL", "Margin", "Free Margin", "Margin Level %"]:
            vv, box = self._kpi(k)
            self.kpis[k] = vv
            lay.addWidget(box)
        lay.addStretch(1)
        side = QVBoxLayout()
        mr = QHBoxLayout()
        ml = QLabel("Margin risk")
        ml.setProperty("class", "dim")
        mr.addWidget(ml)
        self.margin_bar = QProgressBar()
        self.margin_bar.setRange(0, 100)
        mr.addWidget(self.margin_bar, 1)
        self.margin_lbl = QLabel("—")
        self.margin_lbl.setProperty("class", "dim mono")
        mr.addWidget(self.margin_lbl)
        side.addLayout(mr)
        self.ledger_lbl = QLabel("ledger —")
        self.ledger_lbl.setProperty("class", "mono dim")
        side.addWidget(self.ledger_lbl)
        lay.addLayout(side)
        return strip

    def _card(self, title: str) -> tuple[QGroupBox, QVBoxLayout]:
        g = QGroupBox(title)
        g.setProperty("class", "card")
        v = QVBoxLayout(g)
        v.setContentsMargins(10, 6, 10, 10)
        return g, v

    def _build_main_grid(self) -> QWidget:
        grid = QSplitter(Qt.Orientation.Horizontal)
        grid.addWidget(self._rail_scroll(self._build_left_rail()))
        grid.addWidget(self._rail_scroll(self._build_center()))
        grid.addWidget(self._rail_scroll(self._build_right_rail()))
        grid.setStretchFactor(0, 0)
        grid.setStretchFactor(1, 1)
        grid.setStretchFactor(2, 0)
        for i, wdt in enumerate((290, 0, 380)):
            grid.setStretchFactor(i, 1 if wdt == 0 else 0)
        grid.setSizes([290, 700, 380])
        return grid

    def _rail_scroll(self, content: QWidget) -> QScrollArea:
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setWidget(content)
        return sa

    # -------------------------------------------------- left rail
    def _build_left_rail(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 4, 0)
        lay.setSpacing(8)

        mon, mv = self._card("Monitoring · Learning Engine  [LIVE]")
        stats = QGridLayout()
        self.mon_stats = {}
        for i, k in enumerate(["Dispatch avg", "Rescans", "Risk vetoes", "Drift proposals"]):
            kk = QLabel(k)
            kk.setProperty("class", "kpiK")
            vv = QLabel("—")
            vv.setProperty("class", "kpiV mono")
            stats.addWidget(kk, 0, i)
            stats.addWidget(vv, 1, i)
            self.mon_stats[k] = vv
        mv.addLayout(stats)
        self.mon_table = QTableWidget(0, 4)
        self.mon_table.setHorizontalHeaderLabels(["Strategy", "Trades", "Win %", "PnL"])
        self.mon_table.horizontalHeader().setStretchLastSection(True)
        mv.addWidget(self.mon_table)
        self.mon_props = QListWidget()
        self.mon_props.setMaximumHeight(70)
        mv.addWidget(self.mon_props)
        lay.addWidget(mon)

        prot, pv = self._card("Protections · Status Indicators")
        self.prot_rows = {}
        for k in ["News Filter", "Breakeven", "Spike Defence", "Thesis Failure"]:
            row = QHBoxLayout()
            kk = QLabel(k)
            kk.setProperty("class", "dim")
            kk.setFixedWidth(110)
            vv = QLabel("—")
            vv.setProperty("class", "mono")
            row.addWidget(kk)
            row.addWidget(vv, 1)
            pv.addLayout(row)
            self.prot_rows[k] = vv
        lay.addWidget(prot)

        health, hv = self._card("System Health Matrix")
        self.health_grid = QGridLayout()
        hv.addLayout(self.health_grid)
        self.health_cells: dict[str, QLabel] = {}
        lay.addWidget(health)

        sig, sv = self._card("Order Flow · Active Signals")
        self.signals_list = QListWidget()
        sv.addWidget(self.signals_list)
        lay.addWidget(sig, 1)
        lay.addStretch(1)
        return w

    # -------------------------------------------------- center
    def _build_center(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 4, 0)
        lay.setSpacing(8)

        globe_card, gv = self._card("Global Liquidity & Asset Flow")
        head = QHBoxLayout()
        self.mode_btns = {}
        for m, label in [("globe", "◉ GLOBE"), ("heatmap", "▦ HEATMAP"), ("routes", "⑃ ROUTES")]:
            b = QPushButton(label)
            b.setCheckable(True)
            b.setChecked(m == "globe")
            b.clicked.connect(lambda _=False, mm=m: self._set_globe_mode(mm))
            head.addWidget(b)
            self.mode_btns[m] = b
        self.globe_hint = QLabel("drag = rotate · wheel = zoom · SIMULATED FEED")
        self.globe_hint.setProperty("class", "dim mono")
        head.addStretch(1)
        head.addWidget(self.globe_hint)
        gv.addLayout(head)
        self.globe = GlobeWidget()
        gv.addWidget(self.globe, 1)
        lay.addWidget(globe_card, 1)

        tri = QHBoxLayout()
        aw_card, aw = self._card("Market Awareness")
        self.symbol_combo = QComboBox()
        self.symbol_combo.currentTextChanged.connect(self._on_symbol_change)
        aw.addWidget(self.symbol_combo)
        self.aw_labels = {}
        awf = QFormLayout()
        for k in ["Price", "ATR(M1)", "ATR% H1", "Spread (pts)", "Session", "Phase", "Regime"]:
            vv = QLabel("—")
            vv.setProperty("class", "mono")
            awf.addRow(k, vv)
            self.aw_labels[k] = vv
        aw.addLayout(awf)
        tri.addWidget(aw_card)

        sc_card, sc = self._card("Universal Scenario Pool")
        self.scenario_badge = QLabel("—")
        self.scenario_badge.setProperty("class", "bigBadge")
        sc.addWidget(self.scenario_badge)
        self.hyp_labels = {}
        hf = QFormLayout()
        for k in ["Confidence", "Forming", "Class"]:
            vv = QLabel("—")
            vv.setProperty("class", "mono")
            hf.addRow(k, vv)
            self.hyp_labels[k] = vv
        sc.addLayout(hf)
        tri.addWidget(sc_card)

        fu_card, fu = self._card("9-Layer Fusion Brain")
        self.fusion_badge = QLabel("—")
        self.fusion_badge.setProperty("class", "bigBadge")
        fu.addWidget(self.fusion_badge)
        self.bars = BarsWidget()
        fu.addWidget(self.bars, 1)
        tri.addWidget(fu_card)
        lay.addLayout(tri)

        eng_card, ev = self._card("Peer Engines")
        self.engine_grid = QGridLayout()
        ev.addLayout(self.engine_grid)
        self.engine_cells: dict[str, QLabel] = {}
        lay.addWidget(eng_card)
        lay.addStretch(1)
        return w

    # -------------------------------------------------- right rail
    def _build_right_rail(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 4, 0)
        lay.setSpacing(8)

        trade_card, tv = self._card("⚡ Omni-Trade Execution & Basket Panel")
        self.trade_tabs = QTabWidget()
        tv.addWidget(self.trade_tabs)
        self.trade_tabs.addTab(self._build_single_tab(), "Single Trade")
        self.trade_tabs.addTab(self._build_multi_tab(), "Single-Pair Multi")
        self.trade_tabs.addTab(self._build_basket_tab(), "Cross-Pair Basket")
        self.trade_result = QLabel("")
        self.trade_result.setProperty("class", "dim mono")
        self.trade_result.setWordWrap(True)
        tv.addWidget(self.trade_result)
        lay.addWidget(trade_card)

        ctl_card, cv = self._card("🎛 Control Panel — Engine Controls (authorized, ledgered)")
        self.engine_rows: dict[str, tuple[QLabel, object]] = {}
        self.engine_box = QVBoxLayout()
        cv.addLayout(self.engine_box)
        self.control_result = QLabel("config v1 · mutations recorded in evidence ledger")
        self.control_result.setProperty("class", "dim")
        cv.addWidget(self.control_result)
        lay.addWidget(ctl_card)

        pos_card, pv = self._card("Open Positions & Cross-Pair PnL")
        self.pos_table = QTableWidget(0, 11)
        self.pos_table.setHorizontalHeaderLabels(
            ["ID", "Symbol", "Side", "Vol", "Entry", "SL", "TP", "PnL", "BE", "", ""])
        pv.addWidget(self.pos_table)
        self.pnl_table = QTableWidget(0, 7)
        self.pnl_table.setHorizontalHeaderLabels(
            ["Symbol", "Gross Profit", "Gross Loss", "Net", "Swap", "Margin", "Pos"])
        pv.addWidget(self.pnl_table)
        lay.addWidget(pos_card)

        eq_card, qv = self._card("Equity Curve · Capital Deployment")
        self.equity = EquityWidget()
        qv.addWidget(self.equity, 1)
        lay.addWidget(eq_card)
        lay.addStretch(1)
        return w

    def _lbl(self, text: str = "") -> QLabel:
        lbl = QLabel(text)
        lbl.setProperty("class", "dim")
        return lbl

    def _build_single_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        r1 = QHBoxLayout()
        self.t_symbol = QComboBox()
        self.t_side = QComboBox()
        self.t_side.addItems(["BUY", "SELL"])
        self.t_type = QComboBox()
        self.t_type.addItems(["MARKET", "LIMIT", "STOP"])
        self.t_vol = QDoubleSpinBox()
        self.t_vol.setRange(0.01, 100.0)
        self.t_vol.setSingleStep(0.01)
        self.t_vol.setValue(0.10)
        for lbl, ctl in [("Symbol", self.t_symbol), ("Side", self.t_side), ("Type", self.t_type), ("Volume (lots)", self.t_vol)]:
            box = QVBoxLayout()
            box.addWidget(self._lbl(lbl))
            box.addWidget(ctl)
            r1.addLayout(box)
        lay.addLayout(r1)
        r2 = QHBoxLayout()
        self.t_price = QLineEdit()
        self.t_price.setPlaceholderText("market")
        self.t_sl = QLineEdit()
        self.t_tp = QLineEdit()
        self.t_risk = QDoubleSpinBox()
        self.t_risk.setRange(0.1, 10.0)
        self.t_risk.setValue(1.0)
        for lbl, ctl in [("Price (limit/stop)", self.t_price), ("Stop Loss", self.t_sl),
                         ("Take Profit", self.t_tp), ("Risk %", self.t_risk)]:
            box = QVBoxLayout()
            box.addWidget(self._lbl(lbl))
            box.addWidget(ctl)
            r2.addLayout(box)
        lay.addLayout(r2)
        r3 = QHBoxLayout()
        self.btn_open = QPushButton("OPEN TRADE")
        self.btn_open.setProperty("class", "btnBuy")
        self.btn_open.clicked.connect(self._cmd_open)
        r3.addWidget(self.btn_open)
        self.r_multiple = QLabel("")
        self.r_multiple.setProperty("class", "dim")
        r3.addWidget(self.r_multiple)
        r3.addStretch(1)
        lay.addLayout(r3)
        for f in (self.t_price, self.t_sl, self.t_tp):
            f.textChanged.connect(self._update_r)
        lay.addStretch(1)
        return w

    def _batch_buttons(self, lay: QHBoxLayout, scope_symbol: bool) -> None:
        """The 4 batch buttons, identical in BOTH operational modules (multi + basket)."""
        def add(btn: QPushButton) -> None:
            lay.addWidget(btn)
        b1 = QPushButton("Close Losing")
        b1.setProperty("class", "btnSell")
        b1.clicked.connect(lambda: self._cmd_batch({"only_losing": True}))
        b2 = QPushButton("Close Profitable")
        b2.clicked.connect(lambda: self._cmd_batch({"only_profitable": True}))
        b3 = HoldButton("Close All ⏱")
        b3.setProperty("class", "btnWarn")
        b3.on_held(lambda: self._cmd_batch({}))
        b4 = QPushButton("Break-Even All")
        b4.setProperty("class", "btnWarn")
        b4.clicked.connect(lambda: self.worker.enqueue("breakeven_all", self.facade.breakeven_all))
        for b in (b1, b2, b3, b4):
            add(b)
        return None

    def _override_buttons(self, lay: QHBoxLayout) -> None:
        self.btn_panic = HoldButton("🚨 PANIC FLATTEN ⏱")
        self.btn_panic.setProperty("class", "btnDanger")
        self.btn_panic.on_held(self.worker.panic)
        self.btn_halt = HoldButton("⛔ EMERGENCY HALT ⏱")
        self.btn_halt.setProperty("class", "btnWarn")
        self.btn_halt.on_held(self._cmd_halt)
        self.btn_resume = QPushButton("▶ RESUME TRADING")
        self.btn_resume.setProperty("class", "btnOk")
        self.btn_resume.clicked.connect(self.worker.resume)
        for b in (self.btn_panic, self.btn_halt, self.btn_resume):
            lay.addWidget(b)

    def _build_multi_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        r1 = QHBoxLayout()
        self.m_symbol = QComboBox()
        self.m_side = QComboBox()
        self.m_side.addItems(["BUY", "SELL"])
        self.m_tranches = QSpinBox()
        self.m_tranches.setRange(1, 10)
        self.m_tranches.setValue(3)
        self.m_lots = QDoubleSpinBox()
        self.m_lots.setRange(0.01, 100.0)
        self.m_lots.setSingleStep(0.01)
        self.m_lots.setValue(0.05)
        for lbl, ctl in [("Symbol", self.m_symbol), ("Side", self.m_side),
                         ("Tranches", self.m_tranches), ("Lots/tranche", self.m_lots)]:
            box = QVBoxLayout()
            box.addWidget(self._lbl(lbl))
            box.addWidget(ctl)
            r1.addLayout(box)
        lay.addLayout(r1)
        r2 = QHBoxLayout()
        self.m_sl = QLineEdit()
        self.m_tp = QLineEdit()
        self.btn_multi = QPushButton("EXECUTE LADDER")
        self.btn_multi.setProperty("class", "btnBuy")
        self.btn_multi.clicked.connect(self._cmd_multi)
        for lbl, ctl in [("SL", self.m_sl), ("TP", self.m_tp)]:
            box = QVBoxLayout()
            box.addWidget(self._lbl(lbl))
            box.addWidget(ctl)
            r2.addLayout(box)
        r2.addWidget(self.btn_multi)
        lay.addLayout(r2)
        r3 = QHBoxLayout()
        self._batch_buttons(r3, True)
        lay.addLayout(r3)
        r4 = QHBoxLayout()
        self._override_buttons(r4)
        lay.addLayout(r4)
        lay.addStretch(1)
        return w

    def _build_basket_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        r1 = QHBoxLayout()
        self.basket_checks: dict[str, QCheckBox] = {}
        for s in self.symbols:
            cb = QCheckBox(s)
            cb.setChecked(s in ("EURUSD", "USDJPY"))
            self.basket_checks[s] = cb
            r1.addWidget(cb)
        r1.addStretch(1)
        lay.addLayout(r1)
        r2 = QHBoxLayout()
        self.b_side = QComboBox()
        self.b_side.addItems(["BUY", "SELL"])
        self.b_lots = QDoubleSpinBox()
        self.b_lots.setRange(0.01, 100.0)
        self.b_lots.setSingleStep(0.01)
        self.b_lots.setValue(0.05)
        self.b_sl = QDoubleSpinBox()
        self.b_sl.setRange(0.1, 10.0)
        self.b_sl.setValue(1.5)
        self.b_rr = QDoubleSpinBox()
        self.b_rr.setRange(0.1, 10.0)
        self.b_rr.setValue(2.0)
        for lbl, ctl in [("Side", self.b_side), ("Lots each", self.b_lots),
                         ("SL (×ATR)", self.b_sl), ("TP (R)", self.b_rr)]:
            box = QVBoxLayout()
            box.addWidget(self._lbl(lbl))
            box.addWidget(ctl)
            r2.addLayout(box)
        self.btn_basket = QPushButton("EXECUTE BASKET")
        self.btn_basket.setProperty("class", "btnBuy")
        self.btn_basket.clicked.connect(self._cmd_basket)
        r2.addWidget(self.btn_basket)
        lay.addLayout(r2)
        r3 = QHBoxLayout()
        self._batch_buttons(r3, False)  # same 4 batch buttons in the basket module
        lay.addLayout(r3)
        r4 = QHBoxLayout()
        self._override_buttons(r4)
        lay.addLayout(r4)
        lay.addStretch(1)
        return w

    # -------------------------------------------------- bottom console
    def _build_console(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.setMaximumHeight(280)

        jw = QWidget()
        jl = QVBoxLayout(jw)
        self.journal_table = QTableWidget(0, 7)
        self.journal_table.setHorizontalHeaderLabels(
            ["Time", "Kind", "Symbol", "Side", "Detail", "PnL", "Evidence"])
        self.journal_table.horizontalHeader().setStretchLastSection(True)
        jl.addWidget(self.journal_table)
        tabs.addTab(jw, "📓 Trade Journal")

        lw = QWidget()
        ll = QVBoxLayout(lw)
        frow = QHBoxLayout()
        self.log_filter = "ALL"
        self.lv_btns = {}
        for lv in ["ALL", "INFO", "WARNING", "CRITICAL"]:
            b = QPushButton(lv)
            b.setCheckable(True)
            b.setChecked(lv == "ALL")
            b.clicked.connect(lambda _=False, x=lv: self._set_log_filter(x))
            frow.addWidget(b)
            self.lv_btns[lv] = b
        frow.addStretch(1)
        ll.addLayout(frow)
        self.logs_list = QListWidget()
        ll.addWidget(self.logs_list, 1)
        tabs.addTab(lw, "🖥 System Logs")

        iw = QWidget()
        il = QHBoxLayout(iw)
        lat_box = QVBoxLayout()
        lat_box.addWidget(self._lbl("Multi-Region Cloud Latency  [SIMULATED]"))
        self.lat_grid = QGridLayout()
        self.lat_labels = {}
        for i, r in enumerate(["LD4", "NY4", "TY3", "SG1", "FR2", "CH1"]):
            lbl = QLabel(f"{r} —")
            lbl.setProperty("class", "mono")
            self.lat_grid.addWidget(lbl, i % 3, i // 3)
            self.lat_labels[r] = lbl
        lat_box.addLayout(self.lat_grid)
        il.addLayout(lat_box)
        ven_box = QVBoxLayout()
        ven_box.addWidget(self._lbl("Exchange Connectivity  [SIMULATED FEED]"))
        self.ven_labels = {}
        for v in ["SIM-PRIME", "SIM-LP-1", "SIM-LP-2", "SIM-XCHG"]:
            lbl = QLabel(f"{v} —")
            lbl.setProperty("class", "mono")
            ven_box.addWidget(lbl)
            self.ven_labels[v] = lbl
        ven_box.addStretch(1)
        il.addLayout(ven_box)
        tabs.addTab(iw, "🌐 Infrastructure")

        dw = QWidget()
        dl = QVBoxLayout(dw)
        dl.addWidget(self._lbl("Liquidity Pool Depth  [SIMULATED]"))
        self.depth = DepthWidget()
        dl.addWidget(self.depth, 1)
        tabs.addTab(dw, "📊 Liquidity Depth")
        self.console_tabs = tabs
        return tabs

    # ================================================================ bindings
    def _refresh_symbols(self) -> None:
        try:
            m = self.facade.market()
            inner = m.get("market", m) if isinstance(m, dict) else m
            syms = sorted(inner.keys()) if isinstance(inner, dict) else list(inner)
            if syms:
                self.symbols = syms
        except Exception:
            pass
        for combo in (self.symbol_combo, self.t_symbol, self.m_symbol):
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(self.symbols)
            combo.setCurrentText(self.selected if self.selected in self.symbols else self.symbols[0])
            combo.blockSignals(False)
        for _s, cb in list(self.basket_checks.items()):
            cb.setParent(None)
            cb.deleteLater()
        self.basket_checks.clear()
        # rebuild basket checkboxes in place
        host = self.trade_tabs.widget(2).layout().itemAt(0).layout()
        for s in self.symbols:
            cb = QCheckBox(s)
            cb.setChecked(s in ("EURUSD", "USDJPY"))
            self.basket_checks[s] = cb
            host.insertWidget(host.count() - 1, cb)

    def _on_symbol_change(self, s: str) -> None:
        if s:
            self.selected = s

    def _set_globe_mode(self, m: str) -> None:
        self.globe.set_mode(m)
        for k, b in self.mode_btns.items():
            b.setChecked(k == m)
        self.globe_hint.setText({
            "globe": "drag = rotate · wheel = zoom · SIMULATED FEED",
            "heatmap": "2D tactical heatmap · cell = fusion conviction · wheel out = globe",
            "routes": "order-routing corridors · packets = routed signals · wheel out = heatmap"}[m])

    def _toggle_theme(self) -> None:
        self.apply_theme("light" if self.theme == "dark" else "dark")

    def apply_theme(self, theme: str) -> None:
        self.theme = theme
        self.setStyleSheet(stylesheet(theme))
        self.theme_btn.setText("☀️ Light" if theme == "light" else "🌙 Dark")

    def _num(self, le: QLineEdit) -> float | None:
        t = le.text().strip()
        if not t:
            return None
        try:
            return float(t)
        except ValueError:
            return None

    def _update_r(self) -> None:
        sl, tp = self._num(self.t_sl), self._num(self.t_tp)
        px = self._num(self.t_price)
        if sl and tp:
            ref = px if px else self._last_price
            if ref:
                r = abs(tp - ref) / abs(ref - sl) if ref != sl else 0.0
                self.r_multiple.setText(f"R ≈ {r:.2f} (SL dist {abs(ref - sl):.5f})")

    # ---- execution commands (run on the Mt5Worker thread) ----
    def _cmd_open(self) -> None:
        payload = {
            "symbol": self.t_symbol.currentText(), "side": self.t_side.currentText(),
            "order_type": self.t_type.currentText(), "volume": self.t_vol.value(),
            "price": self._num(self.t_price), "sl": self._num(self.t_sl),
            "tp": self._num(self.t_tp), "risk_pct": self.t_risk.value(),
        }
        self.worker.enqueue("single", lambda: self.facade.execute_single_trade(payload))

    def _cmd_multi(self) -> None:
        payload = {
            "symbol": self.m_symbol.currentText(), "side": self.m_side.currentText(),
            "tranches": self.m_tranches.value(), "lots": self.m_lots.value(),
            "sl": self._num(self.m_sl), "tp": self._num(self.m_tp),
        }
        self.worker.enqueue("multi", lambda: self.facade.execute_single_pair_multi(payload))

    def _cmd_basket(self) -> None:
        payload = {
            "symbols": [s for s, cb in self.basket_checks.items() if cb.isChecked()],
            "side": self.b_side.currentText(), "lots": self.b_lots.value(),
            "sl_atr_mult": self.b_sl.value(), "tp_rr": self.b_rr.value(),
        }
        self.worker.enqueue("basket", lambda: self.facade.execute_cross_pair_basket(payload))

    def _cmd_batch(self, extra: dict) -> None:
        payload = dict(extra)
        payload["symbol"] = self.selected
        self.worker.enqueue("batch_close", lambda: self.facade.batch_close(payload))

    def _cmd_halt(self) -> None:
        reason, ok = QInputDialog.getText(self, "EMERGENCY HALT", "Halt reason:", text="operator emergency halt")
        if ok and reason:
            self.worker.halt(reason)

    def _close_pos(self, pid: str, pct: float | None) -> None:
        self.worker.enqueue("close", lambda: self.facade.close_position(pid, pct))

    def _toggle_engine(self, engine_id: str, on: bool) -> None:
        self.worker.enqueue("engine", lambda: self.facade.set_engine(engine_id, on, actor="desktop-operator"))

    def _on_result(self, tag: str, res: Any) -> None:
        try:
            txt = res if isinstance(res, str) else json.dumps(res, default=str)[:300]
        except Exception:
            txt = str(res)
        self.trade_result.setText(f"[{tag}] {txt}")
        ok = isinstance(res, dict) and (res.get("ok") or res.get("closed") or res.get("halted") is not None
                                        or res.get("flattened") is not None or res.get("breakeven_set") is not None
                                        or res.get("engine"))
        self.statusBar().showMessage(f"{'✓' if ok else '⚠'} {tag}: {txt[:120]}", 5000)
        self.refresh()

    def _on_link(self, ok: bool, info: str) -> None:
        self.conn_pill.setText(f"● {'LIVE' if ok else 'SIM'} · {info}")
        self.conn_pill.setProperty("class", "pill pillOk" if ok else "pill pillWarn")
        self.conn_pill.style().unpolish(self.conn_pill)
        self.conn_pill.style().polish(self.conn_pill)
        self.boot_pill.setText("boot OK")
        self.boot_pill.setProperty("class", "pill pillOk")
        self.boot_pill.style().unpolish(self.boot_pill)
        self.boot_pill.style().polish(self.boot_pill)

    # ================================================================ refresh
    def refresh(self) -> None:
        try:
            ov = self.facade.overview()
        except Exception as exc:
            self.statusBar().showMessage(f"⚠ overview: {exc}", 4000)
            return
        self._render_overview(ov)
        try:
            self._render_protections(self.facade.protection_status())
        except Exception as exc:
            self.statusBar().showMessage(f"⚠ protections: {exc}", 4000)
        try:
            self._render_monitoring(self.facade.monitoring())
        except Exception as _exc:
            self.statusBar().showMessage(f"⚠ monitoring: {_exc}", 3000)
        self._tick_infra(ov.get("feed_ticks", 0))

    def _render_overview(self, ov: dict) -> None:
        acct = ov.get("account", {})
        self._last_price = None
        for k, v, d in [("Balance", acct.get("balance"), 2), ("Equity", acct.get("equity"), 2),
                        ("Floating PnL", acct.get("floating_pnl"), 2), ("Margin", acct.get("margin"), 2),
                        ("Free Margin", acct.get("free_margin"), 2), ("Margin Level %", acct.get("margin_level_pct"), 1)]:
            lbl = self.kpis[k]
            lbl.setText("—" if v is None else f"{float(v):,.{d}f}")
            if k == "Floating PnL" and v is not None:
                lbl.setProperty("class", "kpiV mono " + ("pos" if v >= 0 else "neg"))
            else:
                lbl.setProperty("class", "kpiV mono")
        ml = acct.get("margin_level_pct") or 0
        self.margin_bar.setValue(int(max(0, min(100, ml if ml <= 1000 else 100))))
        state = "SAFE" if ml >= 300 else "CAUTION" if ml >= 150 else "CRITICAL"
        self.margin_lbl.setText(f"{ml:.1f}% {state}")
        led = ov.get("ledger", {})
        self.ledger_lbl.setText(f"Entries {led.get('entries')} · Chain {'✓ VERIFIED (SHA3-256)' if led.get('chain_ok') else '✗ BROKEN'}")
        self.session_pill.setText(f"{ov.get('session_phase')} · {ov.get('session_epoch')}")
        ts = ov.get("ts", "")
        self._foot_ts = ts

        # health
        health = ov.get("health", [])
        while self.health_grid.count():
            item = self.health_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.health_cells.clear()
        for i, x in enumerate(health):
            lbl = QLabel(f"{'●' if x.get('healthy') else '●'} {x.get('domain')} {x.get('layer')} {'OK' if x.get('healthy') else 'DOWN'}")
            lbl.setProperty("class", "hcell" + ("" if x.get("healthy") else " neg"))
            self.health_grid.addWidget(lbl, i // 2, i % 2)

        # signals
        self.signals_list.clear()
        for s in list(ov.get("signals", []))[-14:][::-1]:
            it = QListWidgetItem(f"T{s['precision']['tier']} {s['symbol']} {s['direction'].upper()} · "
                                 f"{s['strategy_id']} · Eng {s['engine']} · {s['scenario']} · {s['status']} · R{s['risk_reward']:.1f}")
            self.signals_list.addItem(it)

        # awareness / scenario / fusion for selected symbol
        aw = ov.get("awareness", {}).get(self.selected)
        if aw:
            self._last_price = aw.get("price")
            vals = {"Price": f"{aw['price']:.5f}", "ATR(M1)": f"{aw.get('atr_m1', 0):.6f}",
                    "ATR% H1": f"{aw.get('atr_pct_h1', 0):.1f}", "Spread (pts)": f"{aw.get('spread_points', 0):.1f}",
                    "Session": aw.get("session_epoch", ""), "Phase": aw.get("session_phase", ""),
                    "Regime": f"{aw.get('regime')} ({aw.get('regime_confidence', 0)*100:.0f}%)"}
            for k, v in vals.items():
                self.aw_labels[k].setText(str(v))
            self.depth.set_book(aw.get("price", 0), max(aw.get("atr_m1", 0) * 0.25, 1e-9), self.selected)
        sc = ov.get("scenarios", {}).get(self.selected)
        if sc:
            self.scenario_badge.setText(f"{sc.get('scenario')} · {sc.get('family')}")
            self.scenario_badge.setStyleSheet("color: #00F0FF;" if str(sc.get("scenario", "")).startswith("S") else "color: #FFB800;")
            self.hyp_labels["Confidence"].setText(f"{sc.get('confidence', 0)*100:.0f}%")
            self.hyp_labels["Forming"].setText("yes (bar open)" if sc.get("forming") else "no (closed)")
            self.hyp_labels["Class"].setText("structural" if str(sc.get("scenario", "")).startswith("S") else "flow")
        fu = ov.get("fusion", {}).get(self.selected)
        if fu:
            self.fusion_badge.setText(f"{fu['direction'].upper()} · conv {fu['convergence']*100:.0f}% · conflicts {fu['conflicts']}")
            self.fusion_badge.setStyleSheet(
                "color: #00F0FF;" if fu["direction"] == "long" else "color: #FF2D55;" if fu["direction"] == "short" else "color: #7A8090;")
            self.bars.set_layers(fu.get("layers", {}))
        fusion_all = ov.get("fusion", {})
        self.globe.set_market(self.symbols, fusion_all, ov.get("signals", []))

        # engines cards
        while self.engine_grid.count():
            item = self.engine_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.engine_cells.clear()
        for i, (eid, e) in enumerate(sorted(ov.get("engines", {}).items())):
            lbl = QLabel(f"Engine {eid} — {e['name']}\n{e['horizon']} · ctx {'/'.join(e['context_tfs'])} · trig {'/'.join(e['trigger_tfs'])}\n{e['state']}" + ("" if e.get("enabled") else " · OFF"))
            lbl.setProperty("class", "hcell")
            lbl.setWordWrap(True)
            self.engine_grid.addWidget(lbl, i // 2, i % 2)
            self.engine_cells[eid] = lbl

        # engine control rows
        while self.engine_box.count():
            item = self.engine_box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.engine_rows.clear()
        for eid, e in sorted(ov.get("engines", {}).items()):
            row = QHBoxLayout()
            idl = QLabel(eid)
            idl.setProperty("class", "mono")
            idl.setStyleSheet("font-size: 19px; font-weight: 800; color: #00F0FF;" if e.get("enabled") else "font-size: 19px; font-weight: 800; color: #FF2D55;")
            idl.setFixedWidth(26)
            meta = QLabel(f"{e['name']} · {e['horizon']}\nctx {'/'.join(e['context_tfs'])} · trig {'/'.join(e['trigger_tfs'])} · {e['state']}")
            meta.setProperty("class", "dim")
            meta.setWordWrap(True)
            cb = QCheckBox()
            cb.setChecked(bool(e.get("enabled")))
            cb.toggled.connect(lambda on, eid=eid: self._toggle_engine(eid, on))
            row.addWidget(idl)
            row.addWidget(meta, 1)
            row.addWidget(cb)
            boxw = QWidget()
            boxw.setLayout(row)
            self.engine_box.addWidget(boxw)
            self.engine_rows[eid] = cb

        # positions + pnl
        pos = ov.get("positions", [])
        self.pos_table.setRowCount(len(pos))
        for r, p in enumerate(pos):
            cells = [p["position_id"][:12], p["symbol"], p["side"], f"{p['volume']}",
                     f"{p['entry_price']:.5f}", f"{p.get('stop_loss') or 0:.5f}", f"{p.get('take_profit') or 0:.5f}",
                     f"{p.get('realized_pnl', 0):.2f}", "✓" if p.get("breakeven_done") else ""]
            for c, v in enumerate(cells):
                self.pos_table.setItem(r, c, QTableWidgetItem(str(v)))
            b50 = QPushButton("50%")
            b50.clicked.connect(lambda _=False, pid=p["position_id"]: self._close_pos(pid, 0.5))
            bx = QPushButton("✕")
            bx.setProperty("class", "btnSell")
            bx.clicked.connect(lambda _=False, pid=p["position_id"]: self._close_pos(pid, None))
            self.pos_table.setCellWidget(r, 9, b50)
            self.pos_table.setCellWidget(r, 10, bx)
        if not pos:
            self.pos_table.setRowCount(1)
            self.pos_table.setItem(0, 0, QTableWidgetItem("flat — no open positions"))
        pnl = ov.get("pnl_matrix", [])
        self.pnl_table.setRowCount(len(pnl))
        for r, row in enumerate(pnl):
            for c, v in enumerate([row["symbol"], f"{row['gross_profit']:.2f}", f"{row['gross_loss']:.2f}",
                                   f"{row['net']:.2f}", f"{row['swap']:.2f}", f"{row['margin']:.2f}", str(row["open_positions"])]):
                self.pnl_table.setItem(r, c, QTableWidgetItem(str(v)))

        # alerts -> logs
        self._render_logs(ov.get("alerts", []))
        self.equity.push(float(acct.get("equity", 0)))

    def _render_protections(self, ps: dict) -> None:
        nf = ps.get("news_filter", {})
        if nf.get("active"):
            left = int(nf.get("seconds_left") or 0)
            self.prot_rows["News Filter"].setText(f"ACTIVE · blackout {left // 60}:{left % 60:02d} left")
            self.prot_rows["News Filter"].setStyleSheet("color: #FFB800;")
        else:
            self.prot_rows["News Filter"].setText("INACTIVE · calendar armed")
            self.prot_rows["News Filter"].setStyleSheet("color: #00F0FF;")
        be = ps.get("breakeven", {})
        self.prot_rows["Breakeven"].setText(f"trigger +{be.get('trigger_atr_mult')} ATR · {be.get('positions_armed', 0)} armed")
        sd = ps.get("spike_defence", {})
        armed = [s for s, v in (sd.get("per_symbol") or {}).items() if v.get("armed")]
        txt = f"ATR spike ×{sd.get('atr_spike_mult')} · spread ×{sd.get('spread_widen_mult')} · " + (f"ARMED: {','.join(armed)}" if armed else "all symbols OK")
        self.prot_rows["Spike Defence"].setText(txt)
        self.prot_rows["Spike Defence"].setStyleSheet("color: #FF2D55;" if armed else "color: #00F0FF;")
        tf = ps.get("thesis_failure", {})
        last = tf.get("last") or {}
        self.prot_rows["Thesis Failure"].setText(
            f"invalidations: {tf.get('invalidations_total', 0)}" + (f" · last {last.get('symbol')} @ {last.get('price'):.5f}" if last else ""))
        self.prot_rows["Thesis Failure"].setStyleSheet("color: #FFB800;" if tf.get("invalidations_total") else "color: #00F0FF;")
        if ps.get("halted"):
            self.statusBar().showMessage("⛔ TRADING HALTED — automated cycles frozen", 8000)

    def _render_monitoring(self, mon: dict) -> None:
        disp = (mon.get("dispatch") or {})
        self.mon_stats["Dispatch avg"].setText(f"{disp.get('avg_ms', 0):.2f}ms")
        self.mon_stats["Drift proposals"].setText(str(len(mon.get("proposals", []))))
        strat = mon.get("strategies") or {}
        rows = sorted(strat.items(), key=lambda kv: (kv[1].get("pnl") or 0), reverse=True)[:8]
        self.mon_table.setRowCount(len(rows))
        for r, (sid, s) in enumerate(rows):
            for c, v in enumerate([sid, str(s.get("trades", 0)), f"{(s.get('win_rate') or 0)*100:.1f}", f"{s.get('pnl') or 0:,.0f}"]):
                self.mon_table.setItem(r, c, QTableWidgetItem(str(v)))
        self.mon_props.clear()
        for p in list(mon.get("proposals", []))[-4:][::-1]:
            self.mon_props.addItem(f"⚠ drift proposal: {p.get('strategy', p.get('type'))} ({p.get('type')})")
        if not mon.get("proposals"):
            self.mon_props.addItem("no drift proposals — learning loop stable")

    def _render_logs(self, alerts: list[dict]) -> None:
        lv = self.log_filter
        self.logs_list.clear()
        rows = [a for a in alerts[-60:]][::-1]
        from PySide6.QtGui import QColor

        level_color = {"INFO": "#00F0FF", "WARNING": "#FFB800", "CRITICAL": "#FF2D55", "ERROR": "#FF2D55"}
        for a in rows:
            if lv != "ALL" and a.get("level") != lv:
                continue
            it = QListWidgetItem(f"{(a.get('ts') or '')[:19]} [{a.get('level')}] {a.get('message')}")
            it.setForeground(QColor(level_color.get(a.get("level"), "#E8EAF0")))
            self.logs_list.addItem(it)

    def _set_log_filter(self, lv: str) -> None:
        self.log_filter = lv
        for k, b in self.lv_btns.items():
            b.setChecked(k == lv)
        try:
            self._render_logs(self.facade.alerts(200))
        except Exception as _exc:
            self.statusBar().showMessage(f"⚠ alerts: {_exc}", 3000)

    def _refresh_journal(self) -> None:
        try:
            ev = self.facade.evidence(250)
        except Exception:
            return
        rows = [e for e in ev if e["kind"].startswith("journal.") or e["kind"] in ("position.closed", "risk.veto")][-40:][::-1]
        vetoes = sum(1 for e in ev if e["kind"] == "risk.veto")
        self.mon_stats["Risk vetoes"].setText(str(vetoes))
        self.journal_table.setRowCount(len(rows))
        for r, e in enumerate(rows):
            p = e.get("payload") or {}
            sym = p.get("symbol") or (p.get("intent") or {}).get("symbol") or (p.get("trade") or {}).get("symbol") or "—"
            side = p.get("side") or (p.get("intent") or {}).get("side") or (p.get("trade") or {}).get("side") or ""
            if e["kind"] in ("journal.exit", "position.closed"):
                t = p.get("trade") or p
                detail = f"exit {t.get('reason', '')} · vol {t.get('volume', '')}"
                pnl = f"{t.get('pnl', 0):.2f}" if t.get("pnl") is not None else ""
            elif e["kind"] == "journal.execution":
                i = p.get("intent") or {}
                detail = f"{i.get('order_type', '')} @ {i.get('price') or 'mkt'} · SL {i.get('stop_loss') or '—'} · TP {i.get('take_profit') or '—'}"
                pnl = ""
            elif e["kind"] == "journal.signal":
                s = p.get("ticket") or p
                detail = f"{s.get('strategy_id', '')} · {s.get('scenario', '')} · R{s.get('risk_reward', '—')}"
                pnl = ""
            else:
                detail = str(p.get("reason", ""))[:60]
                pnl = ""
            for c, v in enumerate([(e.get("ts") or "")[:19], e["kind"].replace("journal.", "J:"), str(sym), str(side),
                                   detail, pnl, (e.get("evidence_id") or "")[:10]]):
                self.journal_table.setItem(r, c, QTableWidgetItem(str(v)))

    # infra simulators (SIMULATED, labelled)
    def _tick_infra(self, feed_ticks: int) -> None:
        if not hasattr(self, "_lat"):
            self._lat = {r: 20 + random.random() * 30 for r in self.lat_labels}
            self._ticks_prev = None
        for r, lbl in self.lat_labels.items():
            self._lat[r] = max(8, min(220, self._lat[r] + (random.random() - 0.5) * 14))
            ms = self._lat[r]
            state = "OK" if ms < 60 else "SLOW" if ms < 130 else "DEGRADED"
            lbl.setText(f"{r} {ms:.0f}ms {state}")
            lbl.setStyleSheet("color: #00F0FF;" if ms < 60 else "color: #FFB800;" if ms < 130 else "color: #FF2D55;")
        rate = 0.0
        if self._ticks_prev is not None and feed_ticks is not None:
            rate = (feed_ticks - self._ticks_prev) / 0.5
        self._ticks_prev = feed_ticks
        for i, (v, lbl) in enumerate(self.ven_labels.items()):
            lbl.setText(f"{v} {rate * (1 + i * 0.13):.0f} t/s {'CONNECTED' if rate > 0 else 'STALLED'}")
            lbl.setStyleSheet("color: #00F0FF;" if rate > 0 else "color: #FF2D55;")

    def _tick_clock(self) -> None:
        ts = getattr(self, "_foot_ts", "")
        self.clock_lbl.setText(ts[11:19] if len(ts) >= 19 else datetime.now(UTC).strftime("%H:%M:%S"))

    def closeEvent(self, e) -> None:  # noqa: N802
        try:
            self.worker.request_stop()
            self.worker.wait(2000)
        except Exception:
            pass
        super().closeEvent(e)
