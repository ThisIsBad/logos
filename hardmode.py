"""Legacy wrapper for hardmode generation.

Prefer: `python tools/generate_hardmode.py`
"""

from __future__ import annotations

from tools.generate_hardmode import main


if __name__ == "__main__":
    print("[DEPRECATED] Use: python tools/generate_hardmode.py")
    raise SystemExit(main())
