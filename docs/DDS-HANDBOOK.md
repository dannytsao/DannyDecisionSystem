# DDS Handbook

DDS 是 **Danny Decision System**，也是本 Repository 的主專案。它不是另一套 Agent。

DDS 接收原 DannyOS 建立的 Skill、Workflow、測試與標準，並將它們導向同一個目的：根據證據、風險和 Danny 的條件，建立可重複使用的決策能力。

```text
DDS
├── Decision governance
├── Skills、Workflows、Knowledge、Adapters
└── Inherited DannyOS assets and history
```

## 五個原則

1. **Simple**：五分鐘看不懂，就重新寫。
2. **Reusable**：只保存能改善未來工作的能力。
3. **Explainable**：重要結論必須說明證據與風險。
4. **Maintainable**：規則只有一個正式來源。
5. **Agent-neutral**：Codex、Hermes、Claude、OpenCode 或其他 Agent 都可替換。

## 決策流程

```text
任務
→ 證據
→ 限制
→ 風險
→ 決策
→ 備案
→ 結果校準
```

決策型 Skill 至少回答：

- 建議做什麼？
- 根據什麼？
- 最大風險是什麼？
- 哪個條件會改變結論？
- 如果失敗，備案是什麼？

證據不足時，輸出 `Conditional`、`Defer` 或 `Insufficient evidence`，不要用流暢文字掩蓋不確定性。

## 四種能力

| 類型 | 工作 | 例子 |
| --- | --- | --- |
| Decision Skill | 綜合證據並提出決策 | 天文攝影出勤、PR 合併判斷 |
| Supporting Skill | 提供證據或分析，不擁有最終決策 | 天氣分析、字幕擷取 |
| Shared Utility | 執行單純、共用的處理 | 格式化、單位轉換 |
| Independent Tool | 完成創作、轉換或外部操作 | 圖像生成、影片剪輯 |

分類方式見 `standards/skill-admission.md`。

## 證據只問四件事

1. 來源可靠嗎？
2. 資料仍然新嗎？
3. 與目前任務直接相關嗎？
4. 它會改變決策嗎？

即時觀測通常高於預報，實際測試通常高於推測。不同領域可以定義自己的優先順序，但必須說明原因。

若關鍵證據互相衝突：

- 顯示衝突。
- 降低信心度。
- 說明採用哪一項及原因。
- 說明另一項若為真，結論會如何改變。

## 信心度

預設使用五級：`Very High`、`High`、`Medium`、`Low`、`Very Low`。

百分比只能作輔助，不得使用 `100%`，也不能假裝精確到小數點。信心度表示證據支持結論的程度，不是成功保證。

重要決策至少輸出：

```text
Decision:
Confidence:
Main uncertainty:
What could change the decision:
```

## 人類批准

| 行為 | 預設權限 |
| --- | --- |
| 搜尋、讀取、分析 | 可直接執行 |
| 建立報告或草稿 | 可直接建立草稿 |
| 修改 Repo 內已授權範圍 | 依使用者任務執行並留下 Git 紀錄 |
| 寄送、發布、部署、合併、刪除、付費 | 必須取得明確批准 |

外部 App 只提供證據或執行已批准的工作，不擁有決策權。

## Agent 與 Adapter

核心 Skill 維持平台中立。只有實測證明某個 Agent 需要不同載入或隔離方式時，才建立薄 Adapter。

Adapter 可以處理：

- 載入正確文件。
- 轉換輸入格式。
- 隔離記憶與權限。

Adapter 不可以改寫核心決策規則。

## 記錄與校準

不要永久保存所有執行過程。

```text
短期 Trace → 到期清除
重要 Decision Summary → 保留最小摘要
重複且有用的 Lesson → 審查後升級成 Knowledge 或 Rule
```

只有以下情況值得長期保存：

- 同類偏差重複出現。
- 單次錯誤成本很高。
- 找到明確規則缺陷。
- 新證據推翻舊假設。
- Danny 指定具有長期價值。

原則：保存足以解釋的內容，留下足以學習的內容，其餘刪除。

## 變更規則

DDS 治理在 Pilot 期間保持穩定。只有下列原因可以修改核心原則：

- 現有規則互相矛盾或無法執行。
- 真實案例發現重要缺口。
- 出現安全或權限風險。
- 新 Agent 無法透過薄 Adapter 接入。

「更漂亮」、「更完整」或「以後可能用到」都不是新增規則的理由。

## 一句話文化

> Make good decisions. Keep it simple. Learn only what is worth keeping.
