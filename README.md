# Danny Decision System (DDS)

DDS 是 Danny 的版本控制決策系統。它保存可重複使用的決策能力，讓 Codex、Hermes、Claude、OpenCode 或未來其他 Agent 使用同一套證據、風險與決策規則。

> Make good decisions. Keep it simple. Learn only what is worth keeping.

## 專案關係

這個 Repository 最初名為 **DannyOS**，先完成了 Skill、Workflow、測試和跨 Agent 基礎建設。專案方向後來收斂為 **Danny Decision System (DDS)**。

現在的主從關係是：

```text
DDS（主專案）
├── 接收 DannyOS 已完成的基礎資產
├── 保存已完成的 DannyOS／Hermes 歷史證據
└── 以決策能力為核心繼續發展
```

DannyOS 只保留為歷史階段名稱，不是 DDS 的上層系統，也不再擁有獨立 Roadmap。完整整理見 `docs/DANNYOS-TO-DDS-TRANSITION.md`。

## DDS 做什麼

```text
任務
→ 證據
→ 限制
→ 風險
→ 決策
→ 備案
→ 結果校準
```

DDS 不以累積 Prompt、答案或工具數量為目標。新能力必須先通過 `standards/skill-admission.md`。

## Repository 結構

| Component | Purpose |
| --- | --- |
| `docs/` | DDS 架構、遷移與 Sprint 計畫 |
| `skills/` | 可重複使用的 Decision 或 Supporting Skills |
| `workflows/` | 組合 Skills 的完整工作流程 |
| `standards/` | Skill、Checkpoint、Git 與命名規範 |
| `templates/` | Skill 提案與知識卡模板 |
| `knowledge/` | 經查證、值得長期保存的知識 |
| `adapters/` | 實測證明必要的 Agent 接合與隔離方式 |
| `tests/` | Acceptance、回歸與跨 Agent 證據 |
| `checkpoints/` | 歷史與現行的里程碑決策紀錄 |

## 已接收的 DannyOS 資產

- Production-ready YouTube Knowledge Extractor
- YouTube Learning Workflow
- Skill Specification 與 Templates
- Knowledge Card 格式
- Checkpoint Gate
- Codex 真實影片測試
- Hermes 隔離 Adapter 與跨 Agent 測試證據

第一個 Skill 位於 `skills/youtube-knowledge-extractor/`。它已成為 DDS 的參考實作，不需要為改名而重寫。

## 目前狀態

- DDS Sprint 0：治理與轉換，完成。
- DDS Sprint 1：DannyOS 遺留工作收尾，完成。
- DDS Sprint 2：Documentation Maintenance 與 Project Planning Pilots，完成。
- DDS Sprint 3：Midpoint Checkpoint，完成；Danny 決定 `continue`。
- DDS Sprint 4：Remaining core capabilities，下一步但尚未開始。
- Astro Photography：已保存為後續 Decision Skill Pilot 提案，尚未開始實作。

執行順序以 `ROADMAP.md` 和 `docs/DDS-SPRINT-PLAN.md` 為準。

目前的 DDS Skills：

- `skills/youtube-knowledge-extractor/`
- `skills/documentation-maintenance/`
- `skills/project-planning/`

## 建立新 Skill

1. 填寫 `templates/skill-proposal.md`。
2. 通過 `standards/skill-admission.md`。
3. 閱讀 `standards/skill-specification.md`。
4. 使用 Codex `skill-creator` 的 `init_skill.py` 初始化。
5. 以 `templates/skill-template.md` 檢查內容。
6. 通過結構驗證、Happy Path 與 Failure Path。

## Checkpoint

每個 Sprint 在指定位置停止，讓 Danny 選擇 `continue`、`adjust` 或 `stop`。規則見 `standards/checkpoint-gates.md`。
