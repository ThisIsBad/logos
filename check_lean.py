"""Legacy wrapper for Lean result checking.

Prefer: python tools/check_lean_results.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).with_name("tools") / "check_lean_results.py"
    print("[deprecated] Use `python tools/check_lean_results.py` instead.")
    result = subprocess.run([sys.executable, str(script), *sys.argv[1:]])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
