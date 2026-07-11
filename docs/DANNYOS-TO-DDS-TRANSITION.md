# DannyOS to DDS Transition

## 決定

本 Repository 的主專案是 **Danny Decision System (DDS)**。

DannyOS 是早期名稱與基礎建設階段。它已完成的成果由 DDS 接收，尚未完成的工作由 DDS 收尾；不再維護 DannyOS 的獨立方向。

## 接收內容

| DannyOS 資產 | DDS 處理方式 |
| --- | --- |
| YouTube Knowledge Extractor | 保留，作為第一個參考 Skill |
| YouTube Learning Workflow | 保留 |
| Skill、Git、Naming、Checkpoint Standards | 改以 DDS 名義維護 |
| Knowledge Card 與 Templates | 保留 |
| Codex 測試與 Regression Corpus | 保留 |
| Hermes Adapter | 保留，完成最後安全重測後封存評估階段 |
| 歷史 Checkpoints 與 Tests | 原文保留，避免改寫歷史 |
| 原 Milestone 3–5 | 由 DDS Sprint Roadmap 取代 |

## 名稱規則

- 新文件、Skill 與 Roadmap 使用 `DDS`。
- 歷史紀錄可以保留 `DannyOS`，但必須能看出它是早期階段。
- Hermes profile `dannyos-clean` 暫時保留，因為它是已測試的技術識別字，不代表專案主體。
- 本機資料夾目前仍叫 `DannyOS`，避免在未完成測試前破壞路徑；資料夾名稱不決定專案身份。

## 遺留工作

DannyOS 只剩一項未完成工作：Hermes 最終安全版 Happy Path 重測。

完成後封存原 Milestone 2，不再新增 DannyOS Milestone。

## 不做的事

- 不建立兩份 Roadmap。
- 不把 DDS 寫成 DannyOS 的下層功能。
- 不重寫已通過的 YouTube Skill，只為了改名稱。
- 不修改歷史證據來假裝專案一開始就是 DDS。
- 不在遷移期間提前建立 Astro 或其他新 Skill。
