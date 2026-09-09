# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for preparing an IRCUT mosaic dry-run."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "prepare_mosaic_run", SCRIPT_DIR / "prepare_mosaic_run.py",
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _write_plate_results(root: Path) -> Path:
    """Create a plate-solve result index with IRCUT, LP, and failed rows."""
    source_root = root / "tiles"
    source_root.mkdir()
    rows = []
    for tile_id, status in (
        ("2025-10-04_IRCUT_tile-01", "通過"),
        ("2024-11-28_LP_tile-01", "通過"),
        ("2024-11-28_IRCUT_tile-06", "失敗"),
    ):
        tile = source_root / tile_id
        tile.mkdir()
        solved = tile / "plate_solved.fit"
        solved.write_bytes(b"FITS")
        rows.append(
            {
                "tile_id": tile_id,
                "output_path": str(solved),
                "status": status,
            },
        )
    (source_root / "qa").mkdir()
    (source_root / "qa" / "plate-solve.json").write_text(
        json.dumps(rows), encoding="utf-8",
    )
    return source_root


def test_prepare_mosaic_run_keeps_only_solved_ircuts(tmp_path: Path) -> None:
    """Given mixed plate results, preparation links only solved IRCUT tiles."""
    source_root = _write_plate_results(tmp_path)
    output_root = tmp_path / "mosaic"

    result = MODULE.prepare_mosaic_run(source_root, output_root)

    assert result.input_count == 1
    link = next((output_root / "Lights").iterdir())
    assert link.is_symlink()
    assert link.resolve().name == "plate_solved.fit"
    assert "stack r_tile" in result.script_path.read_text(encoding="utf-8")
    assert "LP" not in result.script_path.read_text(encoding="utf-8")
    assert result.report_path.is_file()


def test_prepare_mosaic_run_rejects_nonempty_output(tmp_path: Path) -> None:
    """Given an existing output, preparation refuses to overwrite it."""
    source_root = _write_plate_results(tmp_path)
    output_root = tmp_path / "mosaic"
    output_root.mkdir()
    (output_root / "existing.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(MODULE.MosaicPreparationError, match="not empty"):
        MODULE.prepare_mosaic_run(source_root, output_root)
