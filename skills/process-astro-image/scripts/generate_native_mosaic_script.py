#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["typer"]
# ///

"""Generate a reviewable Siril astrometric mosaic recipe from a tile manifest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from failure_report import write_failed_report


@dataclass(frozen=True, slots=True)
class NativeMosaicPreparation:
    """Paths and input count written by the native mosaic generator."""

    input_count: int
    script_path: Path
    report_path: Path


class NativeMosaicError(ValueError):
    """Report an unsafe or incomplete native mosaic input set."""


def _manifest_inputs(run_root: Path) -> list[dict[str, str]]:
    manifest = run_root / "mosaic-input.json"
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise NativeMosaicError(f"無法讀取 mosaic-input.json：{manifest}") from error
    if payload.get("filter") != "IRCUT":
        raise NativeMosaicError("原生 Siril mosaic 目前只接受 IRCUT manifest")
    inputs = payload.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise NativeMosaicError("manifest 沒有可用的 mosaic tile")
    rows: list[dict[str, str]] = []
    for item in inputs:
        if not isinstance(item, dict):
            raise NativeMosaicError("manifest 的 tile 項目格式不正確")
        source = Path(str(item.get("source", ""))).resolve()
        if not source.is_file():
            raise NativeMosaicError(f"tile FITS 不存在：{source}")
        rows.append({"tile_id": str(item.get("tile_id", "unknown-tile")), "source": str(source)})
    lights = run_root / "Lights"
    if not lights.is_dir() or not any(lights.glob("*.fit")):
        raise NativeMosaicError("找不到 Lights 內的 FITS tile")
    return rows


def _quote(path: Path) -> str:
    value = path.resolve().as_posix()
    if any(char in value for char in ("\"", "\n", "\r")):
        raise NativeMosaicError("run 路徑含有不安全字元")
    return f'"{value}"'


def _script(run_root: Path, *, feather_pixels: int) -> str:
    if feather_pixels < 0:
        raise NativeMosaicError("feather 像素不可小於 0")
    root = _quote(run_root)
    return "\n".join(
        (
            "#!/bin/siril",
            "requires 1.4.0",
            "# DDS native Siril astrometric mosaic; execution requires explicit approval.",
            f"cd {root}",
            "cd Lights",
            "convert tile -out=../process",
            "cd ../process",
            "seqplatesolve tile_ -force -nocache",
            "seqapplyreg tile_ -framing=max -interp=lanczos3",
            (
                "stack r_tile_ rej none -norm=addscale -maximize "
                f"-overlap_norm -feather={feather_pixels} "
                "-out=../result_siril_mosaic -32b"
            ),
            "cd ..",
            "load result_siril_mosaic",
            "save result_siril_mosaic_linear",
            "autostretch",
            "save result_siril_mosaic_autostretched",
            "savepng result_siril_mosaic_preview",
            "close",
        ),
    ) + "\n"


def generate_native_mosaic_script(
    run_root: Path,
    output: Path | None = None,
    *,
    feather_pixels: int = 150,
) -> NativeMosaicPreparation:
    """Validate the manifest and write a non-executing native Siril recipe."""
    run_root = run_root.resolve()
    rows = _manifest_inputs(run_root)
    script_path = (output or run_root / "native-mosaic-dry-run.ssf").resolve()
    script_path.write_text(
        _script(run_root, feather_pixels=feather_pixels), encoding="utf-8",
    )
    report_path = run_root / "native-mosaic-dry-run.md"
    report_path.write_text(
        "\n".join(
            (
                "# 原生 Siril Mosaic dry-run",
                "",
                f"- 輸入 tile：{len(rows)}",
                f"- feather：{feather_pixels} 像素",
                "- 狀態：只產生腳本，尚未執行 Siril",
                "- 重要：執行前必須檢查每張 tile 的 WCS 與背景一致性。",
                "",
            ),
        ),
        encoding="utf-8",
    )
    return NativeMosaicPreparation(len(rows), script_path, report_path)


def main(run_root: Path, output: Path | None = None, feather_pixels: int = 150) -> None:
    """Generate the recipe and write a Chinese failed report on errors."""
    import typer

    try:
        result = generate_native_mosaic_script(
            run_root, output, feather_pixels=feather_pixels,
        )
    except (OSError, ValueError) as error:
        report = write_failed_report(
            run_root / "native-mosaic-dry-run.ssf",
            operation="prepare_mosaic_run",
            reason=str(error),
            input_root=run_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        f"Prepared {result.input_count} native mosaic tiles; script: {result.script_path}; "
        f"report: {result.report_path}",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
