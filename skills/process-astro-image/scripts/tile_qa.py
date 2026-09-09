#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "Pillow",
#     "typer",
# ]
# ///

# ─── How to run ───
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run directly (no venv, no pip install needed):
#      uv run tile_qa.py RUN_ROOT [--threshold 0.8]
# 3. Or make executable and run:
#      chmod +x tile_qa.py && ./tile_qa.py RUN_ROOT
# ──────────────────

# ruff: noqa: CPY001, RUF001

"""Summarize Siril tile registration and build a visual review sheet."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from failure_report import write_failed_report
from PIL import Image, ImageDraw, ImageFont

_SEQ_HEADER: Final = re.compile(r"^#?S\s+\S+\s+(\d+)\s+(\d+)")
_SEQ_ITEM: Final = re.compile(r"^I\s+(\d+)\s+([01])")
_CONVERSION: Final = re.compile(
    r"^'(.+?)'\s+->\s+'\.\./process/light_(\d+)\.fit'",
)
_COLUMNS: Final = 5
_CELL_WIDTH: Final = 260
_CELL_HEIGHT: Final = 190


@dataclass(frozen=True, slots=True)
class TileQA:
    """Machine-readable QA result for one tile run."""

    tile_id: str
    capture_date: str
    filter_name: str
    total_frames: int
    selected_frames: int
    registration_ratio: float
    rejected_frames: tuple[str, ...]
    missing_companions: tuple[str, ...]
    preview_available: bool
    status: str


@dataclass(frozen=True, slots=True)
class QAArtifacts:
    """Paths written by the QA report builder."""

    markdown_path: Path
    json_path: Path
    contact_sheet_path: Path


class TileQAInputError(ValueError):
    """Report a malformed or incomplete tile run."""

    def __init__(self, reason: str) -> None:
        """Store a user-readable diagnostic."""
        self.reason = reason
        super().__init__(reason)

    def __str__(self) -> str:
        """Return the diagnostic for CLI reports."""
        return self.reason


def _read_sequence(tile_dir: Path) -> tuple[int, tuple[int, ...]]:
    sequence = tile_dir / "process" / "light_.seq"
    total = 0
    selected: list[int] = []
    for line in sequence.read_text(encoding="utf-8").splitlines():
        if match := _SEQ_HEADER.match(line):
            total = int(match.group(2))
        elif (match := _SEQ_ITEM.match(line)) and match.group(2) == "1":
            selected.append(int(match.group(1)))
    if total <= 0:
        reason = f"找不到有效的 Siril sequence 張數：{sequence}"
        raise TileQAInputError(reason)
    return total, tuple(selected)


def _source_names(tile_dir: Path) -> dict[int, str]:
    conversion = tile_dir / "process" / "light_conversion.txt"
    names: dict[int, str] = {}
    for line in conversion.read_text(encoding="utf-8").splitlines():
        if match := _CONVERSION.match(line):
            names[int(match.group(2))] = Path(match.group(1)).name
    return names


def _tile_metadata(tile_dir: Path) -> tuple[str, str]:
    payload = json.loads((tile_dir / "manifest.json").read_text(encoding="utf-8"))
    records = payload.get("files", [])
    first = records[0] if records else {}
    metadata = first.get("metadata", {})
    date = str(metadata.get("date_obs") or tile_dir.name.split("_", 1)[0])
    filter_name = str(metadata.get("filter_name") or "unknown-filter")
    return date.split("T", 1)[0], filter_name


def _missing_companions(tile_dir: Path) -> tuple[str, ...]:
    missing: list[str] = []
    for fit_path in sorted(tile_dir.glob("result*.fit")):
        candidates = (
            fit_path.with_suffix(".dng"),
            fit_path.with_suffix(".tif"),
            fit_path.with_suffix(".tiff"),
        )
        if not any(path.is_file() for path in candidates):
            missing.append(fit_path.name)
    return tuple(missing)


def build_tile_qa(tile_dir: Path, *, threshold: float = 0.8) -> TileQA:
    """Parse one tile's Siril sequence and result companion contract."""
    total, selected = _read_sequence(tile_dir)
    sources = _source_names(tile_dir)
    rejected = tuple(
        sources.get(index, f"light_{index:05d}.fit")
        for index in range(1, total + 1)
        if index not in selected
    )
    ratio = len(selected) / total
    missing = _missing_companions(tile_dir)
    status = "通過" if ratio >= threshold and not missing else "需複查"
    capture_date, filter_name = _tile_metadata(tile_dir)
    return TileQA(
        tile_id=tile_dir.name,
        capture_date=capture_date,
        filter_name=filter_name,
        total_frames=total,
        selected_frames=len(selected),
        registration_ratio=ratio,
        rejected_frames=rejected,
        missing_companions=missing,
        preview_available=(tile_dir / "result_preview.png").is_file(),
        status=status,
    )


def _tile_dirs(run_root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            path for path in run_root.iterdir()
            if path.is_dir() and (path / "manifest.json").is_file()
        ),
    )


def _contact_sheet(tiles: tuple[TileQA, ...], run_root: Path, target: Path) -> None:
    previews = [
        (tile, run_root / tile.tile_id / "result_preview.png")
        for tile in tiles
        if tile.preview_available
    ]
    rows = max(1, (len(previews) + _COLUMNS - 1) // _COLUMNS)
    sheet = Image.new("RGB", (_COLUMNS * _CELL_WIDTH, rows * _CELL_HEIGHT), "#202124")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (tile, path) in enumerate(previews):
        try:
            with Image.open(path) as source:
                image = source.convert("RGB")
                image.thumbnail((_CELL_WIDTH - 12, _CELL_HEIGHT - 38))
                x = (index % _COLUMNS) * _CELL_WIDTH + (_CELL_WIDTH - image.width) // 2
                y = (index // _COLUMNS) * _CELL_HEIGHT + 4
                sheet.paste(image, (x, y))
        except OSError:
            continue
        label = f"{tile.tile_id} {tile.registration_ratio:.1%} {tile.status}"
        draw.text(
            ((index % _COLUMNS) * _CELL_WIDTH + 6,
             (index // _COLUMNS) * _CELL_HEIGHT + _CELL_HEIGHT - 28),
            label,
            fill="white",
            font=font,
        )
    sheet.save(target)


def _markdown(tiles: tuple[TileQA, ...], threshold: float) -> str:
    total = sum(tile.total_frames for tile in tiles)
    selected = sum(tile.selected_frames for tile in tiles)
    review = [tile for tile in tiles if tile.status != "通過"]
    lines = [
        "# Tile QA 報告",
        "",
        f"- tile 數：{len(tiles)}",
        f"- 總張數：{total}",
        (
            f"- 成功註冊：{selected}（{selected / total:.1%}）"
            if total
            else "- 成功註冊：0"
        ),
        f"- 複查門檻：{threshold:.0%}",
        f"- 需複查 tile：{len(review)}",
        "",
        "## 判讀方式",
        "",
        (
            "註冊被排除的 frame 是品質選擇，不等同於工具失敗；"
            "若工具或輸出 companion 失敗，才應查看 `Failed/failed-report.md`。"
        ),
        "",
        "## 各 tile 結果",
        "",
        "| tile | 日期 | 濾鏡 | 張數 | 註冊 | 比率 | 狀態 |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    lines.extend(
        f"| {tile.tile_id} | {tile.capture_date} | {tile.filter_name} | "
        f"{tile.total_frames} | {tile.selected_frames} | "
        f"{tile.registration_ratio:.1%} | {tile.status} |"
        for tile in sorted(tiles, key=lambda item: item.registration_ratio)
    )
    lines.extend(["", "## 需複查明細", ""])
    for tile in review:
        rejected = "、".join(tile.rejected_frames) or "無"
        missing = "、".join(tile.missing_companions) or "無"
        lines.append(
            f"- **{tile.tile_id}**：排除 {rejected}；"
            f"缺少 companion：{missing}",
        )
    if not review:
        lines.append("- 所有 tile 均達到目前門檻，仍需人工檢查星點與背景。")
    lines.extend(["", "預覽 contact sheet：`qa/contact-sheet.png`", ""])
    return "\n".join(lines)


def write_tile_qa(run_root: Path, *, threshold: float = 0.8) -> QAArtifacts:
    """Write JSON, Chinese Markdown, and a preview contact sheet."""
    if not 0 < threshold <= 1:
        reason = "複查門檻必須介於 0 與 1 之間"
        raise TileQAInputError(reason)
    tiles = tuple(
        build_tile_qa(path, threshold=threshold)
        for path in _tile_dirs(run_root)
    )
    if not tiles:
        reason = f"找不到 tile run：{run_root}"
        raise TileQAInputError(reason)
    qa_dir = run_root / "qa"
    qa_dir.mkdir(exist_ok=True)
    json_path = qa_dir / "tile-qa.json"
    json_path.write_text(
        json.dumps(
            [asdict(tile) for tile in tiles], ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    markdown_path = run_root / "tile-qa.md"
    markdown_path.write_text(_markdown(tiles, threshold), encoding="utf-8")
    contact_sheet_path = qa_dir / "contact-sheet.png"
    _contact_sheet(tiles, run_root, contact_sheet_path)
    return QAArtifacts(markdown_path, json_path, contact_sheet_path)


def main(run_root: Path, threshold: float = 0.8) -> None:
    """Run tile QA and write a Failed report only on tool-level errors."""
    import typer  # noqa: PLC0415 - optional CLI dependency at boundary

    try:
        artifacts = write_tile_qa(run_root.resolve(), threshold=threshold)
    except (OSError, TileQAInputError, json.JSONDecodeError) as error:
        report = write_failed_report(
            run_root / "tile-qa.md",
            operation="tile_qa",
            reason=str(error),
            input_root=run_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        f"Tile QA complete: {artifacts.markdown_path}; "
        f"contact sheet: {artifacts.contact_sheet_path}",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
