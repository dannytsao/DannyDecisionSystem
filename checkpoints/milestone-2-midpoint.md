# Milestone 2 Midpoint Checkpoint

Status: Adjustment implemented — final happy-path retest pending

Recommendation: `adjust`

## Original outcome

Validate the YouTube Knowledge Extractor in at least two AI environments, document only observed adapter differences, and establish a small approved regression corpus.

## Completed first half

The first external environment was Hermes Agent using an Anthropic model with tool access disabled.

### Happy path

Input: the synthetic promotional AI-agent transcript used by Milestone 1.

Observed passes:

- Returned all ten requested top-level sections in Traditional Chinese.
- Removed most promotional material and rated the source two stars.
- Preserved the three source-supported practices.
- Clearly marked the unsupported `ten times faster` claim as unverified.
- Included all four named Agent subsections.

Observed failures and differences:

- Hermes injected persistent PersonalKM memory even under `--safe-mode`.
- Several actions and knowledge links referenced PersonalKM, Resolver Layer, and existing Hermes Skills that were absent from the supplied transcript.
- This violates the Skill's source-grounding rule and creates an avoidable privacy and portability risk.
- The compact adapter prompt did not carry every detailed output constraint: the English-keyword table used two columns instead of three, and the final rating omitted the four explicit watch, save, card, and share decisions.
- The first one-shot invocation returned empty stdout within the orchestration window, although Hermes completed the response and stored it in its session database. Session export showed non-zero model usage and the full answer.

### Missing-source path

Observed result: PASS.

Hermes stopped before the ten-section report, stated that it could not access the video, refused to infer from URL or metadata, and requested transcript, subtitles, or pasted source text.

## Validation evidence

- Hermes session store recorded a completed happy-path response with non-zero input and output usage.
- Missing-source one-shot returned the expected refusal directly through stdout.
- Hermes recorded zero tool calls in the completed happy-path test.
- No repository files, personal source material, or secrets were included in the test payload; only Skill instructions and synthetic fixtures were sent.

## Remaining work at the checkpoint

1. Create the minimum Hermes adapter needed to load the full Skill contract and suppress unrelated persistent memory.
2. Rerun both Hermes paths and require exact output-format compliance plus source-only actions.
3. Test the corrected Skill in a second AI environment.
4. Establish the approved regression corpus from the passing outputs.

## Proposed adjustment

Do not proceed directly to the second environment. First create a small Hermes adapter that:

- loads the full `SKILL.md` and `OUTPUT_FORMAT.md` rather than a compressed prompt;
- explicitly disables or isolates persistent memory for evaluation runs;
- restricts Hermes to a harmless clarification tool and forbids external actions;
- records the response and usage reliably even when one-shot stdout is delayed.

After this adapter passes the same two fixtures, continue to the second environment. Do not change the generic Skill yet; the observed failures originate from Hermes context loading and the intentionally compressed test adapter, not from the core Skill contract.

## User decision

Decision: `adjust`.

使用者同意先建立 Hermes 隔離 adapter，要求後續盡量使用淺顯中文說明。完成 Hermes 重測後，再判斷是否進入第二個 AI 環境。

## Adjustment result

Status: Implemented; final happy-path runtime retest pending.

- `dannyos-clean` 空白 profile 已證實不含 PersonalKM 或 Resolver Layer 舊記憶。
- adapter 會載入完整 Skill 與輸出格式、關閉個人規則，並只保留 `clarify` 提問工具。
- missing-source path 已用最終安全版本通過。
- happy path 的行為版本已通過；加入最終安全收窄後的重跑因外部用量上限暫時未完成。
- 核心 Skill 新增知識卡前後一致性規則。
- one-shot stdout 空白時，adapter 會安全地判定失敗，不會誤拿其他 session 的答案。

Checkpoint decision 已執行完成，可以進入 Milestone 2 的第二個 AI 環境測試。

## Final outcome after checkpoint

Status: Pending one final happy-path runtime retest.

- Codex 已通過兩條路徑；Hermes 最終安全版本已通過 missing-source，happy path 等待外部用量恢復後重跑。
- 差異記錄於 `tests/cross-agent-comparison.md`。
- 合成 regression corpus 位於 `tests/fixtures/`，並已獲使用者同意用於 Anthropic 測試。
- Claude Code 因本機尚未登入、API 使用量為 0，未列入有效測試環境，也未保留未驗證 adapter。
