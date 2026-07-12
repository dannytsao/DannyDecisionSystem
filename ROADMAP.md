# DDS Roadmap

本 Roadmap 以 **Danny Decision System (DDS)** 為唯一主線。原 DannyOS Milestone 只保留為歷史與遺留工作來源。

## Current status

| Workstream | Status |
| --- | --- |
| DannyOS Milestone 1：基礎與 YouTube Skill | Complete, inherited by DDS |
| DannyOS Milestone 2：跨 Agent 驗證 | Complete, archived |
| DDS Sprint 0：治理與專案轉換 | Complete |
| DDS Sprint 1：遺留工作收尾 | Complete |
| DDS Sprint 2：首批能力 Pilot | Complete |
| DDS Sprint 3：Midpoint Checkpoint | Complete; decision: continue |
| DDS Sprint 4：Remaining core capabilities | Next; not started |

## Sprint 0：DDS Governance and Transition

Status: Complete

- 確立 DDS 為主專案，DannyOS 為歷史階段。
- 建立精簡 DDS Handbook。
- 建立 Skill Admission Gate 與 Proposal Template。
- 接收 DannyOS 的 Skills、Workflows、Standards、Tests 與 Adapter。
- 保存 Astro Photography Decision Skill Pilot 提案。

## Sprint 1：Close inherited DannyOS work

Status: Complete

1. 使用最終安全版 Hermes Adapter 重跑 approved Happy Path fixture。
2. 確認直接輸出非空白、格式完整、工具呼叫為零且沒有舊記憶污染。
3. 通過後更新測試、Checkpoint 與 Changelog。
4. 將原 DannyOS Milestone 2 標記為完成並封存。

Exit gate：跨 Agent 參考 Skill 有 Codex 與 Hermes 的完整、可稽核通過證據。

完成證據：Hermes 最終 session `20260712_163710_2832ac` 直接回傳完整繁體中文格式，工具呼叫數為 0，且沒有舊記憶污染。

## Sprint 2：First DDS capability pilots

Status: Complete

候選能力：

- Documentation Maintenance
- Project Planning

先經 Skill Admission 判斷它們是 Decision Skill、Supporting Skill 或 Workflow，再決定是否建立。

每項 Pilot 必須有清楚的工作目標、三個代表案例、至少一個失敗案例，且不複製既有規則。

完成成果：

- `documentation-maintenance` Decision Skill Pilot
- `project-planning` Decision Skill Pilot
- 兩者皆通過官方結構驗證、三個案例及獨立 Agent 前向測試

## Sprint 3：DDS Midpoint Checkpoint

Status: Complete

完成兩個 Pilot 後停止，檢查是否解決重複問題、維持簡單、能跨 Agent 使用，以及 DDS Handbook 是否已有足夠規則。

Danny 決定 `continue`、`adjust` 或 `stop`。

Decision: `continue`。完整紀錄見 `checkpoints/sprint-3-checkpoint.md`。

## Sprint 4：Remaining core capabilities

Status: Not started

只有 Sprint 3 決定繼續才進行：

- GitHub Review and Task Coordination
- AI Development Assistance

## Sprint 5：Astro Photography Decision Pilot

依 `docs/ASTRO-PHOTOGRAPHY-SKILL-PROPOSAL.md` 建立 Pilot。

- 查證舊 Custom GPT 的氣象與器材門檻。
- 測試白牆、雲海及星空案例。
- 分開處理觀測、預報、器材與安全證據。
- 單次失敗不自動建立新 Rule。

## Sprint 6：Second specialist pilot and checkpoint

從 IT／SysOps、Power Query、Business／Investment Risk 或 Image Analysis 選一項。完成後檢查 DDS 決策模型能否跨領域使用。

## Sprint 7：Integrations and automation

只有人工 Workflow 通過實際案例後，才考慮 Obsidian、GitHub、Google Drive、Cloudflare、LINE、Knowledge Graph 或 AstroAssistant App。

先自動化一個非正式環境 Workflow，通過權限、隱私、失敗復原與節省時間檢查後才擴充。

詳細執行表見 `docs/DDS-SPRINT-PLAN.md`。
