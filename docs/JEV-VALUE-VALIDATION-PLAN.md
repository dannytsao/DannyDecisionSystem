# DDS × Jev Value Validation Plan

Status: Final evidence consolidation; production routing unchanged. See the
[validation report](JEV-VALUE-VALIDATION-REPORT.md) for the current GitHub
artifact-backed decision.

## Decision question

Does Jev fill a real DDS gap: decisions that are too semantic for rigid rules but too bounded to justify a large LLM call?

## Baseline

DDS remains the source of truth and executes normally. Jev runs in shadow mode only.

The repository currently has no callable DDS Runtime. The limited hard-rule
adapter is a coverage diagnostic only; a full baseline and safe live fallback
remain unmeasured. Adapters must not receive retrospective `expected` labels.

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

## Current measured shadow checkpoint (2026-09-29)

The latest provider run is [36519519841](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36519519841)
at branch commit `a9f5910`. Its [Jev](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36519519841/artifacts/11012565204),
[Cheap LLM](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36519519841/artifacts/11012328156),
[Hybrid](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36519519841/artifacts/11012163647),
and [offline](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36519519841/artifacts/11012013722)
artifacts contain the current per-case rows. No expected labels or risk labels
are sent to adapters.

- Cheap LLM: 36/36 resolved, 91.67% accuracy, 0 critical wrong routes,
  2,750 input tokens, and `$0.0069263` measured provider cost. Language
  accuracy is EN 84.62%, mixed 90.91%, and zh-TW 100%.
- Hybrid: 36/36 resolved, 97.22% accuracy, and 0 critical wrong routes.
  Language accuracy is EN 92.31%, mixed 100%, and zh-TW 100%. Reported
  token/cost coverage is only 41.67% (1,129 tokens; `$0.00380045`), so this is
  not complete end-to-end Hybrid cost. The current scorer also does not expose
  Jev-versus-fallback chain-call counts.
- Direct Jev: 94.44% direct accuracy and 100% accuracy on 22 high-confidence
  cases. Fourteen low-confidence cases remain unresolved because no callable DDS
  Runtime fallback exists; safe accuracy is therefore 61.11%.
- DDS baseline: only the explicit hard-rule diagnostic is executable; it covers
  2/12 golden cases (16.7%). Full DDS accuracy remains unavailable.

This checkpoint is **HOLD** for production adoption. A prior completed run on
the same dataset produced Cheap LLM 94.44% and Hybrid 91.67%; the latest run
produced 91.67% and 97.22%. This run-to-run variance is itself evidence that a
single run cannot establish a winner. The live Jev job remains
red because its safe fallback acceptance gate correctly exposes unresolved
cases; that failure is evidence of the missing Runtime fallback, not a reason
to lower the confidence threshold. The complete per-use-case recommendation is
in [JEV-VALUE-VALIDATION-REPORT.md](JEV-VALUE-VALIDATION-REPORT.md).

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
