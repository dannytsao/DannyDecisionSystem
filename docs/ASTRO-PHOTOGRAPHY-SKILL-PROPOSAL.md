# Astro Photography Decision Skill Proposal

Status: Completed in DDS Sprint 5

Scope approval: Danny instructed Codex to start Sprint 5 on 2026-07-12.

## Problem

根據台灣即時天氣、預報、天文條件、地形、器材和使用者限制，判斷一次風景或天文攝影行程是否值得出發，並避免高成本的白牆、海霧、強風或錯誤目標。

## Type

Decision Skill。

它需要整合多項證據、風險與個人條件，最後輸出 Go、Conditional Go、No-Go 或 Defer。

## Mission Types

- 銀河、星空與深空目標
- 日出、日落與火燒雲
- 雲海、霧景與大景
- 月景、行星與縮時
- 海岸倒影
- 無人機拍攝

不同 Mission 使用不同證據與規則，不能共用一套萬用分數。

## Required Inputs

- 拍攝目標
- 地點
- 日期與時間

視 Mission 加入：

- 現場觀測、衛星雲圖或雷達
- 溫度、露點、濕度、風向風速、雲量與能見度
- 月相、月出月落、曙暮光及目標位置
- 海岸 Mission 的潮汐
- 器材、交通、可接受風險與最晚撤退時間

缺少會改變結論的資料時，輸出 Conditional、Defer 或 Insufficient evidence。

## Decision Flow

```text
確認拍攝目標
→ 取得最新證據
→ 套用地點與器材限制
→ 找出最大失敗風險
→ Go / Conditional Go / No-Go / Defer
→ Plan B 與撤退條件
→ 有可靠事後證據時進行校準
```

## Candidate Rules from the Old GPT

以下舊規則已在 Pilot 中完成來源查證；未獲支持的固定門檻已拒絕或降級為待校準假設：

| Candidate | 原始想法 | Pilot 要確認的事 |
| --- | --- | --- |
| 現況優先 | 現場觀測與即時衛星高於數值預報 | 不同 Mission 是否都適用，以及如何處理時間或位置差異 |
| 預報衰減 | T+24、T+48、T+72 設置信心上限 | 上限是否有歷史準確率支持 |
| 白牆風險 | 溫露差小、低風速及低能見度提高風險 | 地形、季節與站點高度如何校準 |
| 雲海條件 | 低地高濕、高地較乾及迎風可能形成層次 | 測站高度差與地形是否足以代表現場 |
| 鏡面條件 | 風速過高時倒影品質下降 | 不同水域與陣風門檻 |
| 月光影響 | 月照較高時調整深空目標或濾鏡 | 目標種類、窄頻與廣角需求差異 |
| 高空風 | 噴流較強時降低長焦或行星拍攝品質 | Seeing、地面風與器材震動必須分開 |

不得把未校準的數值描述為科學定律或成功保證。

查證結果與正式來源已整理於 `skills/plan-astro-photo-session/references/EVIDENCE.md`。舊規則中的固定預報信心百分比、5 km 白牆、50% 月照濾鏡及 30 m/s 噴流震動門檻不納入正式規則。

## Equipment Context

已知候選器材：

- Seestar S50、S30 Pro、DWARF3
- Nikon D7200、Tokina 11–20mm、Sigma 18–35mm
- DJI Mini 3 Pro、Mavic 2、Avata 2

器材規格、抗風能力與濾鏡建議必須依官方文件及實測校對，不直接沿用舊 Prompt 的數字。

## Required Output

```text
Decision:
Confidence:
Core reason:
Critical evidence:
Primary risk:
What could change the decision:
Equipment plan:
Plan B:
Safety or retreat condition:
Sources and freshness:
```

## Pilot Result

已測試下列三類主要案例，另加入資料不足、部分任務及惡意證據案例：

1. 預報良好，但即時衛星或現場觀測顯示滯留雲。
2. 雲海條件看似成立，但山頂可能落入雲層形成白牆。
3. 星空透明度可接受，但月光、風或器材限制使原目標不適合。

合成案例驗證行為，不證明預測準確率。若日後取得可靠事後證據，再比較預測與結果。實拍只是可能來源之一；單一案例不得建立新 Rule。

## Boundary

- Skill 負責決策，不負責建立天氣 API 或 App UI。
- Weather、satellite、tide 與 astronomy 擷取可成為 Supporting Skills 或工具。
- AstroAssistant App 是未來介面；是否建立應另行通過產品價值、安全與維護成本審查，不綁定實拍次數。
- 本 Pilot 不建立天氣 API、App UI 或自動化，也不提前開始 Sprint 6。
