"""DAVID SLING IATOS - desktop (PySide6) entry point, Milestone B.

    python desktop.py [--mode sim|live]

Boots the David OS runtime on a persistent background event loop (sim feed by
default; live uses the MT5 broker adapter with DAVID_SLING_MT5_* credentials),
then opens the PySide6 command center. Pure Python + QSS only.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import threading


def launch(mode: str = "sim") -> int:
    from PySide6.QtWidgets import QApplication

    from david_sling.application.desktop.main_window import MainWindow
    from david_sling.application.facade import ServiceFacade
    from david_sling.bootstrap.david_os_boot import DavidOSBoot

    loop = asyncio.new_event_loop()

    def _rt_loop() -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    threading.Thread(target=_rt_loop, daemon=True, name="david-sling-runtime-loop").start()
    runtime = asyncio.run_coroutine_threadsafe(DavidOSBoot(mode=mode).run(feed=True), loop).result(timeout=120)
    facade = ServiceFacade(runtime)
    app = QApplication.instance() or QApplication(sys.argv)
    win = MainWindow(facade, mode=mode, loop=loop)
    win.show()
    rc = app.exec()
    asyncio.run_coroutine_threadsafe(runtime.stop(), loop).result(timeout=30)
    loop.call_soon_threadsafe(loop.stop)
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(prog="david-sling-desktop")
    parser.add_argument("--mode", choices=["sim", "live"], default="sim")
    return launch(parser.parse_args().mode)


if __name__ == "__main__":
    sys.exit(main())
