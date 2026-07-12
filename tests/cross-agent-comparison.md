# Codex 與 Hermes 跨 Agent 比較

日期：2026-07-12

## 測試環境

| 環境 | Skill 載入方式 | 記憶隔離方式 |
| --- | --- | --- |
| Codex | 原生讀取 `SKILL.md` 與 reference | 本次 workspace 與明確提供的來源 |
| Hermes Agent | `adapters/hermes/run-youtube-extractor.sh` 組合完整 Skill、格式與來源 | 空白 `dannyos-clean` profile，加上 safe mode 與工具停用 |

## 共同測試

| 測試 | Codex | Hermes |
| --- | --- | --- |
| 宣傳型 AI agent 逐字稿 | PASS | PASS |
| 十個必要輸出區塊 | PASS | PASS |
| 繁體中文 | PASS | PASS |
| 移除宣傳與降低評分 | PASS | PASS |
| 標記未證實 benchmark | PASS | PASS |
| 三欄英文關鍵詞表格 | PASS | PASS |
| 知識卡前後判斷一致 | PASS | PASS |
| 空白來源停止分析 | PASS | PASS |
| 不從 metadata 猜測 | PASS | PASS |

可稽核證據：

- Codex 實際範例：`examples/promotional-agent-workflow.md`、`examples/missing-source.md`
- Hermes 去識別化輸出：`tests/expected/hermes-promotional-output.md`、`tests/expected/hermes-missing-source-output.md`
- 自動檢查：`tests/validate-regression.sh`
- 最終 Hermes session：`20260712_163710_2832ac`（直接輸出非空白、`tool_call_count: 0`、`output_tokens: 1605`）

## 真正需要的 adapter 差異

Codex 可以直接使用 repository Skill。Hermes 需要專用 adapter，原因不是分析能力不同，而是 Hermes 會自動加入自己的長期記憶、Skills 與 session 背景。

Hermes adapter 必須：

- 使用不含舊記憶的空白 profile；
- 傳入完整 Skill 與完整輸出格式；
- 關閉個人規則，只保留不能讀檔、執行命令或傳資料的 `clarify` 提問工具；
- 固定 Anthropic 供應商並核對測試資料的 SHA-256 數位指紋；
- 沒有直接答案時安全地判定失敗，不讀取其他 session。

## 未納入的環境

Claude Code CLI 尚未登入，隔離測試回報 API 使用量為 0，因此沒有實際模型結果，不列入 PASS，也不保留未驗證 adapter。

## 結論

YouTube Knowledge Extractor 已在 Codex 與隔離後的 Hermes Agent 中通過相同核心行為。Hermes 最終安全版本的 happy path 與 missing-source 均已通過，DannyOS Milestone 2 可正式封存。核心 Skill 維持共用；只有 Hermes 的載入與隔離方式需要 adapter。
