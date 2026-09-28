# Codebase Memory MCP — DDS A/B Validation

Status: validation plan; no installation authorized by this document.

## Objective

Determine whether `DeusData/codebase-memory-mcp` (CBM) materially improves DDS repository understanding for coding agents without creating unacceptable configuration, background-process, security, or maintenance cost.

CBM remains an external code-intelligence/MCP adapter candidate during this validation. It is not a DDS Skill or Runtime dependency.

## Scope

Repository under test: `dannytsao/DannyDecisionSystem`.

A = existing agent workflow without CBM (GitHub/file search and targeted reads).
B = the same questions with CBM indexed against the same repository revision.

Use the same repository commit, question wording, agent/model where practical, and evidence standard for both arms. Do not let the B arm see the A answer.

## Pre-install security gate

Before running B:

1. Record the exact CBM release/version and artifact checksum/provenance used.
2. Review the installer before execution; do not pipe a remote script directly to a shell for this Pilot.
3. Prefer a binary-only or isolated setup first when available; record every Agent configuration file the installer would change.
4. Record background services/processes, cache/index locations, localhost ports, update checks, and uninstall/rollback steps.
5. Confirm no source-code upload or external telemetry is required for indexing/query operation; record any network behavior observed.
6. Stop if installation requires broader filesystem or configuration changes than the Pilot owner accepts.

Passing this gate permits only the B-arm Pilot. It does not approve permanent installation.

## Benchmark questions

Run at least these six questions in both arms:

1. List all current DDS Skills and classify each as Decision or Supporting where repository evidence permits.
2. Trace the repository rules that govern adding a new Skill, from admission through validation and review.
3. Identify files and repository contracts that would be affected if `standards/skill-admission.md` changed materially.
4. Explain how `project-planning` is specified and which tests/evidence validate it.
5. Determine whether a proposed request-normalization capability overlaps an existing DDS Skill or fills a distinct gap.
6. Identify whether the current Jev validation work touches production DDS Skill/Runtime files or is isolated validation work.

Questions 1-4 emphasize structural retrieval. Questions 5-6 test cross-file reasoning and boundary detection.

## Measurements

For every question capture:

| Metric | A: without CBM | B: with CBM | Rule |
| --- | --- | --- | --- |
| Answer correctness | | | Verify against repository source of truth |
| Evidence completeness | | | Required claims point to the relevant files |
| Incorrect/hallucinated claims | | | Count material unsupported claims |
| Tool calls | | | Count retrieval/query calls used to reach final answer |
| Files/content reads | | | Count distinct repository files materially read |
| Context/tokens | | | Record when the client exposes a comparable measure; otherwise N/A |
| Elapsed time | | | Wall-clock from question start to answer |
| Recovery needed | | | Note failed queries, re-indexing, or manual fallback |

Do not invent unavailable token or latency measurements. Mark them N/A.

## Acceptance gate

Recommend continued CBM use only if the B arm:

- preserves or improves correctness on all material repository-boundary questions;
- introduces no material unsupported claims that the A arm avoids;
- shows a repeatable reduction in retrieval work (tool calls and/or file reads) on structural questions;
- remains operationally understandable and reversible after the security gate;
- does not require DDS Runtime, Skill, or governance changes merely to function.

Do not require a made-up percentage improvement. Record the observed deltas and make the adoption decision from evidence.

## Stop / rollback conditions

Stop the Pilot and remove/disable the B setup if:

- source or repository metadata is unexpectedly transmitted externally;
- installer/configuration changes cannot be bounded or cleanly reversed;
- indexing materially interferes with normal Agent sessions;
- B produces materially worse repository answers without a clear recoverable cause;
- the tool requires DDS architecture changes before it can demonstrate value.

## Result record

After both arms complete, append:

- repository commit tested;
- CBM version/build and verification evidence;
- environment/client;
- completed measurement table;
- observed configuration/process changes;
- rollback result;
- recommendation: continue Pilot / adopt as optional external adapter / keep independent / stop;
- unresolved risks and next evidence needed.
