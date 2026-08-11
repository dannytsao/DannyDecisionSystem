# Astro Opportunity Monitor Acceptance Specification

This file defines expected behavior. It does not claim that a live Scheduled task or email delivery has passed.

## Case 1 — Bounded daily monitor

Input:

```yaml
mission:
  location_name: 南橫摩天
  coordinates: 23.201, 121.026
  target: 銀河
  forecast_days: 5
schedule:
  active_from: 2026-08-12
  active_until: 2026-09-30
  frequency: daily
  run_at: "08:00"
  timezone: Asia/Taipei
  missed_run_policy: skip
delivery:
  method: email
  recipient: me
```

Expected:

- Keep the active window, daily cadence and five-day forecast window separate.
- Create a prompt that invokes `plan-astro-photo-session` for every dated night.
- Produce the Scheduled task prompt primarily in Traditional Chinese; retain only required skill names, placeholders, decision tokens, and tool terms in English.
- Send no more than one report per run.
- Do not backfill reports for missed runs.

## Case 2 — Ambiguous location

Input: Every Friday at 08:00, monitor next weekend's Perseids opportunity at「五指山」and email the result.

Expected:

- Do not choose coordinates silently because multiple places may match.
- Resolve or confirm the exact location before creating the schedule.
- Create no Scheduled task and send no email while the location remains ambiguous.

## Case 3 — Missing current evidence

Input: A valid scheduled run can reach only a previous report; current weather, satellite and astronomy cannot be verified.

Expected:

- Do not reuse the previous report as current evidence.
- Return `Defer` or `Insufficient evidence`.
- Preserve the complete report in Scheduled results.
- If email delivery is authorized and available, send one Defer report.

## Case 4 — Uncertain email status

Input: The email tool times out after submission and cannot confirm whether the message was sent.

Expected:

- Do not retry automatically.
- Mark delivery status uncertain.
- Preserve the report in Scheduled results.

## Case 5 — Outside active window

Input: The task is invoked after `active_until`.

Expected:

- Skip astronomy analysis and email.
- Report that the monitor is inactive.
- Do not modify the underlying Astro Decision Skill.

## Case 6 — Conversational setup with no inputs

Input: 使用 `$monitor-astro-opportunity` 幫我設定天文機會監測。

Expected:

- Start in Configure mode and respond in Traditional Chinese.
- Ask only for the location in the first turn.
- Give a short example such as「南橫摩天」.
- After the user answers the location, the next question explicitly asks for the observing or photography target.
- Do not ask for dates or frequency, generate a schedule, or create a task before the target is supplied.
- Do not display the full YAML schema, create a Scheduled task, or send email.

## Case 7 — Conversational setup with partial inputs

Input: 每天早上 08:00 幫我監測南橫摩天未來五天的銀河機會。

Expected:

- Retain the supplied location, target, forecast window, frequency, and run time.
- Resolve coordinates without requiring the user to know them; confirm only if the location is ambiguous.
- Ask one short question for the next missing item, starting with the active date range.
- Do not repeat questions for values already supplied.
- Do not generate the final prompt until all settings are summarized and confirmed.

## Case 8 — Confirmed Dry Run

Input: All required values are collected and the user confirms Dry Run only.

Expected:

- Show the normalized configuration summary in Traditional Chinese.
- Generate the completed Scheduled task prompt in Traditional Chinese.
- Leave no unresolved double-brace placeholders.
- Do not create a real Scheduled task or send email.

## Case 9 — Location without target

Input: 設定南橫摩天的天文機會監測。

Expected:

- Retain the supplied location and resolve coordinates as allowed.
- Ask explicitly for the observing or photography target as the next question.
- Do not infer 銀河 or any other target.
- Do not ask for schedule dates or frequency, or create a task, before the target is supplied.

## Case 10 — Email delivery verification

Input: A configured run requests Email delivery to `me`.

Expected:

- Send a non-empty report body with the exact generated subject.
- Search Gmail with that exact subject using `in:anywhere` after sending.
- Read back the matched message and verify the recipient and non-empty body.
- If the message has no `INBOX` label, apply `INBOX` to the exact matched message.
- Report delivery as successful only after all checks pass; otherwise report the failed or uncertain check and preserve the report in Scheduled results.

## Case 11 — Readable run report

Input: A configured run assesses more than one night and the user wants to read the result on mobile.

Expected:

- Start with a one-sentence conclusion and a short overall summary.
- Give each night its own heading/card instead of a wide table.
- Separate the best astronomical time from the practical departure recommendation.
- Present weather, moonlight, and risks as short bullet points.
- Keep the complete report in the Scheduled result; Email uses the same readable format when delivery is enabled.
