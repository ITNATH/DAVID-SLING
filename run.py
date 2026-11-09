"""DAVID SLING - local developer launcher.

Modes:
    live       boot core + web API against the configured broker bridge
    sim        boot core + web API on the deterministic synthetic market feed
    api        API only (no market feed; telemetry reflects idle system)
    scan       run the initial bot-on / pre-market scan and print a report
    backtest   deterministic replay over generated historical data, prints results
    diag       boot diagnostics (architecture audit, config, ledger continuity)
    gui        PySide6 desktop command center (Milestone B, QSS, MT5-ready)
"""
from __future__ import annotations

import argparse
import asyncio
import sys


def _gui(args) -> int:
    import desktop

    return desktop.launch("sim" if args.sim or args.mode == "gui" else "live")


def main() -> int:
    parser = argparse.ArgumentParser(prog="run.py", description="DAVID SLING launcher")
    parser.add_argument("mode", choices=["live", "sim", "api", "scan", "backtest", "diag", "gui"])
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--days", type=int, default=30, help="backtest length in days")
    parser.add_argument("--sim", action="store_true", help="force synthetic feed for live mode")
    args = parser.parse_args()

    from src.david_sling.bootstrap.david_os_boot import DavidOSBoot

    if args.mode == "gui":
        return _gui(args)
    if args.mode in {"live", "sim", "api"}:
        mode = "sim" if (args.mode == "sim" or args.sim) else ("sim" if args.mode == "api" else "live")
        from src.david_sling.api.app import serve

        async def go() -> int:
            runtime = await DavidOSBoot(mode=mode).run()
            print("DAVID SLING - boot OK:", runtime.status_summary())
            await serve(runtime, host=args.host, port=args.port)
            return 0

        try:
            return asyncio.run(go())
        except KeyboardInterrupt:
            return 0

    if args.mode == "scan":
        runtime = asyncio.run(DavidOSBoot(mode="sim").run(scan=True))
        print(runtime.scan_report())
        return 0

    if args.mode == "backtest":
        from david_sling.data.replay.replay_engine import ReplayEngine

        async def factory(mode: str):
            return await DavidOSBoot(mode=mode).run(feed=False, loops=False)

        result = asyncio.run(ReplayEngine(days=args.days).run(runtime_factory=factory))
        print(result.summary())
        return 0

    if args.mode == "diag":
        from scripts.architecture_audit import run_audit

        ok = run_audit()
        return 0 if ok else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
