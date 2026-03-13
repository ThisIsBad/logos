"""Legacy wrapper for escalation generation.

Prefer: `python tools/generate_escalation.py`
"""

from __future__ import annotations

from tools.generate_escalation import main


if __name__ == "__main__":
    print("[DEPRECATED] Use: python tools/generate_escalation.py <round>")
    raise SystemExit(main())
