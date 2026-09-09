#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "typer",
# ]
# ///

# ─── How to run ───
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run directly (no venv, no pip install needed):
#      uv run generate_siril_script.py SESSION_DIR [--output SCRIPT.ssf]
# 3. Or make executable and run:
#      chmod +x generate_siril_script.py && ./generate_siril_script.py SESSION_DIR
# ──────────────────

# ruff: noqa: CPY001, EM101

"""Generate a conservative, non-executable Siril script from a session manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from build_manifest import (
    FrameKind,
    ManifestInputError,
    SessionManifest,
    build_manifest,
)
from failure_report import write_failed_report


@dataclass(frozen=True)
class RecipeGenerationError(Exception):
    """Report why a Siril recipe cannot be generated safely."""

    code: str
    reason: str

    def __str__(self) -> str:
        """Return a stable failure summary for the CLI boundary."""
        return f"cannot generate Siril recipe [{self.code}]: {self.reason}"


def _generation_error(code: str, reason: str) -> RecipeGenerationError:
    """Create a typed generation error at a named safety boundary."""
    return RecipeGenerationError(code=code, reason=reason)


def _siril_quote(path: Path) -> str:
    """Quote an absolute path for a Siril script or reject ambiguous characters."""
    value = path.resolve().as_posix()
    if any(character in value for character in ("'", "\n", "\r")):
        raise _generation_error("unsafe_path", "path contains a quote or newline")
    return f"'{value}'"


def _single_lights_directory(manifest: SessionManifest) -> Path:
    light_paths = {
        Path(record.relative_path).parent
        for record in manifest.files
        if record.kind is FrameKind.LIGHT
    }
    if len(light_paths) != 1:
        raise _generation_error(
            "lights_directory",
            "all light frames must be in one directory for this Pilot recipe",
        )
    return next(iter(light_paths))


def _has_calibration(manifest: SessionManifest) -> bool:
    return any(
        manifest.counts[kind] > 0
        for kind in (FrameKind.DARK, FrameKind.FLAT, FrameKind.BIAS)
    )


def _osc_mode(manifest: SessionManifest) -> bool:
    light_records = (
        record for record in manifest.files if record.kind is FrameKind.LIGHT
    )
    bayer_patterns = {
        record.metadata.bayerpat
        for record in light_records
        if record.metadata is not None and record.metadata.bayerpat is not None
    }
    return bool(bayer_patterns)


def _script_lines(manifest: SessionManifest) -> tuple[str, ...]:
    root = Path(manifest.input_root)
    lights_dir = root / _single_lights_directory(manifest)
    debayer = " -debayer" if _osc_mode(manifest) else ""
    root_arg = _siril_quote(root)
    lights_arg = _siril_quote(lights_dir)
    return (
        "#!/bin/siril",
        "requires 1.4.0",
        "# DDS process-astro-image Pilot dry-run; execution_enabled=false",
        "# This file is generated for review. It is not executed by this tool.",
        f"# Input root: {root_arg}",
        "",
        f"cd {root_arg}",
        f"cd {lights_arg}",
        f"convert light -out=../process{debayer}",
        "cd ../process",
        "register light -2pass -maxstars=500 -interp=lanczos3",
        "seqapplyreg light -interp=lanczos3",
        (
            "stack r_light rej winsorized 3 3 -norm=auto "
            "-weight=wfwhm -out=../result -32b"
        ),
        "cd ..",
        "load result",
        "save result_linear",
        "autostretch",
        "save result_autostretched",
        "savepng result_preview",
        "# RC-Astro BXT/SXT/NXT and QA remain a later approved adapter step.",
        "close",
    )


def generate_script(input_root: Path, output: Path) -> Path:
    """Build and write a Siril dry-run script without invoking Siril."""
    manifest = build_manifest(input_root)
    if manifest.preflight.status == "blocked":
        reason = ", ".join(manifest.preflight.blocking_checks)
        raise _generation_error("preflight_blocked", reason)
    if any(record.metadata_status == "pending" for record in manifest.files):
        raise _generation_error(
            "raw_metadata",
            "RAW metadata is pending; only fully parsed FITS is supported",
        )
    if _has_calibration(manifest):
        raise _generation_error(
            "calibration_mapping",
            "calibration frames require an explicit mapping before generation",
        )

    destination = output.resolve()
    root = Path(manifest.input_root)
    try:
        destination.relative_to(root)
    except ValueError:
        pass
    else:
        raise _generation_error(
            "output_inside_input",
            "Siril script must be written outside the input session",
        )
    if not destination.parent.is_dir():
        raise _generation_error("output_parent", "output directory does not exist")
    if destination.exists():
        raise _generation_error(
            "output_exists",
            "refusing to overwrite an existing script",
        )

    destination.write_text("\n".join(_script_lines(manifest)) + "\n", encoding="utf-8")
    return destination


def main(input_root: Path, output: Path | None = None) -> None:
    """Generate a review-only `.ssf` file at the CLI boundary."""
    import typer  # noqa: PLC0415 - optional CLI dependency loaded only at the boundary

    destination = output or input_root.parent / f"{input_root.name}-siril-dry-run.ssf"
    try:
        generated = generate_script(input_root, destination)
    except (ManifestInputError, RecipeGenerationError) as error:
        report = write_failed_report(
            destination,
            operation="generate_siril_script",
            reason=str(error),
            input_root=input_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(f"Siril dry-run script written: {generated}")


if __name__ == "__main__":
    import typer

    typer.run(main)
