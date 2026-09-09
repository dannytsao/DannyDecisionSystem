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
#      uv run export_dng_sidecars.py OUTPUT_DIR [--siril-cli PATH] [--dnglab PATH]
# 3. Or make executable and run:
#      chmod +x export_dng_sidecars.py && ./export_dng_sidecars.py OUTPUT_DIR
# ──────────────────

# ruff: noqa: CPY001, EM101

"""Create validated DNG companions for every result FITS output."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from failure_report import write_failed_report

DEFAULT_SIRIL_CLI = Path("/Applications/Siril.app/Contents/MacOS/siril-cli")


class DngExportError(RuntimeError):
    """Report a DNG companion failure at the CLI boundary."""

    def __init__(self, code: str, reason: str) -> None:
        """Initialize a typed failure with a stable code and reason."""
        self.code = code
        self.reason = reason
        super().__init__(f"DNG export failed [{code}]: {reason}")


def dng_sidecar_path(fit_path: Path) -> Path:
    """Map a result FITS path to its same-stem DNG companion."""
    return fit_path.with_suffix(".dng")


def result_fits(output_root: Path) -> tuple[Path, ...]:
    """Return result FITS files in deterministic order."""
    return tuple(
        sorted(path for path in output_root.glob("result*.fit") if path.is_file()),
    )


def missing_dng_outputs(output_root: Path) -> tuple[Path, ...]:
    """Return result DNG paths that are absent beside their FITS outputs."""
    return tuple(
        dng_path
        for fit_path in result_fits(output_root)
        if not (dng_path := dng_sidecar_path(fit_path)).is_file()
    )


def _find_tool(explicit: Path | None, name: str) -> Path:
    if explicit is not None:
        if explicit.is_file():
            return explicit
        raise DngExportError("tool_missing", f"{name} not found at {explicit}")
    resolved = shutil.which(name)
    if resolved is None and name == "siril-cli" and DEFAULT_SIRIL_CLI.is_file():
        return DEFAULT_SIRIL_CLI
    if resolved is None:
        raise DngExportError("tool_missing", f"{name} is not available on PATH")
    return Path(resolved)


def _run_siril_export(
    siril: Path,
    output_root: Path,
    fit_path: Path,
    ppm_path: Path,
) -> None:
    ppm_name = ppm_path.with_suffix("").relative_to(output_root).as_posix()
    script = (
        "requires 1.4.0\n"
        f"load '{fit_path.name}'\n"
        f"savepnm '{ppm_name}'\n"
        "close\n"
    )
    result = subprocess.run(  # noqa: S603 - tool path is explicitly resolved
        [str(siril), "-d", str(output_root), "-s", "-"],
        input=script,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0 or not ppm_path.is_file():
        detail = (result.stderr or result.stdout).strip()[-800:]
        raise DngExportError("siril_export", detail or "Siril did not create PPM")


def _run_dnglab(dnglab: Path, ppm_path: Path, dng_path: Path) -> None:
    result = subprocess.run(  # noqa: S603 - tool path is explicitly resolved
        [
            str(dnglab),
            "makedng",
            "--input",
            str(ppm_path),
            "--output",
            str(dng_path),
            "--map",
            "0:raw",
            "--dng-backward-version",
            "1.4",
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0 or not dng_path.is_file():
        detail = (result.stderr or result.stdout).strip()[-800:]
        raise DngExportError("dnglab_export", detail or "DNGLab did not create DNG")
    _validate_dng(dnglab, dng_path)


def _validate_dng(dnglab: Path, dng_path: Path) -> None:
    """Verify a DNG has readable structure and a DNGVersion tag."""
    structure = subprocess.run(  # noqa: S603 - tool path is explicitly resolved
        [str(dnglab), "analyze", "--structure", str(dng_path)],
        capture_output=True,
        check=False,
        text=True,
    )
    if structure.returncode != 0 or '"50706"' not in structure.stdout:
        raise DngExportError(
            "dng_validation", "DNGVersion tag is missing or unreadable",
        )


def export_dng_sidecars(
    output_root: Path,
    *,
    siril_cli: Path | None = None,
    dnglab: Path | None = None,
) -> tuple[Path, ...]:
    """Export and validate one DNG companion for every result FITS file."""
    if not output_root.is_dir():
        raise DngExportError("output_root", f"directory does not exist: {output_root}")
    fits = result_fits(output_root)
    if not fits:
        raise DngExportError("no_results", "no result*.fit files found")
    siril = _find_tool(siril_cli, "siril-cli")
    converter = _find_tool(dnglab, "dnglab")
    generated: list[Path] = []
    for fit_path in fits:
        dng_path = dng_sidecar_path(fit_path)
        if dng_path.exists():
            _validate_dng(converter, dng_path)
            generated.append(dng_path)
            continue
        with tempfile.TemporaryDirectory(
            prefix=".dds-dng-", dir=output_root,
        ) as temp_dir:
            ppm_path = Path(temp_dir) / "converted.ppm"
            _run_siril_export(siril, output_root, fit_path, ppm_path)
            _run_dnglab(converter, ppm_path, dng_path)
        generated.append(dng_path)
    return tuple(generated)


def main(
    output_root: Path,
    siril_cli: Path | None = None,
    dnglab: Path | None = None,
) -> None:
    """Export DNG companions and emit a failed report on any error."""
    import typer  # noqa: PLC0415 - optional CLI dependency loaded only at boundary

    try:
        generated = export_dng_sidecars(
            output_root,
            siril_cli=siril_cli,
            dnglab=dnglab,
        )
    except (DngExportError, OSError) as error:
        report = write_failed_report(
            output_root / "failed-report.md",
            operation="export_dng_sidecars",
            reason=str(error),
            input_root=output_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(f"DNG sidecars ready: {', '.join(str(path) for path in generated)}")


if __name__ == "__main__":
    import typer

    typer.run(main)
