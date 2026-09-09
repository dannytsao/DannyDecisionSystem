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
#      uv run prepare_mosaic_run.py PLATE_ROOT OUTPUT_ROOT
# 3. Or make executable and run:
#      chmod +x prepare_mosaic_run.py && ./prepare_mosaic_run.py PLATE_ROOT OUTPUT_ROOT
# ──────────────────

# ruff: noqa: CPY001, RUF001, TRY003, EM101, EM102

"""Prepare a non-destructive IRCUT mosaic run from solved tile results."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from failure_report import write_failed_report


@dataclass(frozen=True, slots=True)
class MosaicPreparation:
    """Paths and counts written by mosaic preparation."""

    input_count: int
    excluded_tiles: tuple[str, ...]
    manifest_path: Path
    script_path: Path
    report_path: Path


class MosaicPreparationError(ValueError):
    """Report an unsafe or incomplete mosaic input set."""

    def __init__(self, reason: str) -> None:
        """Store a user-readable diagnostic."""
        self.reason = reason
        super().__init__(reason)

    def __str__(self) -> str:
        """Return the diagnostic for reports."""
        return self.reason


def _read_plate_index(plate_root: Path) -> list[dict[str, str]]:
    index_path = plate_root / "qa" / "plate-solve.json"
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise MosaicPreparationError(f"plate-solve index 不是清單：{index_path}")
    return [row for row in payload if isinstance(row, dict)]


def _select_inputs(
    plate_root: Path,
    rows: list[dict[str, str]],
) -> tuple[list[tuple[str, Path]], tuple[str, ...]]:
    selected: list[tuple[str, Path]] = []
    excluded: list[str] = []
    resolved_root = plate_root.resolve()
    for row in rows:
        tile_id = str(row.get("tile_id", "unknown-tile"))
        status = str(row.get("status", ""))
        output = row.get("output_path", "")
        if status == "通過" and "_IRCUT_" in tile_id:
            source = Path(output).resolve()
            try:
                source.relative_to(resolved_root)
            except ValueError as error:
                raise MosaicPreparationError(
                    f"tile 輸出不在 plate root 內：{source}",
                ) from error
            if not source.is_file():
                raise MosaicPreparationError(f"tile FITS 不存在：{source}")
            selected.append((tile_id, source))
        else:
            excluded.append(tile_id)
    if not selected:
        raise MosaicPreparationError("沒有可用的 IRCUT plate-solved tile")
    return selected, tuple(excluded)


def _script(output_root: Path) -> str:
    root = output_root.resolve().as_posix()
    if "'" in root or "\n" in root or "\r" in root:
        raise MosaicPreparationError("mosaic output path 含有不安全字元")
    quoted = f"'{root}'"
    return "\n".join(
        (
            "#!/bin/siril",
            "requires 1.4.0",
            "# DDS IRCUT mosaic dry-run; execution_enabled=false",
            "# This file is generated for review and is not executed by this tool.",
            f"cd {quoted}",
            "cd Lights",
            "convert tile -out=../process",
            "cd ../process",
            "register tile -2pass -maxstars=500 -interp=lanczos3",
            "seqapplyreg tile -interp=lanczos3 -framing=max",
            (
                "stack r_tile rej winsorized 3 3 -norm=addscale "
                "-weight=wfwhm -out=../result_mosaic -32b"
            ),
            "cd ..",
            "load result_mosaic",
            "save result_mosaic_linear",
            "autostretch",
            "save result_mosaic_autostretched",
            "savepng result_mosaic_preview",
            "# Export result*.fit companions with export_dng_sidecars.py after review.",
            "close",
        ),
    ) + "\n"


def prepare_mosaic_run(plate_root: Path, output_root: Path) -> MosaicPreparation:
    """Link solved IRCUT tiles and write a review-only mosaic script."""
    plate_root = plate_root.resolve()
    output_root = output_root.resolve()
    if output_root.exists() and any(output_root.iterdir()):
        raise MosaicPreparationError(f"output directory is not empty: {output_root}")
    rows = _read_plate_index(plate_root)
    selected, excluded = _select_inputs(plate_root, rows)
    output_root.mkdir(parents=True, exist_ok=True)
    lights = output_root / "Lights"
    lights.mkdir()
    links: list[dict[str, str]] = []
    for index, (tile_id, source) in enumerate(selected, start=1):
        name = f"tile_{index:04d}.fit"
        (lights / name).symlink_to(source)
        links.append({"tile_id": tile_id, "source": str(source), "link": name})
    manifest_path = output_root / "mosaic-input.json"
    manifest_path.write_text(
        json.dumps(
            {
                "filter": "IRCUT",
                "input_count": len(links),
                "excluded_tiles": list(excluded),
                "inputs": links,
                "execution_enabled": False,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    script_path = output_root / "mosaic-dry-run.ssf"
    script_path.write_text(_script(output_root), encoding="utf-8")
    report_path = output_root / "mosaic-dry-run.md"
    excluded_text = "、".join(excluded) if excluded else "無"
    report_path.write_text(
        "\n".join(
            (
                "# IRCUT Mosaic dry-run",
                "",
                f"- 輸入 tile：{len(links)}",
                f"- 排除 tile：{excluded_text}",
                "- 狀態：僅產生腳本，尚未執行 Siril",
                "- execution_enabled：false",
                "",
                "執行前仍需確認有效裁切範圍、校準資料與背景亮度一致性。",
                "",
            ),
        ),
        encoding="utf-8",
    )
    return MosaicPreparation(
        input_count=len(links),
        excluded_tiles=excluded,
        manifest_path=manifest_path,
        script_path=script_path,
        report_path=report_path,
    )


def main(plate_root: Path, output_root: Path) -> None:
    """Prepare the IRCUT mosaic run and fail closed on unsafe inputs."""
    import typer  # noqa: PLC0415 - optional CLI dependency at boundary

    try:
        result = prepare_mosaic_run(plate_root, output_root)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        report = write_failed_report(
            output_root / "mosaic-dry-run.ssf",
            operation="prepare_mosaic_run",
            reason=str(error),
            input_root=plate_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        f"Prepared {result.input_count} IRCUT tiles; script: {result.script_path}; "
        f"report: {result.report_path}",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
