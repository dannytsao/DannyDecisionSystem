# ruff: noqa: INP001, S101, CPY001

"""Behavior tests for tile QA summaries and contact sheets."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))
SPEC = importlib.util.spec_from_file_location("tile_qa", SCRIPT_DIR / "tile_qa.py")
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
EXPECTED_TOTAL_FRAMES = 3
EXPECTED_SELECTED_FRAMES = 2


def _write_tile(root: Path, tile_id: str, selected: tuple[int, ...]) -> None:
    """Create a minimal completed tile run fixture."""
    tile = root / tile_id
    process = tile / "process"
    process.mkdir(parents=True)
    total = max(selected) + 1
    lines = [f"#S 'light_' 1 {total} {len(selected)} 5 1 6 0 0 0"]
    lines.extend(f"I {index} {int(index in selected)}" for index in range(1, total + 1))
    (process / "light_.seq").write_text("\n".join(lines) + "\n", encoding="utf-8")
    conversion = "\n".join(
        f"'source-{index:02d}.fit' -> '../process/light_{index:05d}.fit'"
        for index in range(1, total + 1)
    )
    (process / "light_conversion.txt").write_text(conversion + "\n", encoding="utf-8")
    (tile / "manifest.json").write_text(
        json.dumps({"files": [{"relative_path": f"Lights/source-{index:02d}.fit"}
                               for index in range(1, total + 1)]}),
        encoding="utf-8",
    )
    (tile / "result_linear.fit").write_bytes(b"SIMPLE")
    (tile / "result_linear.dng").write_bytes(b"DNG")
    Image.new("RGB", (40, 20), color=(100, 120, 140)).save(tile / "result_preview.png")


def test_build_tile_qa_marks_low_registration_for_review(tmp_path: Path) -> None:
    """Given a completed tile, QA reports selected frames and review status."""
    _write_tile(tmp_path, "2025-10-04_IRCUT_tile-01", (1, 2))

    report = MODULE.build_tile_qa(
        tmp_path / "2025-10-04_IRCUT_tile-01", threshold=0.8,
    )

    assert report.total_frames == EXPECTED_TOTAL_FRAMES
    assert report.selected_frames == EXPECTED_SELECTED_FRAMES
    assert report.registration_ratio == EXPECTED_SELECTED_FRAMES / EXPECTED_TOTAL_FRAMES
    assert report.status == "需複查"
    assert report.rejected_frames == ("source-03.fit",)


def test_write_tile_qa_creates_markdown_json_and_contact_sheet(tmp_path: Path) -> None:
    """Given tile previews, the QA writer creates review artifacts."""
    _write_tile(tmp_path, "2025-10-04_IRCUT_tile-01", (1, 2, 3))
    _write_tile(tmp_path, "2025-10-04_IRCUT_tile-02", (1,))

    artifacts = MODULE.write_tile_qa(tmp_path, threshold=0.8)

    assert artifacts.markdown_path.is_file()
    assert artifacts.json_path.is_file()
    assert artifacts.contact_sheet_path.is_file()
    assert "需複查" in artifacts.markdown_path.read_text(encoding="utf-8")
    with Image.open(artifacts.contact_sheet_path) as image:
        assert image.width > 0
        assert image.height > 0
