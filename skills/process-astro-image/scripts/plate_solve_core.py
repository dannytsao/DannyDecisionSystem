#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

# ─── How to run ───
# This module is imported by plate_solve_tiles.py; run that CLI instead.
# ──────────────────

# ruff: noqa: CPY001, RUF001

"""Typed Siril plate-solving primitives shared by the CLI and tests."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Final

DEFAULT_SIRIL_CLI: Final = Path("/Applications/Siril.app/Contents/MacOS/siril-cli")
DEFAULT_FOCAL_MM: Final = 250.0
DEFAULT_PIXEL_SIZE_UM: Final = 2.9
DEFAULT_TIMEOUT_SECONDS: Final = 180
_SEXAGESIMAL_PARTS: Final = 3
_RESOLUTION: Final = re.compile(r"Resolution:\s+([0-9.]+)\s+arcsec/px")
_CENTER: Final = re.compile(
    r"Image center:\s+alpha:\s+([0-9 ]+\.[0-9]+),\s+delta:\s+([+-]?[0-9 ]+\.[0-9]+)",
)


@dataclass(frozen=True, slots=True)
class PlateSolution:
    """Parsed result of one Siril plate-solve operation."""

    succeeded: bool
    resolution_arcsec_per_pixel: float | None
    center_ra_deg: float | None
    center_dec_deg: float | None


@dataclass(frozen=True, slots=True)
class TilePlateSolve:
    """Machine-readable plate-solve result for one tile."""

    tile_id: str
    input_path: str
    output_path: str
    status: str
    resolution_arcsec_per_pixel: float | None
    center_ra_deg: float | None
    center_dec_deg: float | None
    error: str | None


class PlateSolveInputError(ValueError):
    """Report missing or malformed plate-solve input metadata."""

    def __init__(self, reason: str) -> None:
        """Store a user-readable diagnostic."""
        self.reason = reason
        super().__init__(reason)

    def __str__(self) -> str:
        """Return the diagnostic for reports."""
        return self.reason


class PlateSolveExecutionError(RuntimeError):
    """Report a Siril plate-solve failure."""

    def __init__(self, reason: str) -> None:
        """Store a user-readable diagnostic."""
        self.reason = reason
        super().__init__(reason)

    def __str__(self) -> str:
        """Return the diagnostic for reports."""
        return self.reason


@dataclass(frozen=True, slots=True)
class SolveConfig:
    """Immutable settings shared by all tile solve operations."""

    executable: Path
    log_dir: Path
    focal_mm: float
    pixel_size_um: float
    timeout_seconds: int


def _sexagesimal(value: str, *, right_ascension: bool) -> float:
    parts = value.split()
    if len(parts) != _SEXAGESIMAL_PARTS:
        reason = f"無法解析 Siril 座標：{value}"
        raise PlateSolveInputError(reason)
    sign = -1 if parts[0].startswith("-") else 1
    hours = abs(float(parts[0]))
    result = hours + float(parts[1]) / 60 + float(parts[2]) / 3600
    return sign * result * (15 if right_ascension else 1)


def parse_plate_solve_log(log: str) -> PlateSolution:
    """Extract success, image resolution, and center from Siril output."""
    resolution_match = _RESOLUTION.search(log)
    center_match = _CENTER.search(log)
    failed = "Plate solving failed" in log or "Script execution failed" in log
    return PlateSolution(
        succeeded=bool(resolution_match and center_match and not failed),
        resolution_arcsec_per_pixel=(
            float(resolution_match.group(1)) if resolution_match else None
        ),
        center_ra_deg=(
            _sexagesimal(center_match.group(1), right_ascension=True)
            if center_match
            else None
        ),
        center_dec_deg=(
            _sexagesimal(center_match.group(2), right_ascension=False)
            if center_match
            else None
        ),
    )


def _tile_center(tile_dir: Path) -> tuple[float, float]:
    payload = json.loads((tile_dir / "manifest.json").read_text(encoding="utf-8"))
    records = payload.get("files", [])
    metadata = records[0].get("metadata", {}) if records else {}
    ra = metadata.get("ra_deg")
    dec = metadata.get("dec_deg")
    if not isinstance(ra, (int, float)) or not isinstance(dec, (int, float)):
        reason = f"tile 缺少 RA/DEC：{tile_dir / 'manifest.json'}"
        raise PlateSolveInputError(reason)
    return float(ra), float(dec)


def build_plate_solve_script(
    tile_dir: Path,
    *,
    focal_mm: float = DEFAULT_FOCAL_MM,
    pixel_size_um: float = DEFAULT_PIXEL_SIZE_UM,
) -> str:
    """Build a Siril script that saves WCS to a separate FITS file."""
    ra, dec = _tile_center(tile_dir)
    return (
        "requires 1.4.0\n"
        "load 'result_linear.fit'\n"
        f"platesolve {ra:.6f},{dec:.6f} -focal={focal_mm:.3f} "
        f"-pixelsize={pixel_size_um:.3f} -downscale -noflip\n"
        "save 'plate_solved.fit'\n"
        "close\n"
    )


def resolve_siril(path: Path | None) -> Path:
    """Resolve the Siril executable or raise an input error."""
    if path is not None and path.is_file():
        return path
    if path is None and DEFAULT_SIRIL_CLI.is_file():
        return DEFAULT_SIRIL_CLI
    requested = path or DEFAULT_SIRIL_CLI
    reason = f"找不到 siril-cli：{requested}"
    raise PlateSolveInputError(reason)


def run_tile(tile_dir: Path, config: SolveConfig) -> TilePlateSolve:
    """Run Siril for one tile and save a separate WCS FITS."""
    script = build_plate_solve_script(
        tile_dir, focal_mm=config.focal_mm, pixel_size_um=config.pixel_size_um,
    )
    try:
        result = subprocess.run(  # noqa: S603 - executable path is resolved
            [str(config.executable), "-d", str(tile_dir), "-s", "-"],
            input=script,
            capture_output=True,
            check=False,
            text=True,
            timeout=config.timeout_seconds,
        )
    except subprocess.TimeoutExpired as error:
        reason = f"{tile_dir.name} plate solving 超過 {config.timeout_seconds} 秒"
        raise PlateSolveExecutionError(reason) from error
    log = f"{result.stdout}\n{result.stderr}"
    (config.log_dir / f"{tile_dir.name}.log").write_text(log, encoding="utf-8")
    solution = parse_plate_solve_log(log)
    output = tile_dir / "plate_solved.fit"
    if result.returncode != 0 or not solution.succeeded or not output.is_file():
        detail = log.strip()[-1000:] or "沒有 Siril 診斷訊息"
        reason = f"{tile_dir.name}：{detail}"
        raise PlateSolveExecutionError(reason)
    return TilePlateSolve(
        tile_id=tile_dir.name,
        input_path=str(tile_dir / "result_linear.fit"),
        output_path=str(output),
        status="通過",
        resolution_arcsec_per_pixel=solution.resolution_arcsec_per_pixel,
        center_ra_deg=solution.center_ra_deg,
        center_dec_deg=solution.center_dec_deg,
        error=None,
    )


def run_tile_safely(tile_dir: Path, config: SolveConfig) -> TilePlateSolve:
    """Convert one tile execution error into a reportable result row."""
    try:
        return run_tile(tile_dir, config)
    except (OSError, PlateSolveInputError, PlateSolveExecutionError) as error:
        return TilePlateSolve(
            tile_id=tile_dir.name,
            input_path=str(tile_dir / "result_linear.fit"),
            output_path="",
            status="失敗",
            resolution_arcsec_per_pixel=None,
            center_ra_deg=None,
            center_dec_deg=None,
            error=str(error),
        )
