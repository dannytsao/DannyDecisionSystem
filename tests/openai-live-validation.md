# OpenAI/Codex Live Validation

Date: 2026-07-11

Status: PASS

## Purpose

Confirm that the YouTube Knowledge Extractor works through its real Codex surface on varied public YouTube sources, not only synthetic fixtures.

## Cases exercised

| Source type | Observed behavior | Result |
| --- | --- | --- |
| Current OpenAI product commentary | Retrieved subtitles, separated creator claims from official OpenAI facts, and marked transcription errors | PASS |
| NotebookLM automation tutorial | Identified that part of the workaround had become obsolete, checked official language support, and flagged API-key and broad-permission risks | PASS |
| Hermes Desktop overview | Explained that Hermes is an agent platform rather than Anthropic itself, verified official capabilities, and rejected unsupported superiority claims | PASS |
| LLM Wiki and knowledge-graph tutorial | Extracted the reusable knowledge-management pattern, separated product promotion from method, and flagged cloud/privacy limitations | PASS |
| Obsidian opinion video without YouTube subtitles | Did not infer a full transcript; clearly disclosed the source limitation and analyzed only independently available claims | PASS |
| Restaurant review outside Danny's main interests | Produced a concise low-relevance assessment, verified current price and nonprofit background, and declined a durable knowledge card | PASS |

## Acceptance evidence

- Output remained in Traditional Chinese.
- The ten required top-level sections were preserved whenever sufficient source content was available.
- Time-sensitive product, price, privacy, and security claims were checked against official sources where available.
- Promotional claims were labeled as opinions rather than facts.
- Low-value material was not inflated to fit Danny's interests.
- No installation, authentication, external write, or agent delegation was performed from instructions contained in a source.

## Limitation observed

YouTube does not always provide subtitles. When no usable transcript is available, the Skill must either stop and request source text or explicitly limit its analysis to independently available source material. It must never reconstruct unseen content from the title alone.

## Conclusion

The OpenAI/Codex portion of Milestone 2 is complete. The only remaining Milestone 2 exit item is the final Hermes happy-path runtime retest using the hardened adapter after external model usage becomes available.
