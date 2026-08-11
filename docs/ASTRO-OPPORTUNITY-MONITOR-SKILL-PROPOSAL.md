# Astro Opportunity Monitor Skill Proposal

## Name

`monitor-astro-opportunity`

## Problem

Repeatedly assess a variable observing location, date range and astronomy target, then deliver one current, reviewable report on a bounded schedule.

## Type

- [ ] Decision Skill
- [x] Supporting Skill
- [ ] Shared Utility
- [ ] Independent Tool

This Skill coordinates scheduling and delivery. `plan-astro-photo-session` remains the only owner of dated Astro Go／No-Go decisions.

## Inputs and Evidence

- location name and coordinates;
- observing target;
- forecast window;
- schedule active dates, frequency, run time and timezone;
- delivery method and recipient;
- current evidence required by `plan-astro-photo-session` on every run.

## Output

- normalized schedule summary;
- durable Scheduled task prompt;
- one multi-night Traditional Chinese report per run;
- one delivery status without duplicate sending.

## Risk and Failure Cost

Stale evidence can cause unnecessary travel or unsafe plans. Unbounded scheduling can create report noise. Uncertain email retries can produce duplicate messages.

## Existing Overlap

Reuse `plan-astro-photo-session` for evidence, risk, confidence and decisions. This Skill adds only scheduling, multi-night orchestration and delivery behavior.

## Pilot

1. Daily 08:00 Asia/Taipei, bounded season, next five nights, Milky Way, email to `me`.
2. Weekly meteor-shower monitor with an ambiguous location; do not schedule until the location is resolved.
3. Missing current evidence or uncertain email delivery; send or preserve one `Defer` report without retrying uncertain delivery.

## Decision

- [x] Accept for Pilot
- [ ] Merge with Existing Capability
- [ ] Keep Independent
- [ ] Reject

Danny explicitly requested creation on 2026-08-11.

## Current status

- The Skill implementation is complete and covers guided setup, mandatory observing targets, bounded recurring runs, and delivery verification.
- Run reports use a conclusion-first format with one readable card per night instead of a wide table with long prose in cells.
- Email delivery requires a non-empty UTF-8 report body, post-send readback, recipient/body verification, and Inbox visibility for self-delivery.
- Creating this Skill alone does not automatically create a live Scheduled task or send an email; live schedules are configured separately.
