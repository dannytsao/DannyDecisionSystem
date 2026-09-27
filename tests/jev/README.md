# Jev Value Validation for DDS

Status: Shadow-mode benchmark scaffold. It does not change production DDS routing.

## Baseline boundary

This repository specifies DDS policy in Markdown but does not contain a callable
DDS Runtime decision implementation. `dds_policy_adapter.py` executes only
explicit hard-rule facts for approval and fresh evidence; all other cases
abstain. It is a **partial policy diagnostic**, not a measured full DDS baseline.
It never reads `expected`. The four-way runner sends only decision inputs to
adapters and reports decision coverage; accuracy is `null` for incomplete arms.

```bash
python3 tests/jev/four_way.py --dataset golden --arm dds_baseline \
  --command "python3 tests/jev/dds_policy_adapter.py"
```

For a real baseline, provide a command that executes the DDS Runtime and emits
one JSON row per input row. Configure it with `FOURWAY_DDS_BASELINE_CMD` or
`--command`. The two explicit `policy_facts` in the golden dataset describe
input state, not target labels. Add equivalent facts only from source evidence,
without consulting the expected outcome.

The live Jev fallback currently abstains when no DDS Runtime is connected.
An unresolved fallback fails the safety gate; fixture success is not evidence.

The shadow Hybrid adapter runs hard rules first, then a configured Jev command,
then a configured Cheap LLM command when Jev fails or confidence is below 0.90.
Commands exchange one decision JSON row per case via stdin/stdout. Set
`HYBRID_JEV_CMD` and `HYBRID_LLM_CMD` to real provider adapters before measuring;
without them, semantic cases abstain and cost stays unmeasured. This does not
select a model or provide DDS Runtime fallback behavior.

`cheap_llm_adapter.py` is the executable provider-neutral Cheap LLM boundary.
It accepts the same sanitized JSONL input as the four-way runner and supports
either `CHEAP_LLM_PROVIDER_CMD` (a command that returns one JSON decision) or an
OpenAI-compatible endpoint configured with `CHEAP_LLM_API_URL`,
`CHEAP_LLM_API_KEY`, and `CHEAP_LLM_MODEL`. It abstains when neither provider
is configured. `CHEAP_LLM_INPUT_USD_PER_MILLION` and
`CHEAP_LLM_OUTPUT_USD_PER_MILLION` are optional provider-declared rates; cost
remains null unless both rates and token usage are present.

Run the offline adapter contract with:

```bash
python3 tests/jev/four_way.py --dataset historical --arm cheap_llm \
  --command "python3 tests/jev/cheap_llm_adapter.py"
```

## Configure measured GitHub Hybrid runs

The workflow reads one provider route at a time. The recommended route is an
OpenAI-compatible endpoint:

```bash
gh secret set CHEAP_LLM_API_KEY --repo dannytsao/DannyDecisionSystem
gh variable set CHEAP_LLM_API_URL --repo dannytsao/DannyDecisionSystem \
  --body "<provider chat-completions URL>"
gh variable set CHEAP_LLM_MODEL --repo dannytsao/DannyDecisionSystem \
  --body "<provider model identifier>"
gh variable set CHEAP_LLM_LIVE_ENABLED --repo dannytsao/DannyDecisionSystem \
  --body "true"
```

Use the exact endpoint and model identifier documented by the provider. Keep
the API key in the secret, never in a repository variable. Optional
`CHEAP_LLM_INPUT_USD_PER_MILLION` and
`CHEAP_LLM_OUTPUT_USD_PER_MILLION` variables may be set only to provider-published
rates; leave them unset when either rate or token usage is unavailable.

The command-provider route is for a checked-in or runner-installed executable
that reads one sanitized JSON object from stdin and writes one JSON decision
object to stdout:

```bash
gh variable set CHEAP_LLM_PROVIDER_CMD --repo dannytsao/DannyDecisionSystem \
  --body "python3 path/to/provider_adapter.py"
gh variable set CHEAP_LLM_LIVE_ENABLED --repo dannytsao/DannyDecisionSystem \
  --body "true"
```

Do not set `CHEAP_LLM_PROVIDER_CMD` when using the HTTP route. After either
route is configured, trigger the validation workflow on the validation branch:

```bash
gh workflow run jev-validation.yml \
  --repo dannytsao/DannyDecisionSystem --ref jev-value-validation
gh run list --repo dannytsao/DannyDecisionSystem \
  --workflow jev-validation.yml --limit 3
gh run watch <run-id> --repo dannytsao/DannyDecisionSystem
```

The `live-cheap-llm` and `live-hybrid` jobs are gated by both
`JEV_LIVE_ENABLED=true` and `CHEAP_LLM_LIVE_ENABLED=true`. They upload measured
historical EN, zh-TW, and mixed results. The existing `live-jev` job may still
remain red while DDS baseline fallback is unresolved; that is evidence for a
HOLD, not a provider-cost or accuracy result to be hidden.

## Purpose

Test whether Jev adds measurable value specifically in the gap between deterministic DDS rules and expensive open-ended LLM reasoning.

Primary gates:
- Completion: FINISH / CONTINUE
- Complexity: FAST_PATH / DEEP_REASONING
- Evidence/adoption routing
- Governance/build classification

Hard rules such as irreversible-action approval remain DDS policy and are included only as anti-Jev controls.

## Run

```bash
python3 tests/jev/benchmark.py --provider fixture
```

For a live Jev run, configure `TYPESAFE_API_KEY` and the official SDK:

```bash
python3 tests/jev/benchmark.py --provider jev
```

Live CI remains disabled until the credentials and a real fallback path are ready. No production DDS path depends on it.

## Acceptance gate

- Golden accuracy >= 90%
- High-confidence (>= 0.90) accuracy >= 95%
- Critical wrong route = 0
- Hard-rule violation = 0
- Jev failure must fall back without breaking DDS
- Historical comparison must improve at least two of: LLM calls >=20%, pipeline steps >=20%, retries >=25%, latency >=20%, without degrading final decision quality.

Cost comparison is total task cost, not Jev-vs-LLM unit price.
