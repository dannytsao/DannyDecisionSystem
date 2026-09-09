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
#      uv run --script run_siril.py SCRIPT.ssf RUN_DIR [--siril-cli PATH]
# ──────────────────

# ruff: noqa: CPY001

"""Run an approved Siril script and fail closed with a report on errors."""

from __future__ import annotations

import subprocess
from pathlib import Path

from export_dng_sidecars import DngExportError, export_dng_sidecars
from failure_report import write_failed_report

DEFAULT_SIRIL_CLI = Path("/Applications/Siril.app/Contents/MacOS/siril-cli")


class SirilExecutionError(RuntimeError):
    """Report a non-zero Siril execution result."""

    def __init__(self, returncode: int, detail: str) -> None:
        """Initialize the exit code and captured diagnostic detail."""
        self.returncode = returncode
        self.detail = detail
        super().__init__(f"Siril execution failed (exit {returncode}): {detail}")


def _resolve_siril(path: Path | None) -> Path:
    if path is not None:
        if path.is_file():
            return path
        raise SirilExecutionError(2, f"siril-cli not found at {path}")
    if DEFAULT_SIRIL_CLI.is_file():
        return DEFAULT_SIRIL_CLI
    raise SirilExecutionError(2, "siril-cli is not available")


def run_siril(
    script_path: Path,
    run_root: Path,
    *,
    siril_cli: Path | None = None,
) -> tuple[Path, ...]:
    """Run Siril, then require DNG or TIFF companions for all result FITS."""
    if not script_path.is_file():
        raise SirilExecutionError(2, f"script does not exist: {script_path}")
    if not run_root.is_dir():
        raise SirilExecutionError(2, f"run directory does not exist: {run_root}")
    executable = _resolve_siril(siril_cli)
    result = subprocess.run(  # noqa: S603 - executable path is explicitly resolved
        [str(executable), "-s", str(script_path.resolve())],
        capture_output=True,
        check=False,
        text=True,
        cwd=run_root,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[-1200:]
        raise SirilExecutionError(result.returncode, detail or "no diagnostic output")
    return export_dng_sidecars(run_root, siril_cli=executable)


def main(script_path: Path, run_root: Path, siril_cli: Path | None = None) -> None:
    """Execute Siril and write a failed report for every failed boundary."""
    import typer  # noqa: PLC0415 - optional CLI dependency loaded only at boundary

    try:
        outputs = run_siril(script_path, run_root, siril_cli=siril_cli)
    except (SirilExecutionError, DngExportError, OSError) as error:
        report = write_failed_report(
            run_root / "failed-report.md",
            operation="run_siril",
            reason=str(error),
            input_root=run_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        "Siril run complete; DNG/TIFF companions ready: "
        f"{', '.join(map(str, outputs))}",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
