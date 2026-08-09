# Astro Advisory Verification Reconciliation — 2026-08-08

## Decision

**Do not approve the post-Sprint-5 Astro Advisory extension as behaviorally complete.** Keep it `Pilot-ready; verification gate blocked`. Sprint 6 remains `Not started`.

This checkpoint reconciles the 2026-08-08 five-lane independent review with the current local checkout. It supersedes the ambiguous phrase “awaiting final review” for status reporting; the gate has now been reviewed and rejected, with explicit follow-up work remaining.

## Frozen current identity

- Repository `HEAD`: `4964786d086752adeec55fc96a77a111897af766`
- Advisory Skill SHA-256: `4d8cf8f7e2c9e0eabb79ef8b423e5f14f76cc9508558da8f142a760b8f547cd5`
- Evidence Policy SHA-256: `3c2f8ac6b061c2c7fe4fb30c427663a4eed5d9d26d37eeb4839f4427defec210`
- Advisory test contract SHA-256: `cc02337e70aa3a13301176ad4295b7dd8475b42ecc51478aed71cfb4cc9cafeb`
- Structural checks at this checkpoint: `quick_validate.py` PASS, `tests/validate-regression.sh` PASS, `git diff --check` PASS.

## Authoritative QA surface

The single authoritative end-to-end replay surface for the next gate is:

```text
codex-cli 0.143.0
model: gpt-5.4
flags: --ignore-user-config --ephemeral --json --sandbox read-only
activation: explicit wrapper reads the current Advisory Skill and its current references before the user prompt
evidence: complete JSONL action trace, session id, current source hashes, and final answer
```

The native top-level image-generation probe proved that image generation can work on the parent Codex surface, but it is **capability-only evidence**. It does not prove the isolated advisory runtime's action ordering and is not an end-to-end Case 04 PASS.

## Gate reconciliation

| Gate | Current result | Evidence interpretation |
|---|---|---|
| F1 implementation / durable delivery | PASS, local/source only | Package and docs exist; validators are not behavioral QA. |
| F2 Skill quality / authority / evidence policy | FAIL | Image error/empty-result fallback, dynamic receipt drift, and prose-mirroring test weaknesses remain. |
| F3 six fresh scenarios | FAIL | Cases 01, 02, 03, 05, 06 and hostile listing have useful current traces; Case 04 lacks valid end-to-end image result or truthful fallback on the authoritative surface. |
| F4 scope / status / completion claim | FAIL | Status is now accurately blocked, but current-hash reconciliation and behavioral scope fidelity are not closed. |
| Security / privacy | FAIL | Hostile listing action boundary passes on available evidence; fresh exact-pin non-persistence proof and current-hash image truthfulness are missing. |

## Stale evidence policy

Artifacts recording Advisory Skill hash `ff2129…` or test hash `c4fe86…` predate the latest fallback edits and are retained only as historical/reconciliation inputs. They must not be cited as proof for the frozen current Skill hash above. The current-hash Case 04 v3 artifact is a FAIL and also records that the target Skill was not successfully loaded; it cannot close the gate.

## Required next checkpoint

1. Provide one authoritative isolated runtime that actually exposes the native image-generation action, or explicitly implement a harness-level unavailable-capability result that is recorded in the raw action trace.
2. Rerun Case 04 on the frozen current hash; require one successful image result after all prose and no post-image action, or an explicit truthful unavailable fallback with no image-claiming wording.
3. Run a fresh exact-pin scenario proving session-only use, masked/absent durable artifact output, and no cross-session/shared persistence.
4. Reconcile or mark all earlier hash/model/surface artifacts as stale in one index; do not delete them.
5. Rerun the five-lane independent review against only the frozen current hashes and the new evidence.

Only after those steps pass may the status move from `verification gate blocked` to `behaviorally approved`; only a later owner checkpoint may select and start Sprint 6.
