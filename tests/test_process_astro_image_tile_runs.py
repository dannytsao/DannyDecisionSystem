# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for preparing isolated tile runs."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "prepare_tile_runs",
    SCRIPT_DIR / "prepare_tile_runs.py",
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
EXPECTED_FIRST_GROUP_FRAMES = 2


def _fits_bytes(*, date: str, ra: float, dec: float, filter_name: str) -> bytes:
    """Build a small FITS header with grouping metadata."""
    cards = [
        "SIMPLE  =                    T",
        "BITPIX  =                   16",
        "NAXIS   =                    2",
        "NAXIS1  =                    2",
        "NAXIS2  =                    2",
        "BAYERPAT= 'GRBG    '",
        f"FILTER  = '{filter_name:<8}'",
        f"DATE-OBS= '{date}T12:00:00'",
        f"RA      = {ra:20.6f}",
        f"DEC     = {dec:20.6f}",
        "END",
    ]
    header = b"".join(card.ljust(80).encode("ascii") for card in cards)
    return header.ljust(2880, b" ") + b"\0" * 16


def test_prepare_tile_runs_creates_separate_symlinked_runs(tmp_path: Path) -> None:
    """Given mixed views, preparation creates isolated reviewable tile runs."""
    input_root = tmp_path / "input"
    lights = input_root / "Lights"
    lights.mkdir(parents=True)
    (lights / "a.fit").write_bytes(
        _fits_bytes(date="2025-10-04", ra=12.0, dec=41.0, filter_name="IRCUT"),
    )
    (lights / "b.fit").write_bytes(
        _fits_bytes(date="2025-10-04", ra=12.1, dec=41.05, filter_name="IRCUT"),
    )
    (lights / "c.fit").write_bytes(
        _fits_bytes(date="2025-10-04", ra=9.5, dec=41.0, filter_name="IRCUT"),
    )

    output_root = tmp_path / "runs"
    groups = MODULE.prepare_tile_runs(input_root, output_root, view_radius_deg=0.25)

    assert [path.name for path in groups] == [
        "2025-10-04_IRCUT_tile-01",
        "2025-10-04_IRCUT_tile-02",
    ]
    assert len(list((groups[0] / "Lights").iterdir())) == EXPECTED_FIRST_GROUP_FRAMES
    assert len(list((groups[1] / "Lights").iterdir())) == 1
    assert (output_root / "groups.json").is_file()
    assert (output_root / "2025-10-04_IRCUT_tile-01.ssf").is_file()
