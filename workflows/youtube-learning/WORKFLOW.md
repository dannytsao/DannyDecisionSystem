# YouTube Learning Workflow

## Outcome

Convert a video or transcript into a reviewed learning report and, only when warranted, a durable knowledge card.

## Flow

1. Capture the URL and obtain an accessible transcript or subtitles.
2. If source content is unavailable, stop and request it; do not summarize metadata.
3. Run `skills/youtube-knowledge-extractor/SKILL.md`.
4. Review claims under `【需要查證的說法】` against authoritative current sources when verification is in scope.
5. If recommended, check for personal, confidential, or copyright-sensitive material. Minimize or redact it and obtain explicit user authorization before permanently saving sensitive content.
6. Copy `templates/knowledge-card.md` and populate it from the source-grounded result.
7. Route the card by dominant subject under `knowledge/`.
8. Do not permanently save low-value material unless explicitly requested.

## Routing

| Subject | Destination |
| --- | --- |
| AI and agent development | `knowledge/ai-development/` |
| Astrophotography | `knowledge/astrophotography/` |
| IT, SysOps, logistics | `knowledge/it-operations/` |
| Image creation | `knowledge/image-creation/` |
| Business and investment | `knowledge/business/` |

## Exit criteria

- The report follows the Skill output format.
- Unsupported or time-sensitive claims are separated from verified facts.
- A saved card contains source metadata and verification status.
- Sensitive material is not persisted without redaction and explicit authorization.
- Low-value content does not enter the durable knowledge base by default.
