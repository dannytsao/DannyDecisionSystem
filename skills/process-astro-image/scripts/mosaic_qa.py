#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["typer"]
# ///

# ─── How to run ───
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run directly (no venv, no pip install needed):
#      uv run mosaic_qa.py MOSAIC_RUN [--threshold 0.8]
# 3. Or make executable and run:
#      chmod +x mosaic_qa.py && ./mosaic_qa.py MOSAIC_RUN
# ──────────────────

# ruff: noqa: CPY001, RUF001, TRY003, EM101

"""Gate mosaic results on actual registered input coverage."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path  # noqa: TC003 - Typer resolves CLI annotations at runtime

from failure_report import write_failed_report

_HEADER = re.compile(r"^S\s+\S+\s+(\d+)\s+(\d+)")
_ITEM = re.compile(r"^I\s+(\d+)\s+([01])")


@dataclass(frozen=True, slots=True)
class MosaicQA:
    """Machine-readable mosaic coverage result."""

    total_tiles: int
    selected_tiles: int
    registration_ratio: float
    rejected_tiles: tuple[str, ...]
    missing_companions: tuple[str, ...]
    status: str


def _sequence(run_root: Path) -> tuple[int, tuple[int, ...]]:
    lines = (run_root / "process" / "tile_.seq").read_text(encoding="utf-8")
    total = 0
    selected: list[int] = []
    for line in lines.splitlines():
        if match := _HEADER.match(line):
            total = int(match.group(2))
        elif (match := _ITEM.match(line)) and match.group(2) == "1":
            selected.append(int(match.group(1)))
    if total <= 0:
        raise ValueError("找不到有效的 mosaic Siril sequence")
    return total, tuple(selected)


def _tile_names(run_root: Path) -> dict[int, str]:
    payload = json.loads(
        (run_root / "mosaic-input.json").read_text(encoding="utf-8"),
    )
    return {
        index: str(item["tile_id"])
        for index, item in enumerate(payload.get("inputs", []), start=1)
    }


def _missing_companions(run_root: Path) -> tuple[str, ...]:
    missing = []
    for fit in sorted(run_root.glob("result_mosaic*.fit")):
        companions = (
            fit.with_suffix(".dng"),
            fit.with_suffix(".tif"),
            fit.with_suffix(".tiff"),
        )
        if not any(path.is_file() for path in companions):
            missing.append(fit.name)
    return tuple(missing)


def build_mosaic_qa(run_root: Path, *, threshold: float = 0.8) -> MosaicQA:
    """Read the executed sequence and return a fail-closed quality result."""
    total, selected = _sequence(run_root)
    names = _tile_names(run_root)
    rejected = tuple(
        names.get(index, f"tile-{index}")
        for index in range(1, total + 1)
        if index not in selected
    )
    missing = _missing_companions(run_root)
    ratio = len(selected) / total
    status = "通過" if ratio >= threshold and not missing else "失敗"
    return MosaicQA(total, len(selected), ratio, rejected, missing, status)


def _markdown(result: MosaicQA, threshold: float) -> str:
    rejected = "、".join(result.rejected_tiles) or "無"
    missing = "、".join(result.missing_companions) or "無"
    return "\n".join(
        (
            "# Mosaic QA 報告",
            "",
            f"- 輸入 tile：{result.total_tiles}",
            f"- 實際註冊：{result.selected_tiles}（{result.registration_ratio:.1%}）",
            f"- 門檻：{threshold:.0%}",
            f"- 狀態：{result.status}",
            f"- 排除 tile：{rejected}",
            f"- 缺少 companion：{missing}",
            "",
            "註冊比例不足時，即使 Siril exit code 為 0，也不能視為可用 mosaic。",
            "",
        ),
    )


def write_mosaic_qa(run_root: Path, *, threshold: float = 0.8) -> MosaicQA:
    """Write JSON and Chinese QA report, recording failed coverage."""
    if not 0 < threshold <= 1:
        raise ValueError("QA 門檻必須介於 0 與 1 之間")
    result = build_mosaic_qa(run_root, threshold=threshold)
    qa_dir = run_root / "qa"
    qa_dir.mkdir(exist_ok=True)
    (qa_dir / "mosaic-qa.json").write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_root / "mosaic-qa.md").write_text(
        _markdown(result, threshold), encoding="utf-8",
    )
    if result.status == "失敗":
        write_failed_report(
            run_root / "mosaic-qa.md",
            operation="mosaic_qa",
            reason=f"mosaic 註冊比例 {result.registration_ratio:.1%} 低於門檻",
            input_root=run_root,
        )
    return result


def main(run_root: Path, threshold: float = 0.8) -> None:
    """Run the mosaic quality gate."""
    import typer  # noqa: PLC0415 - optional CLI dependency at boundary

    try:
        result = write_mosaic_qa(run_root.resolve(), threshold=threshold)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        report = write_failed_report(
            run_root / "mosaic-qa.md",
            operation="mosaic_qa",
            reason=str(error),
            input_root=run_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(
        f"Mosaic QA: {result.selected_tiles}/{result.total_tiles} "
        f"({result.registration_ratio:.1%}); status={result.status}",
    )


if __name__ == "__main__":
    import typer

    typer.run(main)
