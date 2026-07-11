# DannyOS Skill Specification

DannyOS Skills follow the current Codex progressive-disclosure model.

## Structure

```text
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/        # optional
```

Use `scripts/` only for deterministic repeated operations and `assets/` only for output assets. Do not add per-Skill README, changelog, installation, checklist, or test documents. Keep essential execution rules in `SKILL.md`, runtime detail in `references/`, and project history or tests at the repository root.

Initialize every new Skill with the current Codex `skill-creator` `init_skill.py` script. Use the DannyOS template to shape the generated instructions, never to bypass initialization.

## `SKILL.md`

The YAML frontmatter contains exactly `name` and `description`. Use lowercase letters, digits, and hyphens for a name below 64 characters. Put the complete trigger contract in `description`, because it is always loaded. Write a concise imperative body below 500 lines. Link every optional reference directly from `SKILL.md` and avoid duplication.

## `agents/openai.yaml`

Generate UI metadata with `skill-creator`. Include `display_name`, a 25 to 64 character `short_description`, and a one-sentence `default_prompt` that explicitly mentions `$skill-name`.

## Definition of done

- `quick_validate.py <skill-directory>` exits successfully.
- The Skill succeeds on a representative happy path.
- It handles one missing or invalid input without fabrication.
- Its output satisfies its required format and validation rules.
