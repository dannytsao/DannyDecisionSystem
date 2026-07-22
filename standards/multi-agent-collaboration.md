# Multi-Agent Collaboration Standard

Purpose: allow Codex, Claude Code, Kimi, Hermes and other agents to contribute without overwriting one another or changing DDS direction independently.

## Five rules

1. **One task, one owner.** Every active task has one named Agent or human owner.
2. **One task, one branch.** Use `agent/<agent>-<task>`; never develop directly on `main`.
3. **Claim the scope before editing.** State the goal, files or directories, and expected output in the PR or task record.
4. **No overlapping edits.** A second Agent reviews or waits when another active branch owns the same files or decision scope.
5. **Merge only through review.** The owner builds; another Agent or Danny reviews; Danny decides architecture, priority and acceptance when material judgment is required.

## Required workflow

```text
Task selected
-> scope claimed
-> branch created from current main
-> focused change
-> validation
-> draft PR
-> independent review
-> Danny: continue / adjust / stop when checkpoint applies
-> merge
```

## Branch naming

```text
agent/codex-<task>
agent/claude-<task>
agent/kimi-<task>
agent/hermes-<task>
agent/human-<task>
```

Existing branches may keep their current names. New work follows this rule.

## Scope claim

Every PR must state:

- owner;
- objective;
- files or directories owned by this change;
- files intentionally not changed;
- validation performed;
- decisions required from Danny.

A scope claim is not permanent ownership. It lasts only until the PR is merged, closed or explicitly released.

## Conflict rules

- Do not ask two Agents to implement the same solution in the same files.
- Parallel work is allowed only when file and decision boundaries are clear.
- Architecture and governance changes must be isolated from feature implementation unless inseparable.
- An Agent must rebase or update from `main` before final review when `main` changed materially.
- Never resolve a semantic conflict by choosing whichever text merges cleanly.

## Roles

- **Danny — Product Owner:** vision, priority, material decisions and acceptance.
- **Builder Agent:** implements the claimed scope and records validation.
- **Reviewer Agent:** reviews evidence, risks, regressions and architecture fit; does not silently rewrite the Builder's branch.
- **DDS Repository:** source of truth for accepted decisions, standards and implementation.

Agents are roles, not permanent identities. Codex, Claude Code or Kimi may be Builder on one task and Reviewer on another.

## Stop conditions

Stop and ask for a decision when:

- the requested change contradicts an accepted DDS decision;
- two active tasks claim overlapping scope;
- the change expands beyond the stated task;
- evidence is insufficient for an irreversible choice;
- merging would start a later Sprint or bypass a checkpoint.

Keep coordination simple. Do not create extra councils, logs or approval layers unless repeated failures prove they are necessary.
