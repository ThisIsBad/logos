"""Module entrypoint for `python -m logic_brain`."""

from __future__ import annotations

import sys

from logic_brain.cli import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
