"""Round-13: PySide6 desktop command center - offscreen wiring tests.

Skipped automatically when PySide6 is not installed (headless CI without GUI
deps); with PySide6 present they run with QT_QPA_PLATFORM=offscreen and verify
every binding: KPI refresh, engine toggle, single-trade button -> facade,
batch buttons, panic/halt/resume, journal/logs render, theme/QSS swap, globe
paint, and the MT5 worker sim fallback.
"""
from __future__ import annotations

import asyncio
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pyside = pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(scope="module")
def facade(tmp_path_factory):
    os.environ["DAVID_SLING_LEDGER_PATH"] = str(tmp_path_factory.mktemp("led") / "evidence_ledger.jsonl")
    from david_sling.bootstrap.david_os_boot import DavidOSBoot

    rt = asyncio.run(DavidOSBoot(mode="sim").run(feed=True))
    asyncio.run(asyncio.sleep(2.0))
    from david_sling.application.facade import ServiceFacade

    yield ServiceFacade(rt)
    asyncio.run(rt.stop())



def _pump(qapp, win, cond, tries=60):
    """Process Qt events so cross-thread worker signals are delivered."""
    import time

    for _ in range(tries):
        qapp.processEvents()
        if cond():
            return True
        time.sleep(0.05)
        qapp.processEvents()
    return cond()

@pytest.fixture()
def win(qapp, facade):
    from david_sling.application.desktop.main_window import MainWindow

    w = MainWindow(facade, mode="sim")
    w.show()
    yield w
    w.close()


def test_window_builds_and_refreshes(qapp, win, facade):
    win.refresh()
    assert win.kpis["Balance"].text() != "—"
    assert len(win.health_cells) >= 15 or win.health_grid.count() >= 15
    assert win.symbol_combo.count() >= 7  # incl. V75/V25/STEP
    assert set(win.engine_rows) == {"A", "B", "C", "D", "G"}


def test_qss_themes(qapp, win):
    from david_sling.application.desktop.qss import stylesheet

    dark = stylesheet("dark")
    light = stylesheet("light")
    assert "#000000" in dark and "#00F0FF" in dark and "#FF2D55" in dark
    assert "#FFFFFF" in light
    win.apply_theme("light")
    assert "#FFFFFF" in win.styleSheet()
    win.apply_theme("dark")
    assert "#000000" in win.styleSheet()


def test_single_trade_button_wired(qapp, win, facade):
    win.t_symbol.setCurrentText("EURUSD")
    win.t_side.setCurrentText("BUY")
    win.t_vol.setValue(0.01)
    win._cmd_open()
    assert _pump(qapp, win, lambda: win.trade_result.text().startswith("[single]"))
    assert win.trade_result.text().startswith("[single]")
    assert '"ok": true' in win.trade_result.text() or '"ok":true' in win.trade_result.text()


def test_batch_buttons_wired(qapp, win):
    win._cmd_batch({"only_losing": True})
    assert _pump(qapp, win, lambda: win.trade_result.text().startswith("[batch_close]"))
    assert '"closed"' in win.trade_result.text()


def test_panic_halt_resume(qapp, win):
    win.worker.panic()
    assert _pump(qapp, win, lambda: "flattened" in win.trade_result.text())
    win.worker.halt("test halt")
    assert _pump(qapp, win, lambda: win.facade.protection_status()["halted"] is True)
    win.worker.resume()
    assert _pump(qapp, win, lambda: win.facade.protection_status()["halted"] is False)


def test_engine_toggle_wired(qapp, win, facade):
    cb = win.engine_rows["G"]
    cb.setChecked(False)
    assert _pump(qapp, win, lambda: facade.engines_status()["engines"]["G"]["enabled"] is False)
    cb.setChecked(True)
    assert _pump(qapp, win, lambda: facade.engines_status()["engines"]["G"]["enabled"] is True)


def test_protection_indicators(qapp, win):
    win._render_protections(win.facade.protection_status())
    assert "News Filter" in win.prot_rows and win.prot_rows["News Filter"].text()
    assert "+1.5 ATR" in win.prot_rows["Breakeven"].text()
    assert "ATR spike" in win.prot_rows["Spike Defence"].text()
    assert "invalidations" in win.prot_rows["Thesis Failure"].text()


def test_journal_and_logs(qapp, win):
    win._refresh_journal()
    assert win.journal_table.columnCount() == 7
    win._render_logs(win.facade.alerts(50))
    assert win.logs_list.count() >= 0
    win._set_log_filter("WARNING")
    assert win.log_filter == "WARNING"


def test_globe_paint_all_modes(qapp, win):
    for m in ("globe", "heatmap", "routes"):
        win._set_globe_mode(m)
        assert win.globe.mode == m
        win.globe.grab()  # forces a paint; must not raise


def test_mt5_worker_sim_fallback(qapp, facade):
    from david_sling.application.desktop.mt5_worker import Mt5Worker

    w = Mt5Worker(facade)
    states = []
    w.connected.connect(lambda ok, info: states.append((ok, info)))
    w.start()
    assert _pump(qapp, None, lambda: bool(states))
    w.request_stop()
    w.wait(3000)
    assert states and "SIMULATED" in states[0][1]


def test_mt5_adapter_contract_without_terminal():
    """Mt5Adapter must raise ExecutionError (never silently drop) when the
    MetaTrader5 package/terminal is unavailable - bulletproof connect()."""
    from david_sling.broker.mt5_adapter import Mt5Adapter
    from david_sling.core.errors import ExecutionError, SecurityError

    ad = Mt5Adapter({}, {"type": "mt5"})  # no credentials
    with pytest.raises((ExecutionError, SecurityError)):
        ad.connect()
    with pytest.raises(ExecutionError):
        ad.reconcile()
