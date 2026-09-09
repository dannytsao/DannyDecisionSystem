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
#      uv run prepare_tile_runs.py SESSION_DIR OUTPUT_DIR [--view-radius-deg 0.4]
# 3. Or make executable and run:
#      chmod +x prepare_tile_runs.py && ./prepare_tile_runs.py SESSION_DIR OUTPUT_DIR
# ──────────────────

# ruff: noqa: CPY001

"""Prepare isolated Siril runs for date/filter/sky-view groups."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TC003 - Path is used at runtime

from build_manifest import (
    FrameKind,
    ImageRecord,
    ManifestInputError,
    _json_ready,
    build_manifest,
)
from failure_report import write_failed_report
from generate_siril_script import RecipeGenerationError, generate_script
from group_siril_runs import FrameGroup, FramePoint, GroupingInputError, group_views


class TilePreparationError(RuntimeError):
    """Report a group-run preparation boundary failure."""


def _point_from_record(record: ImageRecord) -> FramePoint | None:
    """Convert a manifest light record into a grouping point."""
    if record.kind is not FrameKind.LIGHT:
        return None
    metadata = record.metadata
    if metadata is None:
        return None
    capture_date = (metadata.date_obs or "unknown-date").split("T", 1)[0]
    filter_name = (metadata.filter_name or "unknown-filter").strip()
    return FramePoint(
        relative_path=record.relative_path,
        capture_date=capture_date,
        filter_name=filter_name,
        ra_deg=metadata.ra_deg,
        dec_deg=metadata.dec_deg,
    )


def _write_group_manifest(group_dir: Path) -> None:
    manifest = build_manifest(group_dir)
    if manifest.preflight.status == "blocked":
        reason = (
            f"group {group_dir.name} is blocked: {manifest.preflight.blocking_checks}"
        )
        raise TilePreparationError(reason)
    (group_dir / "manifest.json").write_text(
        _json_ready(manifest), encoding="utf-8",
    )


def _create_group_run(
    input_root: Path,
    output_root: Path,
    group: FrameGroup,
) -> Path:
    group_dir = output_root / group.group_id
    lights_dir = group_dir / "Lights"
    lights_dir.mkdir(parents=True)
    names: set[str] = set()
    for point in group.members:
        source = input_root / point.relative_path
        name = source.name
        if name in names:
            reason = f"duplicate light filename in group {group.group_id}: {name}"
            raise TilePreparationError(reason)
        names.add(name)
        (lights_dir / name).symlink_to(source)
    _write_group_manifest(group_dir)
    generate_script(group_dir, output_root / f"{group.group_id}.ssf")
    return group_dir


def _write_group_index(output_root: Path, groups: tuple[FrameGroup, ...]) -> None:
    payload = [
        {
            "group_id": group.group_id,
            "capture_date": group.capture_date,
            "filter_name": group.filter_name,
            "frame_count": len(group.members),
            "members": [point.relative_path for point in group.members],
        }
        for group in groups
    ]
    (output_root / "groups.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def prepare_tile_runs(
    input_root: Path,
    output_root: Path,
    *,
    view_radius_deg: float = 0.4,
) -> tuple[Path, ...]:
    """Create symlinked, independently reviewable Siril tile runs."""
    resolved_input = input_root.resolve()
    resolved_output = output_root.resolve()
    manifest = build_manifest(resolved_input)
    if manifest.preflight.status == "blocked":
        reason = f"input is blocked: {manifest.preflight.blocking_checks}"
        raise TilePreparationError(reason)
    points = tuple(
        point
        for record in manifest.files
        if (point := _point_from_record(record)) is not None
    )
    groups = group_views(points, view_radius_deg=view_radius_deg)
    if resolved_output.exists() and any(resolved_output.iterdir()):
        reason = f"output directory is not empty: {resolved_output}"
        raise TilePreparationError(reason)
    resolved_output.mkdir(parents=True, exist_ok=True)
    _write_group_index(resolved_output, groups)
    return tuple(
        _create_group_run(resolved_input, resolved_output, group)
        for group in groups
    )


def main(
    input_root: Path,
    output_root: Path,
    view_radius_deg: float = 0.4,
) -> None:
    """Prepare grouped runs and write a Chinese failure report on errors."""
    import typer  # noqa: PLC0415 - optional CLI dependency at the boundary

    try:
        groups = prepare_tile_runs(
            input_root, output_root, view_radius_deg=view_radius_deg,
        )
    except (
        GroupingInputError,
        ManifestInputError,
        RecipeGenerationError,
        TilePreparationError,
        OSError,
    ) as error:
        report = write_failed_report(
            output_root / "failed-report.md",
            operation="prepare_tile_runs",
            reason=str(error),
            input_root=input_root,
        )
        typer.echo(f"{error}\nfailed report written: {report}", err=True)
        raise typer.Exit(code=2) from error
    typer.echo(f"Prepared {len(groups)} tile runs under {output_root}")


if __name__ == "__main__":
    import typer

    typer.run(main)
