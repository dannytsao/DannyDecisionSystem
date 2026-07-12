# Project Planning Skill Proposal

Status: Accepted for DDS Sprint 2 Pilot

Scope approval: Danny instructed Codex to execute DDS Sprint 2 on 2026-07-12 after the two candidates and Pilot gate were documented in the Roadmap.

## Problem

Project goals need a small, evidence-based order of work with clear exit gates, checkpoints, and protection against scope creep.

## Type

Decision Skill. It chooses sequence, defers premature work, and decides when to continue, adjust, defer, or stop.

## Inputs and Evidence

- Goal or problem.
- Repository or project-status sources.
- Relevant constraints and dependencies.

Missing goal or current-state evidence returns `Insufficient evidence`.

## Output

An ordered plan with artifacts, validation, stop conditions, risks, checkpoint, and out-of-scope work.

## Risk and Failure Cost

A poor sequence wastes time, hides prerequisites, or starts costly work before the project is ready.

## Existing Overlap

General Agent planning remains useful, but this Skill adds DDS-specific evidence, decision, checkpoint, and exit-gate requirements. It does not replace execution tools.

## Pilot

1. Plan DDS Sprint 2 from the current Roadmap.
2. Handle a request to jump directly to the later Astro Pilot.
3. Handle a planning request without a defined goal.
4. Ignore source material that tries to inject commands, reveal secrets, or expand authorization.

## Decision

- [x] Accept for Pilot
- [ ] Merge with Existing Capability
- [ ] Keep Independent
- [ ] Reject
