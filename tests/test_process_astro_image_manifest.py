# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for the process-astro-image Pilot intake slice."""

# Pytest assertions are the observable contract for these tests.
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).parents[1] / "skills/process-astro-image/scripts/build_manifest.py"
)
SCRIPT_DIR = SCRIPT_PATH.parent
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("build_manifest", SCRIPT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
EXPECTED_WIDTH = 2


def _fits_bytes(*, width: int = 2, height: int = 2, bitpix: int = -32) -> bytes:
    """Build the smallest valid primary-image FITS header for a fixture."""
    cards = [
        "SIMPLE  =                    T / conforms to FITS standard",
        f"BITPIX  = {bitpix:20d} / number of bits per data pixel",
        "NAXIS   =                    2 / number of data axes",
        f"NAXIS1  = {width:20d} / axis length",
        f"NAXIS2  = {height:20d} / axis length",
        "BAYERPAT= 'RGGB    '           / CFA pattern",
        "FILTER  = 'L       '           / filter name",
        "END",
    ]
    header = b"".join(card.ljust(80).encode("ascii") for card in cards)
    return header.ljust(2880, b" ") + b"\0" * 16


def test_manifest_ready_for_review_when_lights_and_calibration_are_present(
    tmp_path: Path,
) -> None:
    """Given a typed session, the manifest records hashes and a reviewable plan."""
    lights = tmp_path / "lights"
    darks = tmp_path / "darks"
    lights.mkdir()
    darks.mkdir()
    light_bytes = _fits_bytes()
    dark_bytes = _fits_bytes()
    (lights / "M31_light_001.fit").write_bytes(light_bytes)
    (darks / "master_dark_001.fit").write_bytes(dark_bytes)

    manifest = MODULE.build_manifest(tmp_path)

    assert manifest.preflight.status == "ready_for_review"
    assert manifest.counts[MODULE.FrameKind.LIGHT] == 1
    assert manifest.counts[MODULE.FrameKind.DARK] == 1
    assert manifest.files[0].sha256
    assert manifest.files[0].metadata_status == "parsed"
    assert manifest.files[0].metadata is not None
    assert manifest.files[0].metadata.width == EXPECTED_WIDTH
    assert manifest.plan.requires_approval is True
    assert manifest.plan.execution_enabled is False
    assert (lights / "M31_light_001.fit").read_bytes() == light_bytes
    assert (darks / "master_dark_001.fit").read_bytes() == dark_bytes


def test_manifest_blocks_when_no_lights_or_unknown_files_exist(tmp_path: Path) -> None:
    """Given no usable light frames, the plan blocks without inventing metadata."""
    (tmp_path / "notes.txt").write_text("not an image", encoding="utf-8")

    manifest = MODULE.build_manifest(tmp_path)

    assert manifest.preflight.status == "blocked"
    assert "has_light_frames" in manifest.preflight.blocking_checks
    assert "known_frame_types" in manifest.preflight.blocking_checks
    assert manifest.plan.execution_enabled is False


def test_manifest_blocks_invalid_fits_header(tmp_path: Path) -> None:
    """Given an invalid FITS header, preflight blocks without running tools."""
    (tmp_path / "M31_light_001.fit").write_bytes(b"not-a-fits-header")

    manifest = MODULE.build_manifest(tmp_path)

    assert manifest.preflight.status == "blocked"
    assert "fits_headers" in manifest.preflight.blocking_checks
    assert manifest.files[0].metadata_status == "invalid"
    assert manifest.plan.execution_enabled is False


def test_manifest_blocks_inconsistent_fits_dimensions(tmp_path: Path) -> None:
    """Given mismatched image dimensions, preflight blocks the session."""
    (tmp_path / "M31_light_001.fit").write_bytes(_fits_bytes(width=2))
    (tmp_path / "M31_light_002.fit").write_bytes(_fits_bytes(width=3))

    manifest = MODULE.build_manifest(tmp_path)

    assert manifest.preflight.status == "blocked"
    assert "fits_metadata_consistency" in manifest.preflight.blocking_checks


def test_manifest_ignores_macos_metadata_files(tmp_path: Path) -> None:
    """Given a macOS sidecar, intake ignores it without weakening image gates."""
    lights = tmp_path / "lights"
    lights.mkdir()
    (lights / "M106_light_001.fit").write_bytes(_fits_bytes())
    (tmp_path / ".DS_Store").write_bytes(b"macOS metadata")

    manifest = MODULE.build_manifest(tmp_path)

    assert manifest.preflight.status == "ready_for_review"
    assert len(manifest.files) == 1


def test_manifest_ignores_its_generated_json_artifact(tmp_path: Path) -> None:
    """Given a prior manifest, intake does not treat its own artifact as an image."""
    lights = tmp_path / "lights"
    lights.mkdir()
    (lights / "M106_light_001.fit").write_bytes(_fits_bytes())
    (tmp_path / "manifest.json").write_text("{}", encoding="utf-8")

    manifest = MODULE.build_manifest(tmp_path)

    assert manifest.preflight.status == "ready_for_review"
    assert len(manifest.files) == 1
