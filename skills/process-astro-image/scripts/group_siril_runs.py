#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

# ─── How to run ───
# 1. Install uv (if not installed):
#      curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run directly (no venv, no pip install needed):
#      uv run group_siril_runs.py
# 3. Or make executable and run:
#      chmod +x group_siril_runs.py && ./group_siril_runs.py
# ──────────────────

# ruff: noqa: CPY001

"""Group astrophotography frames by capture date, filter, and sky view."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FramePoint:
    """Describe the metadata needed to assign one frame to a tile."""

    relative_path: str
    capture_date: str
    filter_name: str
    ra_deg: float | None
    dec_deg: float | None


@dataclass(frozen=True, slots=True)
class FrameGroup:
    """Describe one date/filter/tile group ready for a separate stack."""

    group_id: str
    capture_date: str
    filter_name: str
    members: tuple[FramePoint, ...]


# Mutable only while points are assigned, then exposed as a frozen FrameGroup.
@dataclass(slots=True)
class _GroupAccumulator:
    """Mutable builder for one group while points are assigned."""

    capture_date: str
    filter_name: str
    anchor: FramePoint | None
    members: list[FramePoint]


@dataclass(frozen=True, slots=True)
class GroupingInputError(Exception):
    """Report an invalid view-grouping option."""

    reason: str

    def __str__(self) -> str:
        """Return a concise grouping error."""
        return self.reason


def _distance(first: FramePoint, second: FramePoint) -> float | None:
    if (
        first.ra_deg is None
        or first.dec_deg is None
        or second.ra_deg is None
        or second.dec_deg is None
    ):
        return None
    mean_dec = math.radians((first.dec_deg + second.dec_deg) / 2)
    return math.hypot(
        (first.ra_deg - second.ra_deg) * math.cos(mean_dec),
        first.dec_deg - second.dec_deg,
    )


def _same_view(
    point: FramePoint,
    accumulator: _GroupAccumulator,
    radius_deg: float,
) -> bool:
    if accumulator.anchor is None:
        return False
    distance = _distance(point, accumulator.anchor)
    return distance is not None and distance <= radius_deg


def _filter_slug(filter_name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", filter_name.strip()).strip("-")
    return slug or "unknown-filter"


def group_views(
    points: tuple[FramePoint, ...],
    *,
    view_radius_deg: float = 0.4,
) -> tuple[FrameGroup, ...]:
    """Split points into stable date/filter groups with non-overlapping tile anchors."""
    if view_radius_deg <= 0:
        reason = "view radius must be greater than zero"
        raise GroupingInputError(reason)
    buckets: dict[tuple[str, str], list[FramePoint]] = {}
    for point in sorted(
        points,
        key=lambda item: (
            item.capture_date,
            item.filter_name,
            item.relative_path,
        ),
    ):
        buckets.setdefault((point.capture_date, point.filter_name), []).append(point)

    result: list[FrameGroup] = []
    for (capture_date, filter_name), bucket in sorted(buckets.items()):
        accumulators: list[_GroupAccumulator] = []
        for point in bucket:
            matching = next(
                (
                    accumulator
                    for accumulator in accumulators
                    if _same_view(point, accumulator, view_radius_deg)
                ),
                None,
            )
            if matching is None:
                accumulators.append(
                    _GroupAccumulator(
                        capture_date=capture_date,
                        filter_name=filter_name,
                        anchor=point if point.ra_deg is not None else None,
                        members=[point],
                    ),
                )
            else:
                matching.members.append(point)
        for index, accumulator in enumerate(accumulators, start=1):
            result.append(
                FrameGroup(
                    group_id=(
                        f"{capture_date}_{_filter_slug(filter_name)}_tile-{index:02d}"
                    ),
                    capture_date=capture_date,
                    filter_name=filter_name,
                    members=tuple(accumulator.members),
                ),
            )
    return tuple(result)


def main() -> None:
    """Keep direct execution side-effect free; callers should import group_views."""


if __name__ == "__main__":
    main()
