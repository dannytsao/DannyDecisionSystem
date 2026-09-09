# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for the tile plate-solving adapter."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "plate_solve_core", SCRIPT_DIR / "plate_solve_core.py",
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
EXPECTED_RESOLUTION = 2.373


def _write_tile(root: Path, tile_id: str) -> Path:
    """Create a minimal tile fixture with solve metadata and a result."""
    tile = root / tile_id
    tile.mkdir(parents=True)
    (tile / "result_linear.fit").write_bytes(b"FITS")
    (tile / "manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "metadata": {
                            "date_obs": "2025-10-04T12:00:00",
                            "filter_name": "IRCUT",
                            "ra_deg": 11.25,
                            "dec_deg": 41.75,
                            "focal_length_mm": 250.0,
                            "pixel_size_um": 2.9,
                        },
                    },
                ],
            },
        ),
        encoding="utf-8",
    )
    return tile


def test_build_plate_solve_script_preserves_input_and_writes_new_fit(
    tmp_path: Path,
) -> None:
    """Given a tile center, the generated Siril script saves a separate WCS FITS."""
    tile = _write_tile(tmp_path, "2025-10-04_IRCUT_tile-01")

    script = MODULE.build_plate_solve_script(tile)

    assert "load 'result_linear.fit'" in script
    assert "platesolve 11.250000,41.750000" in script
    assert "-focal=250.000 -pixelsize=2.900" in script
    assert "save 'plate_solved.fit'" in script


def test_parse_plate_solve_log_extracts_solution() -> None:
    """Given Siril success logs, the parser returns solved center and resolution."""
    log = """
log: Resolution:      2.373 arcsec/px
log: Image center: alpha: 00 43 21.964, delta: +41 53 6.579
log: Siril solve succeeded.
"""

    solution = MODULE.parse_plate_solve_log(log)

    assert solution.succeeded is True
    assert solution.resolution_arcsec_per_pixel == EXPECTED_RESOLUTION
    assert solution.center_ra_deg is not None
    assert solution.center_dec_deg is not None
