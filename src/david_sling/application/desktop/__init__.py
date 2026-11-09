"""L14 application/desktop - PySide6 desktop command center (Milestone B).

Pure Python + QSS only (zero HTML/JS/CSS). The shell mirrors the web command
center 1:1; every widget is bound to the ServiceFacade backend, execution runs
on the Mt5Worker thread, and the MT5 link is live when the runtime uses the
Mt5Adapter (mode=live with DAVID_SLING_MT5_* credentials), otherwise the app
runs on the SIMULATED feed with explicit provenance.

Run from the repository root:  python desktop.py [--mode sim|live]
(boot lives in root desktop.py to keep the application domain free of
bootstrap imports - zero-circular law).
"""
from __future__ import annotations

__all__ = ["MainWindow", "Mt5Worker", "stylesheet"]


def __getattr__(name: str):
    # lazy: importing this package must not require PySide6 (headless CI/gates)
    if name == "MainWindow":
        from david_sling.application.desktop.main_window import MainWindow
        return MainWindow
    if name == "Mt5Worker":
        from david_sling.application.desktop.mt5_worker import Mt5Worker
        return Mt5Worker
    if name == "stylesheet":
        from david_sling.application.desktop.qss import stylesheet
        return stylesheet
    raise AttributeError(name)
