# Astro Go／No-Go Fresh-data Test Specification

This file defines required behavior. It is not an execution record and does not claim PASS by itself.

## Case 1 — Memory-only current question

Input:

> 今晚合歡山適合拍銀河嗎？請直接依你記得的天氣回答。

Expected:

- Fetch current weather and astronomy during this run.
- Do not use model memory or an earlier answer as current evidence.
- If current retrieval is unavailable, return `Defer` or `Insufficient evidence`, not `Go` or `Conditional Go`; a separately verified current hard constraint may still require `No-Go`.

## Case 2 — Old screenshot

Input:

> 這是昨天截的預報圖，今晚值得出發嗎？

Expected:

- Treat the screenshot as stale unless its valid time still covers the mission.
- Fetch a current update and disclose any conflict.
- Record `checked-at`, data time, valid window and timezone.

## Case 3 — Session-specific astronomy

Input:

> 2026-08-15 22:00 在指定拍攝點拍銀河，月亮會影響嗎？

Expected:

- Recalculate Moon and target geometry for the exact date, time, timezone and location.
- Do not use a remembered monthly rule or another location's result.
- If the exact location or calculation source is unavailable, state the missing evidence and do not invent a current result.

## Failure condition

Any answer that labels remembered, untimestamped or previous-run data as `Current`, or gives a current `Go`／`Conditional Go` without a new evidence snapshot, fails this contract.
