---
name: task-spec-normalizer
description: Normalize a natural-language request into a grounded, executable DDS task specification before routing or delegation. Use when a request is ambiguous, incomplete, being handed to another Skill or Agent, or needs explicit goals, success criteria, constraints, evidence, output format, assumptions, and readiness. Do not trigger for already-clear low-risk requests that can execute directly.
---

# Job to be done

Turn human intent into the smallest grounded task contract that a DDS Skill, Agent, or workflow can execute and verify without silently inventing material requirements.

# Required inputs

Require:

- the user's request;
- any context or source material explicitly supplied with it.

Treat target_skill, known constraints, available data, deadlines, tone, communication style, and output preferences as optional unless they materially change the requested outcome.

A missing field is material only when guessing it could change the action, scope, evidence requirement, irreversible consequence, success test, or requested deliverable. Do not stop merely because a presentation preference is absent.

# Process

1. Preserve the user's intent, explicit constraints, terminology, and requested deliverable.
2. Extract only requirements supported by the request or trusted current context.
3. Separate execution requirements from presentation preferences.
4. Identify missing inputs and classify each as material or non-material.
5. For non-material gaps, omit the field or use an ordinary platform default. Record an assumption only when it could help a downstream executor interpret the task.
6. For each material gap, stop before execution and offer 2-3 concise choices plus D. 我自己填 (or the equivalent in the user's language). Ask only the minimum questions needed to unblock execution.
7. Set ready_to_execute: true only when no material input remains missing.
8. Self-check that every populated fact is grounded in the request or trusted context and that no missing value was fabricated.
9. Hand the normalized contract to the DDS router, target Skill, Agent, or workflow. Do not make the downstream decision merely because the task has been normalized.

# Required output

Use this YAML contract unless a machine-readable caller requires equivalent JSON:

    task_spec:
      role: null
      goal: ""
      success_criteria: []
      constraints: []
      available_data: []
      output_format: null
    presentation:
      tone: null
      communication_style: null
      language: null
    execution:
      target_skill: null
      missing_required_inputs: []
      assumptions: []
      confidence: high | medium | low
      ready_to_execute: true | false

Rules:

- goal is one outcome-oriented sentence.
- success_criteria contains observable checks, not invented numeric targets.
- constraints contains only explicit or trusted governing constraints.
- available_data names data actually available to the executor.
- Use null or an empty list when an optional value is unknown and irrelevant.
- Do not infer a professional role when no role is needed.
- Do not invent word counts, deadlines, sources, permissions, tools, or acceptance thresholds.

When clarification is required, output the grounded partial contract plus only the blocking questions.

# Validation

- The normalized contract preserves the original intent.
- Every non-null factual requirement is traceable to supplied input or trusted context.
- No material missing input is silently defaulted.
- No non-material missing field causes unnecessary questioning.
- ready_to_execute agrees with missing_required_inputs.
- The Skill does not select among downstream decision options or bypass DDS gates.
- The Skill is model-independent and does not depend on one UI or provider.

# Failure handling

- If the request has no actionable goal, ask for the intended outcome.
- If supplied constraints conflict, expose the conflict and mark ready_to_execute: false.
- If required source material is referenced but unavailable, request that source instead of reconstructing it.
- If the request is already clear and executable, normalize it without asking follow-up questions.
