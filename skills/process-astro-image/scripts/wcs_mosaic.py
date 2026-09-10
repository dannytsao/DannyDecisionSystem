#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "astropy>=6",
#     "numpy>=1.26",
#     "reproject>=0.13",
#     "typer",
# ]
# ///

# ruff: noqa: CPY001, RUF001, TRY003, EM101

"""Build a celestial mosaic by reprojecting plate-solved FITS tiles."""

from __future__ import annotations

import json
from contextlib import ExitStack
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from failure_report import write_failed_report
from wcs_background import BackgroundModelError, fit_background

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

_TWO_DIMENSIONS = 2
_THREE_DIMENSIONS = 3


@dataclass(frozen=True, slots=True)
class TileSpec:
    """One validated plate-solved tile from the mosaic manifest."""

    tile_id: str
    source: Path


@dataclass(frozen=True, slots=True)
class WcsMosaicResult:
    """Machine-readable result of one WCS reprojection run."""

    method: str
    input_count: int
    output_path: str
    output_shape: tuple[int, ...]
    channel_count: int
    covered_pixels: int
    output_pixels: int
    coverage_ratio: float


class WcsMosaicError(ValueError):
    """Report invalid WCS mosaic inputs or output constraints."""


def read_tile_specs(run_root: Path) -> tuple[TileSpec, ...]:
    """Read and validate the existing solved-tile manifest."""
    manifest = run_root / "mosaic-input.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    if payload.get("filter") != "IRCUT":
        raise WcsMosaicError("WCS mosaic 目前只接受 IRCUT manifest")
    specs: list[TileSpec] = []
    for item in payload.get("inputs", []):
        tile_id = str(item.get("tile_id", "unknown-tile"))
        source = Path(str(item.get("source", ""))).resolve()
        if not source.is_file():
            reason = f"找不到 plate-solved FITS：{source}"
            raise WcsMosaicError(reason)
        specs.append(TileSpec(tile_id, source))
    if not specs:
        raise WcsMosaicError("mosaic manifest 沒有可用的 tile")
    return tuple(specs)


def _open_tiles(
    specs: tuple[TileSpec, ...], stack: ExitStack,
) -> list[tuple[TileSpec, NDArray[np.floating], object, int]]:
    """Open all tiles as memmaps and validate their 2-D celestial WCS."""
    from astropy.io import fits  # noqa: PLC0415 - optional runtime dependency
    from astropy.wcs import WCS  # noqa: PLC0415 - optional runtime dependency

    opened: list[tuple[TileSpec, NDArray[np.floating], object, int]] = []
    for spec in specs:
        hdul = stack.enter_context(fits.open(spec.source, memmap=True))
        data = hdul[0].data
        if data is None or data.ndim not in (_TWO_DIMENSIONS, _THREE_DIMENSIONS):
            reason = f"{spec.tile_id} 不是 2D 或 channel-first 3D FITS"
            raise WcsMosaicError(reason)
        channels = 1 if data.ndim == _TWO_DIMENSIONS else int(data.shape[0])
        if channels not in (1, 3):
            reason = f"{spec.tile_id} 的 channel 數 {channels} 不受支援"
            raise WcsMosaicError(reason)
        wcs = WCS(hdul[0].header, naxis=2).celestial
        if not wcs.has_celestial:
            reason = f"{spec.tile_id} 缺少 RA/DEC WCS"
            raise WcsMosaicError(reason)
        opened.append((spec, data, wcs, channels))
    channel_counts = {item[3] for item in opened}
    if len(channel_counts) != 1:
        raise WcsMosaicError("所有 tile 必須有相同的 channel 數")
    return opened


def _coadd_channel(
    tiles: list[tuple[TileSpec, NDArray[np.floating], object, int]],
    output_wcs: object,
    output_shape: tuple[int, int],
    channel: int,
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """Reproject one channel and match backgrounds over overlapping tiles."""
    import numpy as np  # noqa: PLC0415 - optional runtime dependency
    from reproject import reproject_interp  # noqa: PLC0415 - optional dependency
    from reproject.mosaicking import reproject_and_coadd  # noqa: PLC0415

    images: list[tuple[NDArray[np.float32], object, NDArray[np.float32], float]] = []
    for spec, data, wcs, _ in tiles:
        image = np.asarray(
            data if data.ndim == _TWO_DIMENSIONS else data[channel],
            dtype=np.float32,
        )
        try:
            background = fit_background(image)
        except BackgroundModelError as error:
            reason = f"{spec.tile_id} 背景模型失敗：{error}"
            raise WcsMosaicError(reason) from error
        baseline = float(np.nanmedian(background))
        images.append((image, wcs, background, baseline))
    target_background = float(np.median([item[3] for item in images]))
    inputs = [
        (image - background + np.float32(target_background), wcs)
        for image, wcs, background, _ in images
    ]
    mosaic, footprint = reproject_and_coadd(
        inputs,
        output_wcs,
        shape_out=output_shape,
        reproject_function=reproject_interp,
        combine_function="mean",
        match_background=True,
        order="bilinear",
        roundtrip_coords=False,
    )
    return np.asarray(mosaic, dtype=np.float32), np.asarray(footprint, dtype=np.float32)


def _write_preview_script(run_root: Path, output_stem: str) -> Path:
    """Write the reviewed Siril stretch/export script without executing it."""
    script = run_root / "wcs-mosaic-preview.ssf"
    root = run_root.resolve().as_posix()
    script.write_text(
        "\n".join(
            (
                "#!/bin/siril",
                "requires 1.4.0",
                f"cd '{root}'",
                f"load {output_stem}",
                f"save {output_stem}_linear",
                "autostretch",
                f"save {output_stem}_autostretched",
                f"savepng {output_stem}_preview",
                "close",
                "",
            ),
        ),
        encoding="utf-8",
    )
    return script


def run_wcs_mosaic(run_root: Path, output_path: Path) -> WcsMosaicResult:
    """Reproject all solved tiles into one common celestial grid."""
    if output_path.exists():
        reason = f"拒絕覆寫既有輸出：{output_path}"
        raise WcsMosaicError(reason)
    specs = read_tile_specs(run_root)
    import numpy as np  # noqa: PLC0415 - optional runtime dependency
    from astropy.io import fits  # noqa: PLC0415 - optional runtime dependency
    from reproject.mosaicking import (  # noqa: PLC0415
        find_optimal_celestial_wcs,
    )

    with ExitStack() as stack:
        tiles = _open_tiles(specs, stack)
        shape_specs = [(data.shape[-2:], wcs) for _, data, wcs, _ in tiles]
        output_wcs, output_shape = find_optimal_celestial_wcs(
            shape_specs, projection="TAN", auto_rotate=False,
        )
        channels = tiles[0][3]
        mosaics: list[NDArray[np.float32]] = []
        footprint: NDArray[np.float32] | None = None
        for channel in range(channels):
            mosaic, current_footprint = _coadd_channel(
                tiles, output_wcs, output_shape, channel,
            )
            mosaics.append(mosaic)
            if footprint is None:
                footprint = current_footprint
        if footprint is None:
            raise WcsMosaicError("WCS mosaic 沒有產生 footprint")
        data = mosaics[0] if channels == 1 else np.stack(mosaics)
        header = output_wcs.to_header(relax=True)
        header["FILTER"] = "IRCUT"
        header["DDSMOS"] = ("WCS_REPROJECT", "DDS mosaic method")
        header["NINPUT"] = (len(specs), "plate-solved tiles")
        header["BUNIT"] = "background-subtracted normalized"
        header["BGMATCH"] = ("QUAD2COMMON", "quadratic border sky normalization")
        fits.PrimaryHDU(data=data, header=header).writeto(output_path)
    covered = int(np.count_nonzero(footprint > 0))
    result = WcsMosaicResult(
        method="WCS reproject + quadratic background normalization + mean coadd",
        input_count=len(specs),
        output_path=str(output_path),
        output_shape=tuple(int(value) for value in data.shape),
        channel_count=channels,
        covered_pixels=covered,
        output_pixels=int(np.prod(output_shape)),
        coverage_ratio=covered / int(np.prod(output_shape)),
    )
    qa_dir = run_root / "qa"
    qa_dir.mkdir(exist_ok=True)
    (qa_dir / "wcs-mosaic.json").write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_root / "wcs-mosaic.md").write_text(
        "\n".join(
            (
                "# WCS 重投影 Mosaic 報告",
                "",
                f"- 輸入 tile：{result.input_count}",
                f"- 輸出尺寸：{result.output_shape}",
                f"- 有效覆蓋率：{result.coverage_ratio:.1%}",
                f"- 方法：{result.method}",
                f"- 輸出：`{result.output_path}`",
                "- 狀態：已完成重投影；仍需檢查背景、接縫與 companion。",
                "",
            ),
        ),
        encoding="utf-8",
    )
    _write_preview_script(run_root, output_path.stem)
    return result


def main(run_root: Path, output_path: Path | None = None) -> None:
    """Run the WCS adapter and write a Chinese failure report on errors."""
    import typer  # noqa: PLC0415 - optional CLI dependency

    resolved_root = run_root.resolve()
    target = output_path or resolved_root / "result_wcs_mosaic.fit"
    try:
        result = run_wcs_mosaic(resolved_root, target.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        report = write_failed_report(
            resolved_root / "wcs-mosaic.md",
            operation="wcs_mosaic",
            reason=str(error),
            input_root=resolved_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        f"WCS mosaic complete: {result.input_count} tiles -> {result.output_path}; "
        f"coverage={result.coverage_ratio:.1%}; preview script written",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
