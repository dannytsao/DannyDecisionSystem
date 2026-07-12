# Milestone Checkpoint Gates

Every DDS Sprint with a declared midpoint must stop before the remaining work begins. The checkpoint is a decision gate, not a status update. Historical DannyOS milestone records remain valid evidence.

## Required checkpoint record

For DDS, create `checkpoints/sprint-<number>-checkpoint.md`. Historical DannyOS records may keep `checkpoints/milestone-<number>-midpoint.md`.

The record contains:

1. Original milestone outcome and exit criteria.
2. Work completed, with links to actual artifacts.
3. Validation evidence gathered so far.
4. Work still remaining.
5. New risks, contradictions, or scope changes.
6. Recommendation: `continue`, `adjust`, or `stop`.
7. User decision and any approved correction.

Do not begin the next Sprint until the user reviews this record and explicitly chooses a direction.

## Pass conditions

A checkpoint may recommend `continue` only when:

- Completed artifacts support the original goal rather than merely increasing file count.
- At least one representative behavior has been exercised through its real surface.
- Current validation has no unresolved blocking issue.
- Remaining work still fits the milestone scope and is likely to satisfy its exit criteria.
- Assumptions that materially affect direction are visible to the user.

Recommend `adjust` when the goal remains valid but evidence supports changing scope, sequence, or design. Recommend `stop` when the milestone no longer solves the intended problem or cannot meet its exit criteria safely.

## Final gate

At milestone completion, compare the final artifacts with both the original exit criteria and the approved midpoint decision. Record deviations before marking the milestone complete.
