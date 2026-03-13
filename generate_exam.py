"""Legacy wrapper for exam generation.

Prefer: `python tools/generate_exam.py`
"""

from __future__ import annotations

from tools.generate_exam import main


if __name__ == "__main__":
    print("[DEPRECATED] Use: python tools/generate_exam.py")
    raise SystemExit(main())
