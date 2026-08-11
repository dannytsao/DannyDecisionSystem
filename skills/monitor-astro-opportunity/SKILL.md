---
name: monitor-astro-opportunity
description: Configure through a guided conversation or run a recurring astronomy and astrophotography opportunity brief for a variable location, forecast date range, observing target, schedule window, execution time, frequency, timezone, and optional email delivery. Use when Codex needs to interview the user for missing schedule parameters, create or update a scheduled astro monitor, execute one scheduled run, or prepare a reusable Scheduled task prompt. Reuse plan-astro-photo-session for every dated Go or No-Go assessment instead of duplicating its weather, astronomy, safety, or confidence rules.
---

# Job to be done

Turn a repeated astronomy question into a bounded Scheduled task that obtains fresh evidence, assesses each requested night, produces one concise report, and optionally emails it once.

Keep three clocks separate:

1. `active window`: when the Scheduled task may run;
2. `cadence`: how often and at what local time it runs;
3. `forecast window`: which future dates each run assesses.

# Required inputs

Require:

```yaml
mission:
  location_name: string
  coordinates: latitude, longitude
  target: string
  forecast_days: integer

schedule:
  active_from: YYYY-MM-DD
  active_until: YYYY-MM-DD | none
  frequency: daily | weekdays | weekly | custom
  run_at: HH:MM
  timezone: IANA timezone
  missed_run_policy: skip

delivery:
  method: scheduled-result | email
  recipient: me | email address
```

`target` is mandatory. Treat it as the observing or photography target, not an
optional description. Examples include `銀河`, `英仙座流星雨`, `10P 彗星`,
`月蝕`, and `火燒雲`. If the user supplies a location but no target, ask for
the target next and do not proceed to dates, cadence, delivery, prompt
generation, or scheduling.

Accept an explicit start and end date instead of `forecast_days` when the user requests a fixed observing interval.

Do not require the user to know coordinates. Ask for the place in ordinary language, resolve it to one coordinate pair, and ask for confirmation when the match is ambiguous or could materially change weather, altitude, horizon, access, or astronomy.

If `active_until` is `none`, state that the task continues until paused. Default `missed_run_policy` to `skip`; do not backfill obsolete reports.

# Modes

## Configure

Use a guided Traditional Chinese conversation.

1. Read the user's message and keep every parameter already provided.
2. Ask only for information that is missing, ambiguous, or contradictory.
3. Ask one short question per turn. Do not present the entire input schema or a long questionnaire.
4. Collect information in this order when it is missing:
   1. location;
   2. observing or photography target (mandatory; ask this immediately after the
      location when it is absent);
   3. forecast window for each run;
   4. schedule start and end dates;
   5. frequency;
   6. local run time;
   7. timezone;
   8. delivery method;
   9. recipient, only when email is selected.
5. Resolve the location to coordinates. Ask the user to choose only when more than one meaningful match remains.
6. Default missed runs to `skip` and explain it in the final summary; do not ask unless the user wants different behavior.
7. If the user is unsure, give two or three simple examples and recommend one practical default.
8. After all inputs are known, show one plain-language summary and ask the user to confirm or correct it.
9. Build the task prompt from [SCHEDULED_TASK_PROMPT.md](references/SCHEDULED_TASK_PROMPT.md) only after confirmation.
10. In Dry Run, display the completed prompt but do not create a Scheduled task or send email.
11. Create or update the Scheduled task only when the user explicitly requests that external change after reviewing the summary.
12. Put the actual recurrence in the Scheduled task configuration. Do not simulate scheduling with sleep loops or hide raw cron commands inside the astronomy rules.
13. Do not send a test email unless the user explicitly requests a test send.

Example first question when no parameters were supplied:

> 你想監測哪一個拍攝地點？請直接輸入地名，例如「南橫摩天」。

If the user answers only with a location, the next question must be:

> 這次要觀測或拍攝什麼標的？例如「銀河」、「英仙座流星雨」或「10P 彗星」。

## Run

1. Stop without emailing when the execution date is outside the active window.
2. Interpret the forecast window relative to the current run date unless the user supplied fixed dates.
3. Use `$plan-astro-photo-session` for every dated assessment. Load its current Skill and evidence policy; never copy or weaken its rules here.
4. Re-fetch current weather, observation, satellite or radar, astronomy, access, and safety evidence during this run.
5. Return `Defer` or `Insufficient evidence` when the core Skill's fresh-data gate cannot be satisfied.
6. Summarize all assessed nights and name the best supported opportunity, or say none is currently worth recommending.
7. Deliver the report through the authorized method.

# Email delivery

Treat a saved Scheduled task that explicitly names automatic email delivery and its recipient as standing authorization for that delivery only.

- Send at most one email per run.
- Use `me` only for the connected account owner.
- Use subject `DDS｜{location}未來{forecast-window}{target}機會｜{run-date}`.
- Send a non-empty `text/plain` or `text/markdown` body containing the complete report; never call the mail tool with an empty payload.
- After sending, search Gmail with the exact subject using `in:anywhere`, read the matched message, and verify that the recipient and body are present before reporting delivery success.
- When sending to `me`, if the matched message has no `INBOX` label, apply `INBOX` to that exact matched message so the self-delivered report is visible in the inbox.
- If the message is missing, the body is empty, or the label/readback check fails, report `Delivery status: failed` or `uncertain` with the precise reason; do not claim it was sent successfully.
- Send a `Defer` report when critical evidence is unavailable; do not fail silently.
- If send status is uncertain, do not retry. Report `Delivery status: uncertain` in the Scheduled result.
- If sending fails, preserve the complete report in the Scheduled result and report the error.
- Do not add attachments unless the user explicitly requests them.

# Required output

For configuration:

```text
任務：
地點與座標：
拍攝標的：
預判範圍：
排程有效期間：
執行頻率與時間：
時區：
錯過排程處理：
交付方式：
核准狀態：
```

For each run:

```text
結論：
一句話說明是否值得出勤，以及最主要的原因。

整體摘要：
用 2–3 句話先說明天文條件、氣象限制與出勤建議。

## {日期／夜晚}

判斷：Go | Conditional Go | No-Go | Defer
信心度：
天文最佳時段：
出勤建議：

觀測與天氣：
-
-

月光：
-

主要風險：
-
-

最推薦夜晚：
可能改變結論的條件：
道路與安全狀態：
資料來源與新鮮度：
寄送狀態：
```

For run reports, use the conclusion-first card format above. Do not use a wide
Markdown table with long prose in cells: it is difficult to read in email and
on mobile. Keep each night in its own heading, use short bullets, explain why
the astronomical window is or is not actionable, and separate `天文最佳時段`
from `出勤建議`.

Use Traditional Chinese in the report and email.

# Validation

- Keep schedule dates, run cadence, and forecast dates distinct.
- During Configure mode, ask one missing-parameter question per turn and retain answers already supplied.
- Treat `mission.target` as mandatory and non-empty.
- When only the location is known, ask for the target before forecast dates, frequency, delivery, or any scheduling action.
- Do not infer a target from the location, date, weather, or astronomy context, and do not substitute a generic target.
- Do not force the user to provide coordinates when the location can be resolved safely.
- Do not generate the final Scheduled task prompt until the collected settings have been summarized and confirmed.
- Generate the Scheduled task prompt and user-facing configuration summary primarily in Traditional Chinese. Keep only skill names, placeholders, decision tokens, and required tool terms in English.
- For run reports, lead with the decision and use one heading/card per night with short bullets; avoid wide tables with long prose in cells.
- Always separate the best astronomical time from the practical departure recommendation.
- Include a timezone for every schedule.
- Require one exact location before a dated assessment.
- Do not label remembered, cached, or previous-run evidence as current.
- Do not let delivery failure change the astronomy decision.
- Do not create duplicate emails after an uncertain send.
- Do not create or modify a Scheduled task without explicit user authorization.

# Failure handling

- Missing schedule input: ask for the next missing field in conversational order; do not dump the entire missing-field list.
- Missing target: ask explicitly for the observing or photography target; do not continue or create a task.
- Ambiguous location: request or resolve the exact place before scheduling.
- Expired active window: skip analysis and email; report that the task is inactive.
- Unavailable current evidence: complete a `Defer` or `Insufficient evidence` report.
- Unavailable email tool: keep the report in Scheduled results and mark delivery failed.
- Unsupported cadence: propose the nearest supported schedule and wait for approval.
