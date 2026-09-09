# ruff: noqa: INP001, S101, CPY001, RUF001, EM101

"""Behavior tests for failure reports and FITS companion pairing."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import typer

if TYPE_CHECKING:
    from types import ModuleType

SCRIPT_DIR = Path(__file__).parents[1] / "skills/process-astro-image/scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def _load(name: str, filename: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / filename)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


FAILURE_REPORT = _load("failure_report", "failure_report.py")
EXPORT_DNG = _load("export_dng_sidecars", "export_dng_sidecars.py")
RUN_SIRIL = _load("run_siril", "run_siril.py")
EXIT_FAILURE = 2


def test_failed_report_is_written_with_stable_failure_fields(tmp_path: Path) -> None:
    """Given a failed operation, a report records the operation and reason."""
    target = tmp_path / "m106-manifest.json"

    report = FAILURE_REPORT.write_failed_report(
        target,
        operation="build_manifest",
        reason="fits_headers",
        input_root=tmp_path / "M106",
    )

    assert report == tmp_path / "Failed" / "failed-report.md"
    content = report.read_text(encoding="utf-8")
    assert "狀態：失敗" in content
    assert "建立影像資料清單" in content
    assert "FITS 標頭無法讀取" in content


def test_result_fits_require_matching_dng_or_tiff_sidecars(tmp_path: Path) -> None:
    """Given result FITS files, missing DNG/TIFF companions are reported."""
    (tmp_path / "result.fit").write_bytes(b"fit")
    (tmp_path / "result_linear.fit").write_bytes(b"fit")
    (tmp_path / "result_linear.dng").write_bytes(b"dng")

    assert EXPORT_DNG.missing_result_companions(tmp_path) == (tmp_path / "result.fit",)


def test_dng_sidecar_path_preserves_result_stem(tmp_path: Path) -> None:
    """Given a FITS result name, its DNG sidecar uses the identical stem."""
    fit = tmp_path / "result_autostretched.fit"

    assert EXPORT_DNG.dng_sidecar_path(fit) == (
        tmp_path / "result_autostretched.dng"
    )


def test_tiff_fallback_is_used_when_dnglab_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Given no DNGLab, the exporter writes a validated TIFF companion."""
    (tmp_path / "result.fit").write_bytes(b"fit")
    siril = tmp_path / "siril-cli"

    def resolve_tool(_explicit: Path | None, name: str) -> Path:
        if name == "siril-cli":
            return siril
        raise EXPORT_DNG.DngExportError("tool_missing", "dnglab unavailable")

    def fake_tif_export(
        _siril: Path,
        _root: Path,
        _fit: Path,
        tif_path: Path,
    ) -> Path:
        tif_path.write_bytes(b"II*\x00")
        return tif_path

    monkeypatch.setattr(EXPORT_DNG, "_find_tool", resolve_tool)
    monkeypatch.setattr(EXPORT_DNG, "_run_siril_tif", fake_tif_export)

    outputs = EXPORT_DNG.export_dng_sidecars(tmp_path)

    assert outputs == (tmp_path / "result.tif",)
    assert (tmp_path / "result.tif").read_bytes() == b"II*\x00"


def test_siril_runner_writes_failed_report_when_script_is_missing(
    tmp_path: Path,
) -> None:
    """Given a missing Siril script, the runner writes a failed report."""
    with pytest.raises(typer.Exit) as caught:
        RUN_SIRIL.main(tmp_path / "missing.ssf", tmp_path)

    assert caught.value.exit_code == EXIT_FAILURE
    assert (tmp_path / "Failed" / "failed-report.md").is_file()
