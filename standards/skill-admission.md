# Skill Admission

新增 Skill 前先回答四個問題：

1. 會重複使用，或做錯的成本很高嗎？
2. 是否已經有 Skill、Workflow 或 Utility 能處理？
3. 它是在做決策、提供證據，還是單純執行？
4. 能否用真實案例驗證？

## 分類

| 判斷 | 放置方式 |
| --- | --- |
| 綜合證據、限制與風險後做選擇 | Decision Skill，放在 `skills/` |
| 只提供證據、分析或擷取 | Supporting Skill，放在 `skills/` |
| 單純格式化、轉換或計算 | 優先放進現有 Skill 的 `scripts/` 或共用工具；不要急著建立 Skill |
| 創作、外部產品操作或一次性工作 | 保持獨立；需要時由 Workflow 呼叫 |

## Admission Gate

建立正式 Skill 前必須具備：

- 清楚的 Job to be done。
- 最少必要輸入與缺少輸入時的處理方式。
- 與現有能力沒有不必要重複。
- 一個 Happy Path 與一個 Failure Path。
- 使用者同意分類與 Pilot 範圍。

不因為「看起來很有用」就加入。先填 `templates/skill-proposal.md`，通過後再依 `standards/skill-specification.md` 建立。

## Pilot 與退場

- Pilot 使用三個有代表性的真實案例；高風險能力可增加案例。
- Pilot 通過後才標記為正式能力。
- 沒有重複價值、長期未使用或與其他 Skill 重疊時，應合併、停用或移除。
- Pilot 發現治理缺口時，先嘗試用現有規則解決；只有必要時才修改 DDS Handbook。
