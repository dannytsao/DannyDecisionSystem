# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for deterministic astrophotography view grouping."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location(
    "group_siril_runs",
    SCRIPT_DIR / "group_siril_runs.py",
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_group_views_separates_date_filter_and_nonoverlapping_views() -> None:
    """Given mixed captures, groups split by date, filter, and sky distance."""
    points = (
        MODULE.FramePoint("a.fit", "2025-10-04", "IRCUT", 12.0, 41.0),
        MODULE.FramePoint("b.fit", "2025-10-04", "IRCUT", 12.1, 41.05),
        MODULE.FramePoint("c.fit", "2025-10-04", "IRCUT", 9.5, 41.0),
        MODULE.FramePoint("d.fit", "2025-10-04", "LP", 12.0, 41.0),
        MODULE.FramePoint("e.fit", "2024-11-27", "IRCUT", 12.0, 41.0),
    )

    groups = MODULE.group_views(points, view_radius_deg=0.25)

    assert [len(group.members) for group in groups] == [1, 2, 1, 1]
    assert [group.capture_date for group in groups] == [
        "2024-11-27",
        "2025-10-04",
        "2025-10-04",
        "2025-10-04",
    ]
    assert [group.filter_name for group in groups] == [
        "IRCUT",
        "IRCUT",
        "IRCUT",
        "LP",
    ]
