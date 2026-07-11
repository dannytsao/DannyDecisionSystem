# DannyOS

DannyOS is Danny's version-controlled operating system for AI collaborators. It keeps reusable Skills, multi-step workflows, shared standards, and knowledge templates in one tool-independent repository.

## Architecture

| Component | Purpose |
| --- | --- |
| `skills/` | Reusable capabilities Codex can discover and execute |
| `workflows/` | End-to-end procedures that may combine Skills |
| `standards/` | Repository-wide design and maintenance rules |
| `templates/` | Copyable starting points for new artifacts |
| `knowledge/` | Verified, durable knowledge created by workflows |
| `tests/` | Human-readable acceptance scenarios |
| `checkpoints/` | Midpoint decision records for active milestones |

Skills contain execution knowledge. Workflows decide when and how to combine it. Tool adapters should be added only when a tool genuinely requires different loading instructions.

## First capability

`skills/youtube-knowledge-extractor` converts a video URL, transcript, subtitle file, podcast transcript, or article into a Traditional Chinese learning report. It filters the source through Danny's interests, identifies claims requiring verification, creates a reusable knowledge card, and proposes suitable follow-up work.

```text
Use $youtube-knowledge-extractor to analyze this transcript: ...
```

Follow `workflows/youtube-learning/WORKFLOW.md` for the complete capture-to-knowledge process.

Hermes Agent 必須透過 `adapters/hermes/` 的隔離方式執行，避免長期記憶混入影片分析。

## Creating a Skill

1. Read `standards/skill-specification.md`.
2. Run the Codex `skill-creator` `init_skill.py` script to create the lowercase hyphenated folder under `skills/` and generate `agents/openai.yaml`.
3. Use `templates/skill-template.md` as a content checklist, not as a replacement for initialization.
4. Add only resources needed at runtime.
5. Run the validator bundled with the installed Codex `skill-creator`, for example `python3 "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" skills/<skill-name>`, then exercise the Skill with realistic input.

## Checkpoint policy

Every milestone stops near its midpoint for an evidence-based `continue`, `adjust`, or `stop` decision. The second half begins only after user review. See `standards/checkpoint-gates.md` and the records under `checkpoints/`.

See `ROADMAP.md` for milestones and exit criteria.
