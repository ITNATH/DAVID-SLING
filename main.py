"""DAVID SLING IATOS - single production application entry point.

Boots the David OS (integrity verify -> configuration -> evidence ledger ->
data feed -> decision pipeline -> execution boundary), then starts the Phase 1
web application (FastAPI ASGI + telemetry WebSockets) and the operator UI.

Usage:
    python main.py --mode sim --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

from david_sling import __version__
from david_sling.bootstrap.david_os_boot import DavidOSBoot


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="DAVID SLING", description="DAVID SLING IATOS boot")
    parser.add_argument("--mode", choices=["sim", "live", "backtest"], default="sim")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--api-only", action="store_true", help="boot core + API, no GUI")
    return parser.parse_args(argv)


async def amain() -> int:
    args = parse_args()
    print(f"DAVID SLING IATOS v{__version__} - booting David OS ...")
    if args.mode == "sim":
        # simulated sessions always start from a clean evidence ledger
        ledger_path = os.environ.get("DAVID_SLING_LEDGER_PATH", "storage/audit/evidence_ledger.jsonl")
        if os.path.exists(ledger_path):
            os.remove(ledger_path)
    boot = DavidOSBoot(mode=args.mode)
    runtime = await boot.run()
    print("DAVID SLING - boot OK:", runtime.status_summary())
    from david_sling.api.app import serve

    await serve(runtime, host=args.host, port=args.port)
    return 0


def main() -> int:
    try:
        return asyncio.run(amain())
    except KeyboardInterrupt:
        print("DAVID SLING - halted by operator.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
