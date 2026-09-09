# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for mosaic output quality gates."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "mosaic_qa", SCRIPT_DIR / "mosaic_qa.py",
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
EXPECTED_TOTAL_TILES = 4
EXPECTED_SELECTED_TILES = 2


def test_build_mosaic_qa_detects_registration_quality_failure(tmp_path: Path) -> None:
    """Given a mosaic sequence with few selected tiles, QA fails closed."""
    process = tmp_path / "process"
    process.mkdir()
    (process / "tile_.seq").write_text(
        "S 'tile_' 1 4 2 5 1 6 0 0 0\nI 1 1\nI 2 0\nI 3 1\nI 4 0\n",
        encoding="utf-8",
    )
    (tmp_path / "mosaic-input.json").write_text(
        json.dumps(
            {
                "inputs": [
                    {"tile_id": f"tile-{i}", "link": f"tile_{i:04d}.fit"}
                    for i in range(1, 5)
                ],
            },
        ),
        encoding="utf-8",
    )
    (tmp_path / "result_mosaic.fit").write_bytes(b"FITS")
    (tmp_path / "result_mosaic.dng").write_bytes(b"DNG")

    result = MODULE.build_mosaic_qa(tmp_path, threshold=0.8)

    assert result.total_tiles == EXPECTED_TOTAL_TILES
    assert result.selected_tiles == EXPECTED_SELECTED_TILES
    assert result.status == "失敗"
    assert result.rejected_tiles == ("tile-2", "tile-4")
