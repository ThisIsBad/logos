"""Legacy wrapper for stress result checking.

Prefer: `python tools/check_stress_results.py`
"""

from __future__ import annotations

from tools.check_stress_results import main


if __name__ == "__main__":
    print("[DEPRECATED] Use: python tools/check_stress_results.py")
    raise SystemExit(main())
