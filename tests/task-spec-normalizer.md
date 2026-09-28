# Task Specification Normalizer Pilot

Status: Pilot candidate. Acceptance requires three representative cases.

## Case 01 — Clear request; no unnecessary clarification

Input: Compare SQLite and PostgreSQL as a DDS state store. Cover reliability, operational complexity, migration cost, and fit with the current DDS architecture. Return Markdown.

Expected: goal preserves the comparison request; success criteria include all four requested dimensions; output format is Markdown; tone, role, and communication style may remain null; missing_required_inputs is empty; ready_to_execute is true; no clarification is emitted merely for missing tone or role.

## Case 02 — Material deployment inputs missing

Input: Deploy this for me.

Expected: do not invent repository or deployment target; mark unavailable repository/source and deployment target as material missing inputs; ready_to_execute is false; ask only blocking questions with concise choices plus D. 我自己填 when reasonable; do not perform or authorize deployment.

## Case 03 — Clear handoff with optional presentation gaps

Input: Review https://github.com/example/tool for DDS adoption. Determine overlap, integration risk, and whether it should be a Skill, utility, external tool, or rejected. Do not modify DDS.

Expected: record URL as available data and no-modification as a constraint; preserve requested dimensions and classification choices; do not invent a numeric rubric; ready_to_execute is true; do not itself choose the adoption outcome.

## Case 04 — Real-world GitHub adoption request (observed)

Observed user input:

> 評估以下這個github 適合安裝嗎？ https://github.com/DeusData/codebase-memory-mcp

Observed normalized contract:

- Goal: evaluate whether `DeusData/codebase-memory-mcp` is worth installing and whether it adds useful code-intelligence capability to DDS/development workflows.
- Success criteria: explain core capability; identify DDS overlap; assess Agent/Mac development-workflow fit; assess security/permission risk; classify the integration boundary; propose a low-risk validation path.
- Constraints: evaluation does not authorize installation; do not modify DDS `main`; do not make a third-party tool a DDS core dependency merely because it is useful.
- Available data: repository URL plus trusted DDS repository context.
- Missing required inputs: none.
- Confidence: high.
- `ready_to_execute: true`.

Observed behavior:

- No clarification was requested for role, tone, communication style, or output format.
- The downstream evaluation was able to proceed from the normalized request.
- The downstream conclusion remained outside the Normalizer: it treated CBM as an external MCP/code-intelligence adapter candidate and proposed an A/B validation rather than silently installing it.

Pilot evidence result: **PASS for this observed case**. It demonstrates the intended behavior for a terse but materially sufficient real-world request. It does not by itself satisfy independent review or the remaining Pilot cases.

## Case 05 — Terse GitHub request resolved from trusted conversation context (observed)

Observed user input:

> 幫我看看這個 https://github.com/MaximeRivest/tiny-classifiers

Trusted current context:

- The immediately preceding Pilot established a recurring task: evaluate a GitHub project for DDS relevance, installation/adoption fit, risks, and whether a separate validation is warranted.
- The user had explicitly chosen to continue real-world `task-spec-normalizer` Pilot cases.

Observed normalized contract:

- Goal: evaluate `MaximeRivest/tiny-classifiers` for DDS relevance and determine whether it warrants installation/adoption or a bounded Pilot.
- Success criteria: explain the mechanism; compare it with current DDS decision engines, especially Jev/hard-rule/LLM routing; identify prerequisites and maturity requirements; avoid installing before value is demonstrated.
- Constraints: do not treat the repository as a DDS dependency merely because it is relevant; do not install or train a model without a separate evidence gate.
- Available data: repository URL, current DDS/Jev validation context, and the established GitHub-evaluation task context.
- Missing required inputs: none.
- Assumption: the terse phrase `幫我看看這個` continues the immediately established GitHub-to-DDS suitability/Pilot evaluation.
- Confidence: high.
- `ready_to_execute: true`.

Observed behavior:

- No clarification was requested because trusted immediate context resolved the otherwise ambiguous phrase.
- The assumption was narrow, explicit, and reversible rather than an invented new objective.
- The downstream evaluation remained separate from normalization and proposed a Tiny Classifier feasibility gate instead of installation.

Pilot evidence result: **PASS for this observed case**. This case specifically tests context-aware normalization: a terse request can execute when trusted current context materially disambiguates it. It does not permit unrelated historical context to be used to manufacture intent.

## Failure conditions

Fail if the Skill fabricates a requirement, blocks on a non-material presentation field, reports ready with a material input missing, changes the requested outcome, or makes a downstream decision instead of normalizing the task.
