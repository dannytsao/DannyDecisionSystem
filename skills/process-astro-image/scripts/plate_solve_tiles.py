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
#      uv run plate_solve_tiles.py RUN_ROOT [--focal 250] [--pixel-size 2.9]
# 3. Or make executable and run:
#      chmod +x plate_solve_tiles.py && ./plate_solve_tiles.py RUN_ROOT
# ──────────────────

# ruff: noqa: CPY001, RUF001

"""Plate-solve each tile result without changing the original stack."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path  # noqa: TC003 - Typer resolves CLI annotations at runtime

from failure_report import write_failed_report
from plate_solve_core import (
    DEFAULT_FOCAL_MM,
    DEFAULT_PIXEL_SIZE_UM,
    DEFAULT_TIMEOUT_SECONDS,
    PlateSolveInputError,
    SolveConfig,
    TilePlateSolve,
    resolve_siril,
    run_tile_safely,
)


def _tile_dirs(run_root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path for path in run_root.iterdir()
            if path.is_dir() and (path / "manifest.json").is_file()
        ),
    )


def _markdown(results: tuple[TilePlateSolve, ...]) -> str:
    solved = [item for item in results if item.status == "通過"]
    lines = [
        "# Tile Plate-solving 報告",
        "",
        f"- tile 數：{len(results)}",
        f"- 解算成功：{len(solved)}",
        f"- 解算失敗：{len(results) - len(solved)}",
        "",
        (
            "解算輸出為各 tile 的 `plate_solved.fit`，不會覆寫 "
            "`result_linear.fit`。這一步只確認 WCS 位置，尚未代表 "
            "tile 已可直接合成。"
        ),
        "",
        "| tile | 狀態 | 解析度 (arcsec/px) | 解算中心 RA | 解算中心 DEC |",
        "|---|---|---:|---:|---:|",
    ]
    lines.extend(
        f"| {item.tile_id} | {item.status} | "
        f"{item.resolution_arcsec_per_pixel or 0:.3f} | "
        f"{item.center_ra_deg or 0:.6f} | {item.center_dec_deg or 0:.6f} |"
        for item in results
    )
    failures = [item for item in results if item.error]
    if failures:
        lines.extend(["", "## 失敗明細", ""])
        lines.extend(f"- **{item.tile_id}**：{item.error}" for item in failures)
    lines.extend(
        [
            "",
            (
                "下一步：讀取 WCS footprint，確認 tile 重疊與有效裁切範圍，"
                "再產生 mosaic recipe。"
            ),
            "",
        ],
    )
    return "\n".join(lines)


def run_plate_solves(
    run_root: Path,
    *,
    siril_cli: Path | None = None,
    focal_mm: float = DEFAULT_FOCAL_MM,
    pixel_size_um: float = DEFAULT_PIXEL_SIZE_UM,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[TilePlateSolve, ...]:
    """Solve every tile and preserve a result even when one tile fails."""
    executable = resolve_siril(siril_cli)
    tiles = _tile_dirs(run_root)
    if not tiles:
        reason = f"找不到 tile run：{run_root}"
        raise PlateSolveInputError(reason)
    qa_dir = run_root / "qa"
    log_dir = qa_dir / "plate-solve-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    config = SolveConfig(
        executable=executable,
        log_dir=log_dir,
        focal_mm=focal_mm,
        pixel_size_um=pixel_size_um,
        timeout_seconds=timeout_seconds,
    )
    results: list[TilePlateSolve] = []
    failures: list[str] = []
    for tile_dir in tiles:
        result = run_tile_safely(tile_dir, config)
        results.append(result)
        if result.error:
            failures.append(result.error)
    result_tuple = tuple(results)
    (qa_dir / "plate-solve.json").write_text(
        json.dumps(
            [asdict(item) for item in result_tuple], ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (run_root / "plate-solve.md").write_text(
        _markdown(result_tuple), encoding="utf-8",
    )
    if failures:
        write_failed_report(
            run_root / "plate-solve.md",
            operation="plate_solve_tiles",
            reason=f"{len(failures)} 個 tile 解算失敗",
            input_root=run_root,
        )
    return result_tuple


def main(
    run_root: Path,
    focal_mm: float = DEFAULT_FOCAL_MM,
    pixel_size_um: float = DEFAULT_PIXEL_SIZE_UM,
    siril_cli: Path | None = None,
) -> None:
    """Plate-solve all tiles and write review artifacts."""
    import typer  # noqa: PLC0415 - optional CLI dependency at boundary

    try:
        results = run_plate_solves(
            run_root.resolve(), siril_cli=siril_cli,
            focal_mm=focal_mm, pixel_size_um=pixel_size_um,
        )
    except (OSError, PlateSolveInputError) as error:
        report = write_failed_report(
            run_root / "plate-solve.md",
            operation="plate_solve_tiles",
            reason=str(error),
            input_root=run_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        f"Plate solving complete: {sum(item.status == '通過' for item in results)} "
        f"/{len(results)} succeeded; report: {run_root / 'plate-solve.md'}",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
