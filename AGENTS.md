# DDS Agent Instructions

Read this file before changing the repository.

## Source of truth

Follow, in order:

1. Danny's explicit current instruction.
2. Accepted DDS decisions and checkpoint records.
3. `ROADMAP.md` and `docs/DDS-SPRINT-PLAN.md`.
4. Standards in `standards/`.
5. Existing implementation and tests.

Do not invent a new roadmap, governance layer or architecture when the repository already answers the question.

## Before editing

- Read `README.md`.
- Read `docs/DDS-RUNTIME-AND-INTERFACES.md` for platform boundaries.
- Read `standards/multi-agent-collaboration.md`.
- Confirm the task owner, branch and file scope.
- Check that another active task is not editing the same scope.

## Working rules

- Never work directly on `main`.
- Use one branch for one task.
- Keep changes inside the claimed scope.
- Preserve existing history and accepted terminology.
- Prefer small, reversible changes.
- Do not start a later Sprint without Danny's explicit decision.
- Do not promote one observation into a permanent rule.
- Do not expose secrets, tokens or private data.

## Required handoff

Every PR or handoff must include:

- owner and objective;
- changed files;
- validation performed;
- known risks or missing evidence;
- decisions needed from Danny;
- suggested reviewer.

## Multi-agent behavior

Codex, Claude Code, Kimi, Hermes and other agents are peers using the same repository contract. No Agent may treat its private conversation, memory or generated plan as the source of truth unless it has been accepted and recorded in the repository.

A Builder implements. A separate Reviewer reviews. Danny remains Product Owner for material decisions and acceptance.
