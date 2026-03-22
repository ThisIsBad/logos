"""Check experiment result files for Stage 4 validation runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


RESULTS_DIR = Path("results")


def _load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Experiment result must be a JSON object: {path}")
    return {str(key): value for key, value in data.items()}


def _require_number(payload: dict[str, object], key: str) -> float:
    value = payload.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"Field '{key}' must be numeric")
    return float(value)


def _require_int(payload: dict[str, object], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Field '{key}' must be an integer")
    return value


def _memory_consistency_paths() -> tuple[Path, Path, Path]:
    return (
        RESULTS_DIR / "experiment_memory_scale.json",
        RESULTS_DIR / "experiment_contradiction_detection.json",
        RESULTS_DIR / "experiment_mixed_accumulation.json",
    )


def _check_memory_consistency() -> int:
    scale_path, contradiction_path, mixed_path = _memory_consistency_paths()
    for path in (scale_path, contradiction_path, mixed_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing experiment result file: {path}")

    scale = _load_json(scale_path)
    contradictions = _load_json(contradiction_path)
    mixed = _load_json(mixed_path)

    rows = [
        (
            "scale_wall_time<30s",
            _require_number(scale, "wall_time_seconds") < 30.0,
            f"wall_time={_require_number(scale, 'wall_time_seconds'):.3f}s",
        ),
        (
            "detected==injected",
            _require_int(contradictions, "detected_contradictions")
            == _require_int(contradictions, "injected_contradictions"),
            (
                f"detected={_require_int(contradictions, 'detected_contradictions')} "
                f"injected={_require_int(contradictions, 'injected_contradictions')}"
            ),
        ),
        (
            "false_positives==0",
            _require_int(contradictions, "false_positives") == 0,
            f"false_positives={_require_int(contradictions, 'false_positives')}",
        ),
        (
            "false_negatives==0",
            _require_int(contradictions, "false_negatives") == 0,
            f"false_negatives={_require_int(contradictions, 'false_negatives')}",
        ),
        (
            "mixed_counts_match",
            _require_int(mixed, "expected_valid") == _require_int(mixed, "actual_valid")
            and _require_int(mixed, "expected_invalid") == _require_int(mixed, "actual_invalid"),
            (
                f"valid={_require_int(mixed, 'actual_valid')}/{_require_int(mixed, 'expected_valid')} "
                f"invalid={_require_int(mixed, 'actual_invalid')}/{_require_int(mixed, 'expected_invalid')}"
            ),
        ),
    ]

    print("check                        status   details")
    print("-------------------------------------------------------------")
    failures = 0
    for name, ok, detail in rows:
        print(f"{name:28s} {'PASS' if ok else 'FAIL':6s} {detail}")
        failures += int(not ok)
    return 0 if failures == 0 else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check experiment result files")
    parser.add_argument(
        "experiment",
        choices=["memory_consistency"],
        help="Experiment family to validate",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.experiment == "memory_consistency":
        return _check_memory_consistency()
    raise ValueError(f"Unsupported experiment '{args.experiment}'")


if __name__ == "__main__":
    raise SystemExit(main())
