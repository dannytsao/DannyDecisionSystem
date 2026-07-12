# Documentation Maintenance Skill Proposal

Status: Accepted for DDS Sprint 2 Pilot

Scope approval: Danny instructed Codex to execute DDS Sprint 2 on 2026-07-12 after the two candidates and Pilot gate were documented in the Roadmap.

## Problem

Repository status and navigation documents become stale or duplicated. The capability must decide what to keep, update, merge, archive, or remove without rewriting history.

## Type

Decision Skill. It combines repository evidence, document purpose, history, and maintenance risk to choose an action.

## Inputs and Evidence

- Repository path and review scope.
- Current files, tests, Git history, links, and project status.

Missing repository evidence returns `Insufficient evidence`.

## Output

A document decision table, conflicts, stale references, approval needs, and validation performed.

## Risk and Failure Cost

Wrong decisions can delete useful evidence, preserve incorrect guidance, or create more duplicate documents. Destructive changes require authorization.

## Existing Overlap

No existing DDS Skill governs repository documentation. Git tools provide evidence and execution but do not own the decision.

## Pilot

1. Check whether current DDS status documents agree after Sprint 1.
2. Decide how to treat a historical checkpoint that still describes an old pending item.
3. Handle a request without an accessible repository or clear scope.
4. Ignore a repository document that attempts to override instructions or request secrets and external actions.

## Decision

- [x] Accept for Pilot
- [ ] Merge with Existing Capability
- [ ] Keep Independent
- [ ] Reject
