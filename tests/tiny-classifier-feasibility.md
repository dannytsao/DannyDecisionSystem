# Tiny Classifier DDS Feasibility Validation

Status: feasibility gate only; no model installation or training authorized.

## Objective

Determine whether any current DDS bounded decision gate has enough stable, checked labeled examples and expected execution volume to justify training/evaluating a local tiny text classifier such as the Ettin-17M recipe demonstrated by `MaximeRivest/tiny-classifiers`.

This validation is about readiness, not adoption. Tiny classifiers remain an external implementation candidate, not a DDS Skill or Runtime dependency.

## Current evidence source

Use the Jev validation historical dataset on PR #4 as the first available DDS labeled-decision sample. Keep PR #4 independent: do not modify its branch or reinterpret its benchmark labels as production truth.

Current checkpoint inspected: `tests/jev/historical.json` on `jev-value-validation`, 36 cases (H01-H36). Cases span multiple gates including completion, complexity, adoption, evidence, build, and governance, with English, Traditional Chinese, and mixed-language examples.

## Feasibility questions

Before installing a model or creating training infrastructure, answer for each candidate gate:

1. Is the label taxonomy stable and bounded?
2. Are labels checked strongly enough to serve as training/evaluation truth?
3. Are there enough examples per class to create disjoint train, validation, and held-out test sets without leakage?
4. Does the input distribution resemble the future production traffic for that gate?
5. Is expected message volume high enough that local inference could repay labeling, training, packaging, calibration, and maintenance cost?
6. Can deterministic hard rules remove cases that should never be delegated to a statistical classifier?
7. Is there a safe fallback when classifier confidence is low or the input is out of distribution?

## Phase 0 — Dataset readiness gate

Inventory the PR #4 dataset by gate, option/label, language, source type, and risk. Do not combine semantically different gates merely to inflate sample size.

A gate is **not training-ready** when any of these apply:

- its taxonomy or policy boundary is still changing;
- checked labels are too sparse to reserve a meaningful held-out test set;
- one or more classes have only a handful of examples;
- retrospective/synthetic labels dominate without enough observed cases;
- production volume is unknown or clearly too low to justify a trained model;
- hard-rule authority and statistical-classifier authority are not separated.

No universal minimum sample count is invented here. The Pilot must report the actual per-class counts and justify whether a statistically useful held-out evaluation is possible.

## Phase 1 — Only if Phase 0 passes

Create a frozen task-specific dataset for exactly one DDS gate. Split by provenance/time where possible to reduce leakage. Preserve a held-out human-checked test set that is never used by the teacher or trainer.

Compare at minimum:

- DDS deterministic policy where applicable;
- Jev or the current bounded semantic provider;
- Cheap LLM baseline;
- Tiny local classifier.

Measure accuracy, critical wrong routes, abstention/fallback rate, Traditional Chinese/mixed-language slices, latency, provider/training cost, inference cost, and maintenance burden.

## Phase 2 — Training experiment

Only after Phase 0/1 approval may the Pilot install training dependencies, obtain the selected encoder, generate/curate labels, or fine-tune a model. Teacher-generated labels must be permitted by the provider/model terms and must never contaminate the held-out human-checked test set.

## Current preliminary finding

The inspected PR #4 historical dataset has 36 total cases spread across multiple semantically distinct gates. That total must not be treated as 36 training examples for one classifier. On current evidence, no DDS gate has yet demonstrated enough checked, task-specific examples for a credible train/validation/held-out-test experiment.

Therefore the current status is **HOLD TRAINING** pending a per-gate inventory and additional real labeled decisions. This is a data-readiness conclusion, not evidence that tiny classifiers are unsuitable for DDS long term.

## Graduation trigger

Revisit a tiny-classifier experiment when one bounded gate has:

- a stable option taxonomy and policy boundary;
- a growing body of checked real decisions across its important classes and languages;
- enough examples to reserve an untouched test set while still training meaningfully;
- repeated execution volume that makes API/LLM cost or latency material;
- a defined low-confidence/OOD fallback.

## Result record

When revisited, record dataset commit, per-gate/per-class counts, provenance, language slices, split method, classifier/model version, training environment, benchmark results, cost assumptions, fallback behavior, and an evidence-based continue/hold/stop decision.
