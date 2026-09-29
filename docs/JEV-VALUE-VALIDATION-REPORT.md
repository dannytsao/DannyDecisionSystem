# DDS × Jev Value Validation Report

**Status:** Final evidence consolidation for the validation branch; production
routing is unchanged.

**Verified on:** 2026-09-29 (Asia/Taipei)

**Source of truth:** GitHub repository state at [`jev-value-validation` /
`37ad329`](https://github.com/dannytsao/DannyDecisionSystem/tree/jev-value-validation),
PR [#4](https://github.com/dannytsao/DannyDecisionSystem/pull/4), and the
latest PR Actions run [#36398968862](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36398968862).

PR #4 is still Draft. `main` is still `6b409586`. No production DDS files
were changed.

## Decision

**Overall: HOLD for production adoption; GO only for bounded, non-authoritative
shadow/canary use.**

The evidence is sufficient to finish this validation stage, but not to claim
that Jev is a production DDS baseline replacement. Direct Jev is promising at
high confidence, while the safe fallback is unresolved because this repository
still has no callable DDS Runtime. Hybrid is the strongest measured arm, but
its token/cost coverage and provider-chain counters are incomplete.

The intended boundary remains:

```text
DDS deterministic policy → Jev bounded semantic gate → DDS composition → LLM / Tool / Action
```

Jev must not own irreversible actions, approval, permissions, budgets, critical
thresholds, or fresh-information policy. Those remain DDS authority rules.

## Evidence inventory

| Evidence | Current result | Interpretation |
| --- | --- | --- |
| Offline/unit/regression | Success in the latest run's `offline-validation` job | Contract and regression evidence only; fixtures are not provider evidence |
| Live Jev golden | 12/12 direct and safe; 100%; 0 critical wrong routes | Small anti-control/contract sample, not a historical value result |
| Live Jev historical | 36 cases; direct 34/36 (94.44%); 21/21 high-confidence (100%); safe 21/36 (58.33%) | 15 low-confidence cases intentionally abstained because DDS fallback is unavailable |
| Cheap LLM historical | 36/36 resolved; 34/36 (94.44%); 0 critical wrong routes | Complete measured provider arm |
| Hybrid historical | 36/36 resolved; 35/36 (97.22%); 0 critical wrong routes | Best measured quality, with partial chain telemetry |
| DDS baseline | Golden hard-rule adapter resolved 2/12 (16.7%); resolved accuracy 2/2 | Partial policy diagnostic, not a full DDS Runtime baseline |

Artifacts are independently downloadable from the latest run: [Jev](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36398968862/artifacts/10959408243),
[Cheap LLM](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36398968862/artifacts/10959607769),
[Hybrid](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36398968862/artifacts/10958708796),
and [offline results](https://github.com/dannytsao/DannyDecisionSystem/actions/runs/36398968862/artifacts/10959552273).

## Four-arm comparison

| Arm | Coverage / quality | Language slices | Latency | Calls / steps | Tokens / cost | Fallback |
| --- | --- | --- | --- | --- | --- | --- |
| DDS baseline | **Unavailable as a whole-arm measure.** Hard-rule diagnostic: 2/12 golden coverage, 100% on those 2 | No meaningful slice | 0.0014 ms mean over resolved diagnostic rows | 0 LLM; 2 policy steps | 0 measured | Abstains outside explicit facts |
| GPT-5 nano / Cheap LLM | 36/36; 94.44%; 0 critical wrong routes | EN 92.31%, mixed 90.91%, zh-TW 100% | 4,664.6 ms mean; 168.0 s wall | 36 LLM, 0 retries, 36 pipeline steps | 2,750 input tokens; `$0.0078959` measured cost, 100% coverage | None in the measured successful run |
| Jev direct | Historical 34/36 (94.44%); high-confidence 21/21 (100%); 0 direct critical wrong routes | Direct: EN 92.31%, mixed 90.91%, zh-TW 100% | 186.1 ms mean per case (artifact rows) | Provider call telemetry not summarized by the benchmark | Token and cost telemetry unavailable | 15/36 low-confidence fallbacks; all 15 unresolved |
| Hybrid | 36/36; 35/36 (97.22%); 0 critical wrong routes | EN 92.31%, mixed 100%, zh-TW 100% | 2,753.8 ms mean; 99.2 s wall | Artifact reports 36 terminal `llm_calls`; it does not expose Jev-vs-fallback chain calls | 1,048 tokens and `$0.0033464` reported, only 38.9% coverage; not an end-to-end cost | 14 rows carry Cheap LLM token/cost fields; this is inferred from rows, not a first-class counter |

The Hybrid `llm_calls_total=36` value must not be read as “36 calls for the
whole chain.” The adapter invokes Jev first and may then invoke Cheap LLM;
the current four-way scorer preserves only the final adapter row. The 14-row
fallback count above is therefore an explicitly **inferred** observation from
the token/cost-bearing rows, not a complete provider-call measurement.

Likewise, `$0.0033464` is a partial measured field, not complete Hybrid task
cost. Jev does not report token/cost usage in this run, so no missing values are
filled or extrapolated.

## Integrity checks

- The four-way runner sends adapters only `id`, `gate`, `state`, `options`, and
  `policy_facts`; it does not send `expected`, `risk`, or other scoring labels.
- The DDS adapter reads only explicit policy facts and abstains otherwise. Its
  16.7% golden coverage is intentionally reported as partial, not promoted to
  full-baseline accuracy.
- Fixture results are infrastructure checks. They are not provider evidence.
- The live Jev job is red because the acceptance gate rejects unresolved safe
  fallback cases. That failure is valid evidence of the missing DDS Runtime;
  lowering the confidence threshold would hide the risk and was not done.
- The historical set has 36 cases: EN 13, mixed 11, zh-TW 12. It contains no
  critical-risk cases (all are marked medium), so “0 critical wrong routes” on
  this slice is a non-finding, not a safety proof. Golden T11 remains the
  explicit critical hard-rule control.
- The two direct Jev errors are H21 and H33, both low-confidence false
  `FINISH` decisions. No high-confidence direct error was observed.
- Cheap LLM errors are H03 (`FAST_PATH` → `DEEP_REASONING`) and H27
  (`SKILL_FIRST` → `BUILD_APP`). Hybrid retains H03 as its only wrong route.

## By-use-case recommendation

| Use case | Decision | Boundary |
| --- | --- | --- |
| CompletionJudge | **HOLD** | Re-test with a callable DDS fallback; direct Jev has two false `FINISH` cases and safe coverage is incomplete |
| NextAction | **HOLD** | Historical proxy is encouraging, but no executable DDS baseline or action-outcome replay contract exists |
| Complexity Gate | **HOLD** | Hybrid is 5/6 on this slice and misses H03; suitable for shadow/canary advice only |
| Skill / Task Router | **HOLD** | Jev direct was correct on the three build cases, but safe fallback was unresolved on two |
| Tool Router | **HOLD for semantic pre-gate; REJECT as authority** | No tool-execution cohort was measured; DDS must retain permissions and action authority |
| Retry Gate | **HOLD** | Successful runs report zero retries, but timeout/retry behavior is only fixture/unit-tested |
| Model Router | **HOLD** | Complexity results are only a proxy; Hybrid cost and chain-call telemetry are incomplete |
| Approval / risk classification | **HOLD for advisory classification; REJECT for policy ownership** | Jev may classify bounded text, never approve or bypass DDS hard rules |
| General open-ended reasoning | **REJECT** | The experiment evaluates bounded choices, not open-ended reasoning quality |

## What would change HOLD to GO

1. Provide a callable DDS Runtime baseline or an approved manual replay
   contract, with the same sanitized inputs and independently reviewable
   outcomes.
2. Make Hybrid route, Jev-call, fallback-call, retry, and per-provider latency
   counters first-class telemetry rather than inferred from output fields.
3. Capture provider-declared rate metadata alongside token usage, and measure
   complete Hybrid cost or leave the comparison explicitly cost-unavailable.
4. Add critical-risk, tool, retry, timeout, and approval cohorts; the current
   36-case historical slice cannot establish those safety properties.
5. Re-run the acceptance gate and require reliable fallback completion without
   weakening the confidence threshold.

Until then, the defensible outcome is **HOLD**, with **GO only for
shadow/canary, bounded, replaceable semantic gating** and with DDS deterministic
policy remaining authoritative.
