#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

# ─── How to run ───
# This module is imported by the Pilot CLI scripts; run those entry points instead.
# ──────────────────

# ruff: noqa: CPY001, RUF001

"""Write append-only failure reports for every rejected Pilot operation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path  # noqa: TC003 - Path is used at runtime

_OPERATION_NAMES = {
    "build_manifest": "建立影像資料清單",
    "generate_siril_script": "產生 Siril 腳本",
    "run_siril": "執行 Siril 流程",
    "export_dng_sidecars": "產生結果檔案 companion",
    "prepare_tile_runs": "準備視野分組 run",
    "tile_qa": "檢查視野分組品質",
    "plate_solve_tiles": "確認各視野座標",
    "prepare_mosaic_run": "準備 IRCUT mosaic 試作",
    "mosaic_qa": "檢查 mosaic 輸出品質",
    "wcs_mosaic": "執行 WCS 重投影 mosaic",
    "wcs_mosaic_qa": "檢查 WCS mosaic 品質",
}
_REASON_NAMES = {
    "has_light_frames": "找不到 Lights（亮場）檔案",
    "known_frame_types": "發現無法辨識的影像檔案",
    "fits_headers": "FITS 標頭無法讀取",
    "fits_metadata_consistency": "FITS 影像尺寸或格式不一致",
    "raw_metadata": "RAW 檔案 metadata 尚未完成檢查",
    "calibration_mapping": "校準檔尚未完成配對",
    "tool_missing": "找不到必要工具",
    "siril_export": "Siril 無法產生中介影像",
    "dnglab_export": "DNGLab 無法產生 DNG",
    "dng_validation": "產生的 DNG 驗證失敗",
    "tiff_export": "Siril 無法產生 TIFF",
    "tiff_validation": "產生的 TIFF 驗證失敗",
    "companion_export": "DNG 與 TIFF 都無法產生",
    "no_results": "找不到 result*.fit 結果檔",
}


def failed_report_path(target: Path) -> Path:
    """Return the shared Failed-folder report path for an output target."""
    return target.parent / "Failed" / "failed-report.md"


def _simple_operation(operation: str) -> str:
    return _OPERATION_NAMES.get(operation, operation)


def _simple_reason(reason: str) -> str:
    for code, label in _REASON_NAMES.items():
        if code in reason:
            return label
    return "處理工具回報錯誤，請查看下方原始訊息"


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
        f"## 失敗時間：{timestamp}\n\n"
        "- 狀態：失敗\n"
        f"- 做了什麼：{_simple_operation(operation)}\n"
        f"- 原因：{_simple_reason(reason)}\n"
        f"{input_line.replace('input_root', '資料夾')}"
        f"- 原始訊息：`{reason}`\n"
        "- 下一步：修正資料或工具後，再重新執行。\n"
    )
    if report.exists():
        report.write_text(
            report.read_text(encoding="utf-8") + f"\n{entry}",
            encoding="utf-8",
        )
    else:
        report.write_text(f"# Failed Report\n\n{entry}", encoding="utf-8")
    return report
