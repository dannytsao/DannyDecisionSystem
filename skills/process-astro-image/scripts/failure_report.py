#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

# ─── How to run ───
# This module is imported by the Pilot CLI scripts; run those entry points instead.
# ──────────────────

# ruff: noqa: CPY001

"""Write append-only failure reports for every rejected Pilot operation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path  # noqa: TC003 - Path is used at runtime


def failed_report_path(target: Path) -> Path:
    """Return the report path associated with an output target."""
    if target.name == "failed-report.md":
        return target
    return target.with_name(f"{target.stem}-failed-report.md")


def write_failed_report(
    target: Path,
    *,
    operation: str,
    reason: str,
    input_root: Path | None = None,
) -> Path:
    """Append a structured failed report without overwriting prior failures."""
    report = failed_report_path(target)
    report.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    input_line = f"- input_root: `{input_root}`\n" if input_root else ""
    entry = (
        f"## Failed Pilot operation — {timestamp}\n\n"
        "- status: failed\n"
        f"- operation: {operation}\n"
        f"- reason: {reason}\n"
        f"{input_line}"
        "- next_action: inspect the evidence, correct the input or tool, and rerun\n"
    )
    if report.exists():
        report.write_text(
            report.read_text(encoding="utf-8") + f"\n{entry}",
            encoding="utf-8",
        )
    else:
        report.write_text(f"# Failed Report\n\n{entry}", encoding="utf-8")
    return report
