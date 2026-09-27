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
