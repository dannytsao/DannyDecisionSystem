# Jev Value Validation for DDS

Status: Shadow-mode benchmark scaffold. It does not change production DDS routing.

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

For a live Jev run, set `JEV_API_KEY` and configure the endpoint/response adapter only after checking the current Jev API contract:

```bash
python3 tests/jev/benchmark.py --provider jev
```

The live provider is intentionally fail-closed until its current API endpoint and response schema are configured. No production DDS path depends on it.

## Acceptance gate

- Golden accuracy >= 90%
- High-confidence (>= 0.90) accuracy >= 95%
- Critical wrong route = 0
- Hard-rule violation = 0
- Jev failure must fall back without breaking DDS
- Historical comparison must improve at least two of: LLM calls >=20%, pipeline steps >=20%, retries >=25%, latency >=20%, without degrading final decision quality.

Cost comparison is total task cost, not Jev-vs-LLM unit price.
