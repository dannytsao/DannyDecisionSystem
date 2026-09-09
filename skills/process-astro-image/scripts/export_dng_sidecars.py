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

"""Create validated DNG or TIFF companions for every result FITS output."""

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


def tif_sidecar_path(fit_path: Path) -> Path:
    """Map a result FITS path to the canonical same-stem TIFF companion."""
    return fit_path.with_suffix(".tif")


def _tiff_candidates(fit_path: Path) -> tuple[Path, ...]:
    """Return accepted TIFF spellings in preference order."""
    tif_path = tif_sidecar_path(fit_path)
    return tif_path, fit_path.with_suffix(".tiff")


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


def missing_result_companions(output_root: Path) -> tuple[Path, ...]:
    """Return FITS results that have neither DNG nor TIFF companions."""
    return tuple(
        fit_path
        for fit_path in result_fits(output_root)
        if not dng_sidecar_path(fit_path).is_file()
        and not any(path.is_file() for path in _tiff_candidates(fit_path))
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


def _run_siril_tif(
    siril: Path,
    output_root: Path,
    fit_path: Path,
    tif_path: Path,
) -> Path:
    """Ask Siril for a 32-bit TIFF and return the file it actually wrote."""
    tif_name = tif_path.with_suffix("").relative_to(output_root).as_posix()
    script = (
        "requires 1.4.0\n"
        f"load '{fit_path.name}'\n"
        f"savetif32 '{tif_name}'\n"
        "close\n"
    )
    result = subprocess.run(  # noqa: S603 - tool path is explicitly resolved
        [str(siril), "-d", str(output_root), "-s", "-"],
        input=script,
        capture_output=True,
        check=False,
        text=True,
    )
    candidates = (tif_path, tif_path.with_suffix(".tiff"))
    created = next((path for path in candidates if path.is_file()), None)
    if result.returncode != 0 or created is None:
        detail = (result.stderr or result.stdout).strip()[-800:]
        raise DngExportError("tiff_export", detail or "Siril did not create TIFF")
    _validate_tif(created)
    return created


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


def _validate_tif(tif_path: Path) -> None:
    """Verify a TIFF has a valid byte-order and magic header."""
    header = tif_path.read_bytes()[:4]
    if header not in {b"II*\x00", b"MM\x00*"}:
        raise DngExportError("tiff_validation", "TIFF 標頭無法讀取")


def _export_tif(
    siril: Path,
    output_root: Path,
    fit_path: Path,
    tif_path: Path,
) -> Path:
    """Create the accepted TIFF fallback in the final output directory."""
    with tempfile.TemporaryDirectory(prefix=".dds-tif-", dir=output_root) as temp_dir:
        temporary_tif = Path(temp_dir) / tif_path.name
        created = _run_siril_tif(siril, output_root, fit_path, temporary_tif)
        shutil.copy2(created, tif_path)
    _validate_tif(tif_path)
    return tif_path


def _existing_companion(
    fit_path: Path,
    converter: Path | None,
) -> Path | None:
    """Return an already validated companion, if one exists."""
    dng_path = dng_sidecar_path(fit_path)
    if dng_path.is_file() and converter is None:
        return dng_path
    if dng_path.is_file() and converter is not None:
        try:
            _validate_dng(converter, dng_path)
        except DngExportError:
            pass
        else:
            return dng_path
    for tif_path in _tiff_candidates(fit_path):
        if tif_path.is_file():
            _validate_tif(tif_path)
            return tif_path
    return None


def _try_export_dng(
    siril: Path,
    converter: Path | None,
    output_root: Path,
    fit_path: Path,
    dng_path: Path,
) -> tuple[Path | None, DngExportError | None]:
    """Try DNG export and return a typed error for the TIFF fallback."""
    if converter is None:
        return None, None
    try:
        with tempfile.TemporaryDirectory(
            prefix=".dds-dng-", dir=output_root,
        ) as temp_dir:
            ppm_path = Path(temp_dir) / "converted.ppm"
            _run_siril_export(siril, output_root, fit_path, ppm_path)
            _run_dnglab(converter, ppm_path, dng_path)
    except DngExportError as error:
        dng_path.unlink(missing_ok=True)
        return None, error
    return dng_path, None


def _export_companion(
    siril: Path,
    converter: Path | None,
    output_root: Path,
    fit_path: Path,
) -> Path:
    """Create one DNG, falling back to TIFF when necessary."""
    existing = _existing_companion(fit_path, converter)
    if existing is not None:
        return existing
    dng_path, dng_error = _try_export_dng(
        siril, converter, output_root, fit_path, dng_sidecar_path(fit_path),
    )
    if dng_path is not None:
        return dng_path
    try:
        return _export_tif(
            siril, output_root, fit_path, tif_sidecar_path(fit_path),
        )
    except DngExportError as tif_error:
        if dng_error is not None:
            raise DngExportError(
                "companion_export",
                f"DNG: {dng_error}; TIFF: {tif_error}",
            ) from tif_error
        raise


def export_dng_sidecars(
    output_root: Path,
    *,
    siril_cli: Path | None = None,
    dnglab: Path | None = None,
) -> tuple[Path, ...]:
    """Export one validated DNG, or a TIFF fallback, per result FITS file."""
    if not output_root.is_dir():
        raise DngExportError("output_root", f"directory does not exist: {output_root}")
    fits = result_fits(output_root)
    if not fits:
        raise DngExportError("no_results", "no result*.fit files found")
    siril = _find_tool(siril_cli, "siril-cli")
    try:
        converter = _find_tool(dnglab, "dnglab")
    except DngExportError:
        converter = None
    return tuple(
        _export_companion(siril, converter, output_root, fit_path)
        for fit_path in fits
    )


def main(
    output_root: Path,
    siril_cli: Path | None = None,
    dnglab: Path | None = None,
) -> None:
    """Export DNG/TIFF companions and emit a failed report on any error."""
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
    typer.echo(
        f"DNG/TIFF companions ready: {', '.join(str(path) for path in generated)}",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
