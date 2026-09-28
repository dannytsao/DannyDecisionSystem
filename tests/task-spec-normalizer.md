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

## Failure conditions

Fail if the Skill fabricates a requirement, blocks on a non-material presentation field, reports ready with a material input missing, changes the requested outcome, or makes a downstream decision instead of normalizing the task.
