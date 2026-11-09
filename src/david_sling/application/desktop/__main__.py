"""Module entry: python -m david_sling.application.desktop

The boot/launch logic lives in the repo-root `desktop.py` so the `application`
domain never imports `bootstrap` (zero-circular architecture law). This shim
delegates to it when run from the repository root.
"""
from __future__ import annotations

import sys


def main() -> int:
    try:
        import desktop  # repo-root entry point
    except ImportError:
        print("run from the repository root:  python desktop.py [--mode sim|live]")
        return 2
    return desktop.main()


if __name__ == "__main__":
    sys.exit(main())
