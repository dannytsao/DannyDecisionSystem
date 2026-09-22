# DDS × Jev Value Validation Plan

Status: Proposed experiment; production routing unchanged.

## Decision question

Does Jev fill a real DDS gap: decisions that are too semantic for rigid rules but too bounded to justify a large LLM call?

## Baseline

DDS remains the source of truth and executes normally. Jev runs in shadow mode only.

## Phases

1. Golden benchmark: validate bounded decision behavior.
2. Historical regression: replay 30–50 real DDS decision states.
3. Adversarial/failure tests: ambiguous evidence, long irrelevant context, timeout, invalid response, low confidence.
4. Cost/runtime comparison: compare total task cost, LLM/search/tool calls, retries, pipeline steps and latency.
5. Decision: GO / HOLD / REJECT.

## Ground truth

Baseline output is not automatically ground truth. Ground truth comes from observed task outcome plus retrospective review. Extra research that did not materially change the answer counts as avoidable work.

## Metrics

Decision quality:
- overall accuracy
- high-confidence accuracy
- false FINISH
- false CONTINUE
- wrong route
- critical wrong route

Efficiency:
- LLM calls
- search/tool calls
- retries
- pipeline steps
- total latency
- total task cost

Architecture:
- new modules/dependencies/configuration
- new failure paths
- fallback success
- maintenance burden

## Production gate

GO only if decision quality is not worse than baseline, high-confidence accuracy is >=95%, critical wrong routes and hard-rule violations are zero, fallback is reliable, and at least two efficiency measures materially improve.

HOLD if quality is good but savings are unclear. REJECT if high-confidence errors are unsafe, runtime cost is not reduced, or architecture complexity outweighs benefit.

## DDS boundary

Code/policy owns deterministic and authority rules. Jev may handle bounded semantic gates. LLMs own open-ended reasoning. Jev must remain a replaceable adapter and never become a required runtime dependency.

## External references

### jev-codex-router

- Repository: https://github.com/0xNatoshi/jev-codex-router
- Purpose: per-call Codex model and reasoning-effort routing driven by Jev.
- Relevance to DDS validation:
  - Uses a compact bounded decision state rather than sending Jev the full executor context.
  - Implements fail-open fallback and a kill switch.
  - Logs routing decisions for later calibration.
  - Supports shadow mode and an all-Sol baseline cohort.
  - Measures model distribution, latency, cache behavior, token usage and counterfactual cost.
  - Its published historical ≈60% saving is explicitly a simulation under an older policy, so DDS must not treat that figure as proof of current savings.
- DDS test mapping: NextAction / ModelRouter, confidence calibration, fallback behavior, shadow-mode measurement and cost counterfactuals.
- Added for reference: 2026-09-22.
