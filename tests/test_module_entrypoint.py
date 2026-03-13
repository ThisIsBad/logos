"""Direct coverage test for logic_brain.__main__."""

from __future__ import annotations

import runpy
import sys

import pytest


def test_module_entrypoint_calls_cli_main(monkeypatch):
    called: dict[str, object] = {}

    def _fake_main(argv: list[str]) -> int:
        called["argv"] = argv
        return 7

    monkeypatch.setattr("logic_brain.cli.main", _fake_main)
    monkeypatch.setattr(sys, "argv", ["logic_brain", "P |- P"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("logic_brain", run_name="__main__")

    assert exc_info.value.code == 7
    assert called["argv"] == ["P |- P"]
