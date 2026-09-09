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
#      uv run build_manifest.py SESSION_DIR [--output MANIFEST.json]
# 3. Or make executable and run:
#      chmod +x build_manifest.py && ./build_manifest.py SESSION_DIR
# ──────────────────

# ruff: noqa: CPY001

"""Create a read-only astrophotography session manifest and dry-run plan."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path  # noqa: TC003 - Path is also used at runtime
from typing import Final, Literal

from fits_header import FitsHeaderError, FitsMetadata, is_fits, read_fits_metadata

SUPPORTED_SUFFIXES: Final = frozenset(
    {
        ".arw",
        ".cr2",
        ".cr3",
        ".dng",
        ".fit",
        ".fits",
        ".fts",
        ".nef",
        ".xisf",
    },
)
IGNORED_METADATA_FILENAMES: Final = frozenset({".DS_Store", "manifest.json"})


class FrameKind(str, Enum):
    """Initial frame classification based on supported suffixes and name tokens."""

    LIGHT = "light"
    DARK = "dark"
    FLAT = "flat"
    BIAS = "bias"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ManifestInputError(Exception):
    """Report a session boundary that cannot be inspected safely."""

    path: Path
    reason: str

    def __str__(self) -> str:
        """Return a user-facing description without exposing sensitive data."""
        return f"invalid session {self.path}: {self.reason}"


@dataclass(frozen=True)
class ImageRecord:
    """Describe one input file and its content hash."""

    relative_path: str
    kind: FrameKind
    suffix: str
    size_bytes: int
    sha256: str
    metadata_status: Literal["parsed", "pending", "invalid"]
    metadata: FitsMetadata | None
    metadata_error: str | None


@dataclass(frozen=True)
class Preflight:
    """Record blocking and pending checks before any execution is allowed."""

    status: Literal["ready_for_review", "blocked"]
    blocking_checks: tuple[str, ...]
    pending_checks: tuple[str, ...]


@dataclass(frozen=True)
class DryRunPlan:
    """Describe planned steps without enabling a tool invocation."""

    steps: tuple[str, ...]
    requires_approval: bool
    execution_enabled: bool


@dataclass(frozen=True)
class SessionManifest:
    """Immutable manifest exchanged between intake and later Pilot gates."""

    schema_version: str
    input_root: str
    files: tuple[ImageRecord, ...]
    counts: dict[FrameKind, int]
    preflight: Preflight
    plan: DryRunPlan


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _classify(path: Path) -> FrameKind:
    tokens = {
        token
        for part in (*path.parts, path.stem)
        for token in re.split(r"[^a-z0-9]+", part.lower())
        if token
    }
    if "dark" in tokens:
        return FrameKind.DARK
    if "flat" in tokens:
        return FrameKind.FLAT
    if "bias" in tokens or "offset" in tokens:
        return FrameKind.BIAS
    if path.suffix.lower() in SUPPORTED_SUFFIXES:
        return FrameKind.LIGHT
    return FrameKind.UNKNOWN


def build_manifest(input_root: Path) -> SessionManifest:
    """Build a read-only manifest and non-executable dry-run plan."""
    if not input_root.exists():
        raise ManifestInputError(input_root, "path does not exist")
    if not input_root.is_dir():
        raise ManifestInputError(input_root, "path is not a directory")

    records: list[ImageRecord] = []
    candidates = (
        candidate
        for candidate in input_root.rglob("*")
        if candidate.is_file() and candidate.name not in IGNORED_METADATA_FILENAMES
    )
    for path in sorted(candidates):
        relative_path = path.relative_to(input_root)
        metadata_status: Literal["parsed", "pending", "invalid"] = "pending"
        metadata: FitsMetadata | None = None
        metadata_error: str | None = None
        if is_fits(relative_path):
            try:
                metadata = read_fits_metadata(path)
            except FitsHeaderError as error:
                metadata_status = "invalid"
                metadata_error = str(error)
            else:
                metadata_status = "parsed"
        records.append(
            ImageRecord(
                relative_path=relative_path.as_posix(),
                kind=_classify(relative_path),
                suffix=path.suffix.lower(),
                size_bytes=path.stat().st_size,
                sha256=_sha256(path),
                metadata_status=metadata_status,
                metadata=metadata,
                metadata_error=metadata_error,
            ),
        )

    counts = {
        kind: sum(record.kind is kind for record in records) for kind in FrameKind
    }
    blocking_checks = tuple(
        check
        for check, failed in (
            ("has_light_frames", counts[FrameKind.LIGHT] == 0),
            ("known_frame_types", counts[FrameKind.UNKNOWN] > 0),
            (
                "fits_headers",
                any(record.metadata_status == "invalid" for record in records),
            ),
            ("fits_metadata_consistency", _has_inconsistent_metadata(records)),
        )
        if failed
    )
    status: Literal["ready_for_review", "blocked"] = (
        "blocked" if blocking_checks else "ready_for_review"
    )
    pending_checks = ["tool_versions", "models_and_license"]
    if any(record.metadata_status == "pending" for record in records):
        pending_checks.insert(0, "raw_metadata")
    return SessionManifest(
        schema_version="0.1",
        input_root=str(input_root.resolve()),
        files=tuple(records),
        counts=counts,
        preflight=Preflight(
            status=status,
            blocking_checks=blocking_checks,
            pending_checks=tuple(pending_checks),
        ),
        plan=DryRunPlan(
            steps=(
                "validate_fits_headers",
                "siril_calibrate_register_stack",
                "rc_astro_bxt_sxt_nxt",
                "qa_and_report",
            ),
            requires_approval=True,
            execution_enabled=False,
        ),
    )


def _has_inconsistent_metadata(records: list[ImageRecord]) -> bool:
    signatures = {
        (
            record.metadata.width,
            record.metadata.height,
            record.metadata.bitpix,
            record.metadata.bayerpat,
        )
        for record in records
        if record.metadata is not None
    }
    return len(signatures) > 1


def _json_ready(manifest: SessionManifest) -> str:
    """Serialize the typed manifest without exposing Enum objects to JSON."""
    payload = asdict(manifest)
    payload["counts"] = {kind.value: count for kind, count in manifest.counts.items()}
    payload["files"] = [
        {**asdict(record), "kind": record.kind.value} for record in manifest.files
    ]
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main(input_root: Path, output: Path | None = None) -> None:
    """Build and print or save a manifest at the CLI boundary."""
    import typer  # noqa: PLC0415 - optional CLI dependency loaded only at the boundary

    try:
        manifest = build_manifest(input_root)
    except ManifestInputError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=2) from error

    serialized = _json_ready(manifest)
    if output is None:
        typer.echo(serialized, nl=False)
        return
    output.write_text(serialized, encoding="utf-8")
    typer.echo(f"manifest written: {output}")


if __name__ == "__main__":
    import typer

    typer.run(main)
