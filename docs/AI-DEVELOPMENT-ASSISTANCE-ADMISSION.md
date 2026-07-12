# AI Development Assistance Admission

Status: Merge with Existing Capability

Scope approval: Danny instructed Codex to execute DDS Sprint 4 on 2026-07-12 after Sprint 3 recorded `continue`.

## Decision

Do not create a separate AI Development Assistance Skill in Sprint 4.

## Why

- General coding belongs to the active Agent or coding runtime.
- `project-planning` already handles task breakdown, dependencies, risks, validation, checkpoints, and stop conditions.
- `review-github-change` handles readiness decisions after implementation.
- Existing programming, debugging, review, Git, and CI tools perform specialist execution.

A new general assistant would repeat these rules without adding a distinct decision.

## Routing

| Need | Existing capability |
| --- | --- |
| Plan the work | `project-planning` |
| Implement or debug | Agent coding tools |
| Review readiness | `review-github-change` |
| Git history or commit | Git tools |
| Fix failing CI | CI-specific tool or Skill |

## Reconsider only when

At least three real cases reveal the same missing AI-development decision that cannot be handled by the existing capabilities.
