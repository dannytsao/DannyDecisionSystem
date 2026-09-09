# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for the Siril dry-run script generator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "generate_siril_script",
    SCRIPT_DIR / "generate_siril_script.py",
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _fits_bytes(*, bayerpat: str | None = "RGGB") -> bytes:
    """Build a valid FITS header for the generator fixture."""
    cards = [
        "SIMPLE  =                    T / conforms to FITS standard",
        "BITPIX  =                  -32 / number of bits per data pixel",
        "NAXIS   =                    2 / number of data axes",
        "NAXIS1  =                    2 / axis length",
        "NAXIS2  =                    2 / axis length",
    ]
    if bayerpat is not None:
        cards.append(f"BAYERPAT= '{bayerpat:<8}'           / CFA pattern")
    cards.extend(("FILTER  = 'L       '           / filter name", "END"))
    header = b"".join(card.ljust(80).encode("ascii") for card in cards)
    return header.ljust(2880, b" ") + b"\0" * 16


def test_generator_writes_conservative_osc_siril_script(tmp_path: Path) -> None:
    """Given a valid OSC session, the generator writes a non-executable script."""
    lights = tmp_path / "lights"
    lights.mkdir()
    (lights / "M31_light_001.fit").write_bytes(_fits_bytes())
    output = tmp_path.parent / "m31-dry-run.ssf"

    MODULE.generate_script(tmp_path, output)

    script = output.read_text(encoding="utf-8")
    assert "requires 1.4.0" in script
    assert "convert light -out=" in script
    assert " -debayer" in script
    assert "convert light -out=../process -debayer" in script
    assert "cd ../process" in script
    assert "-out=../result -32b" in script
    assert "register light -2pass" in script
    assert "seqapplyreg light" in script
    assert "stack r_light rej winsorized 3 3 -norm=auto" in script
    assert "execution_enabled=false" in script
    assert "siril-cli" not in script
    assert output.parent != tmp_path


def test_generator_blocks_calibration_until_mapping_is_explicit(tmp_path: Path) -> None:
    """Given calibration frames, generation blocks instead of silently ignoring them."""
    lights = tmp_path / "lights"
    darks = tmp_path / "darks"
    lights.mkdir()
    darks.mkdir()
    (lights / "M31_light_001.fit").write_bytes(_fits_bytes())
    (darks / "master_dark_001.fit").write_bytes(_fits_bytes())

    with pytest.raises(MODULE.RecipeGenerationError) as caught:
        MODULE.generate_script(tmp_path, tmp_path.parent / "blocked.ssf")
    assert caught.value.code == "calibration_mapping"


def test_generator_omits_debayer_for_mono_fits(tmp_path: Path) -> None:
    """Given a mono FITS session, the generated convert command stays mono."""
    lights = tmp_path / "lights"
    lights.mkdir()
    (lights / "M51_light_001.fit").write_bytes(_fits_bytes(bayerpat=None))
    output = tmp_path.parent / "m51-dry-run.ssf"

    MODULE.generate_script(tmp_path, output)

    convert_line = next(
        line
        for line in output.read_text(encoding="utf-8").splitlines()
        if line.startswith("convert light")
    )
    assert "-debayer" not in convert_line
