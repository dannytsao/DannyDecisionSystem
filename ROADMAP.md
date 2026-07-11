# DannyOS Roadmap

## Milestone 1: Foundation

Status: Complete (2026-07-11)

Deliverables:

- Repository architecture and governing standards
- Current Codex Skill specification and reusable template
- Production-ready YouTube Knowledge Extractor
- YouTube Learning workflow and knowledge-card template
- Validation and realistic acceptance scenarios

Exit criteria:

- The Skill passes the Codex structural validator.
- A transcript produces the required Traditional Chinese report without invented claims.
- Missing source content produces a clear request for transcript or accessible content.
- The repository is understandable from `README.md` without oral explanation.

## Milestone 2: Cross-agent validation

- Exercise the reference Skill in at least two supported AI environments.
- Document only real adapter differences.
- Establish a small regression corpus from approved source material.

Midpoint checkpoint: stop after the first external AI environment has executed both the happy path and missing-source path. Review output differences, privacy constraints, and whether a tool-specific adapter is genuinely needed before testing the second environment.

## Milestone 3: Core development Skills

- Documentation maintenance
- Project planning
- GitHub review and task coordination
- AI development assistance

Midpoint checkpoint: stop after two candidate Skills have been exercised. Confirm they solve recurring work, remain distinct, and follow the reference Skill structure before building the remaining Skills.

## Milestone 4: Specialist capabilities

- Astrophotography and weather analysis
- IT, SysOps, logistics, and Power Query
- Image creation and critique
- Business, investment, and scam-risk analysis

Midpoint checkpoint: stop after the first two domain Skills pass realistic tasks. Confirm domain boundaries, evidence requirements, and maintenance cost before expanding the catalog.

## Milestone 5: Integrations and automation

- Knowledge-base destinations
- GitHub, Cloudflare, local, and LINE integrations where useful

Midpoint checkpoint: stop after one manual workflow is automated in a non-production environment. Review authorization, privacy, failure recovery, and measurable time saved before adding another integration.

Automation begins only after the corresponding manual workflow passes its acceptance scenarios.

All checkpoints follow `standards/checkpoint-gates.md`.
