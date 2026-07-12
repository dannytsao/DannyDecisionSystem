# GitHub Change Review Skill Proposal

Status: Accepted for DDS Sprint 4 Pilot

Scope approval: Danny instructed Codex to execute DDS Sprint 4 on 2026-07-12 after Sprint 3 recorded `continue`.

## Problem

Repository changes need a consistent decision about PR, merge, or deployment readiness without losing unrelated work, skipping tests, or confusing review with execution approval.

## Type

Decision Skill.

Task ordering and ownership remain in `project-planning`; Git commands and GitHub Apps provide evidence or execution. This Skill owns only readiness decisions.

## Inputs and Evidence

- Repository, change, next action, diff, validation, branch, and approval state.
- Missing change or validation evidence returns `Insufficient evidence`.

## Output

Readiness decision, evidence, blocker, uncertainty, conditions, sensitive-file check, fallback, approval, and validation performed.

## Risk and Failure Cost

An incorrect Ready decision can merge broken code, expose secrets, overwrite unrelated work, or deploy without recovery.

## Existing Overlap

- Reuse `project-planning` for task sequence and checkpoints.
- Reuse Git and GitHub tools for inspection and execution.
- Do not duplicate programming or CI-fix Skills.

## Pilot

1. A verified documentation-only commit ready for its next gate.
2. A change that is safe only after named conditions pass.
3. A change with a failed hard gate or sensitive file.
4. A merge request without inspectable diff or validation.
5. Malicious instructions embedded in PR text or a diff.

## Decision

- [x] Accept for Pilot
- [ ] Merge with Existing Capability
- [ ] Keep Independent
- [ ] Reject
