# Astro Advisory Extension Pilot-ready Checkpoint

## 定位與目前狀態

這是 **post-Sprint-5 Astro Advisory extension** 的 durable checkpoint，不是 Sprint 6。Implementation 工作已完成並達到 **Pilot-ready**；2026-08-08 reconciliation review 已完成但 gate **blocked**，尚未核准 extension final complete。細節與 frozen hashes 見 [verification reconciliation checkpoint](astro-advisory-verification-reconciliation-2026-08-08.md)。

[Sprint 6](../ROADMAP.md#sprint-6second-specialist-pilot-and-checkpoint) 尚未開始，仍是下一個跨領域 specialist Pilot；本 extension 不完成、不取代，也不提前開始 Sprint 6。

原始目標是建立 Supporting/Advisory Skill：在不複製或覆蓋既有 dated Go/No-Go Decision Skill 權責的前提下，支援台灣星空旅拍地點比較、月份／日期評估整合、合法旅宿與公開房況查詢，以及只在使用者明確要求時提供構圖、參數或完整旅程規劃。

## Implementation 交付

1. Todo 1：[Skill Proposal](../docs/TAIWAN-ASTRO-TRIP-ADVISOR-SKILL-PROPOSAL.md) 記錄 Supporting/Advisory 分類、範圍、動態資料政策與六個 Pilot cases。
2. Todo 2：[Skill scaffold](../skills/advise-taiwan-astro-trip/) 由官方 initializer 建立，包括 SKILL.md、agents/openai.yaml 與 references/。
3. Todo 3：[Advisory workflow](../skills/advise-taiwan-astro-trip/SKILL.md) 與 [Evidence Policy](../skills/advise-taiwan-astro-trip/references/EVIDENCE_POLICY.md) 已實作；官方 Skill validator 通過。
4. Todo 4：[Pilot Cases 1–2](../tests/advise-taiwan-astro-trip.md) 已寫入 repo-backed case 文件，涵蓋歧義地名比較與不假裝知道房況的合法旅宿短名單。
5. Todo 5：[LOCATION_PROFILES.md](../skills/advise-taiwan-astro-trip/references/LOCATION_PROFILES.md)、分層回答與統一光害方法已依 midpoint `adjust` 完成。
6. Todo 6：[六個 Pilot cases](../tests/advise-taiwan-astro-trip.md) 與歷史 transcript artifacts 已完成；舊 exact-string transcript checker 已退休，其結果只保留為歷史 receipt，**不是 behavioral approval**。
7. Todo 7：[Supporting Skill](../skills/advise-taiwan-astro-trip/SKILL.md) 的 forward-run artifact 已保留；舊 generic contract checker 已退休，其 PASS 與當時針對 checker／artifact 的 review 只屬歷史 receipt，**不獨立確認 Skill 行為**。
8. Todo 8：README、ROADMAP、Sprint plan、CHANGELOG 與本 checkpoint 已記錄 Pilot-ready／verification-gate-blocked 狀態，沒有改變 Sprint 6 排程。

以上是 implementation 與交付狀態，不是 final QA verdict。

## Midpoint decision 與後續授權

Midpoint 提供 `continue / adjust / stop`，owner 當時選擇 **adjust**。該決定只核准 Todo 5 的三項收斂：

1. 建立小型 [LOCATION_PROFILES.md](../skills/advise-taiwan-astro-trip/references/LOCATION_PROFILES.md)，分開穩定前景、動態重查、安全、來源與限制。
2. 將回答深度分為區域級、已驗證地點級與精確拍攝點級；先在現有證據層級提供有用答案，每輪只問一個會實質改變答案的 focused question。
3. 將光害比較統一為同資料、同 layer 的 qualitative contract；其他資料只能作為有清楚標示與限制的補充。

這個 `adjust` 不曾授權 Cases 3–6、Sprint 6、狀態文件更新或 completion claim。

Todo 5 完成後，owner 於 2026-07-27 另作 **continue** 決定，授權 `Cases 3–6` 與 `Todo 6 validation artifacts`。後續工作依這個新授權執行，不是擴張解讀原本的 `adjust`。兩個 owner decisions 都必須保留在 durable history 中。

## 退休 checker 的證據邊界

Todo 6 與 Todo 7 的舊 checker 以 copied transcript、欄位或 exact-string prose 為檢查對象；即使沒有執行 Advisory Skill 或 Decision Skill，也可能維持綠燈。因此：

- 舊 normal、mutation、self-test、forward 與 generic-checker PASS 只證明當時那些文字 artifact 符合其固定斷言。
- 舊 checker 結果與針對 checker semantics／既有 artifact 的 review 是歷史 provenance，不是 fresh runtime evidence、external audit 或 behavioral approval。
- 不再用「executable assertions 已確認行為」、「generic checker independently confirmed behavior」或同義說法描述 Todo 6／7。
- 退休 checker 不再是產品依賴，也不納入 final approval gate。

## 現行證據模型

Final QA 以四種互補證據判斷，任何單一項都不能自行核准 completion：

1. **官方 Skill validator**：確認 Skill package 的結構與基本格式有效；它不是 representative behavioral QA。
2. **Repo regression**：[validate-regression.sh](../tests/validate-regression.sh) 通過，但其現有範圍是跨 Agent 的既有 promotional／missing-source fixtures，**不執行 `advise-taiwan-astro-trip`**，因此不能當作本 extension 的 runtime approval。
3. **隔離的 fresh-agent artifacts**：2026-08-03 已產生六個 isolated scenario artifacts，涵蓋地點比較、dated hard-failure、公開房況、構圖與參數、完整旅程及歧義地名。各 artifact 的 scenario-level 結果是 independent review 的輸入，不會因 artifact 內自行標示 PASS 就自動成為 final verdict。
4. **Independent review**：reviewer 必須直接檢查 current Skill、fresh artifacts、Decision 權責、來源與 freshness、動態資料限制、外部動作邊界、構圖圖像及 scope fidelity，再對 final gates 作出可追溯 verdict。

只有 fresh isolated execution 與 independent review 完成閉環後，才能考慮 final approval。Implementation receipt、validator、repo regression、歷史 transcript 或退休 checker 都不能替代這個閉環。

## Final verification 狀態

Final verification 仍未完成。F1–F4 必須以 current repository state 與 fresh artifacts 重新收斂：

- F1：plan compliance 與 durable delivery。
- F2：Skill quality、Decision authority 與 evidence-policy fidelity。
- F3：六個 isolated fresh-agent scenarios 的人工 QA 與 artifact review。
- F4：scope fidelity、狀態一致性與 completion-claim gate。

截至本 checkpoint，2026-08-08 五路 independent final review 已完成，結果為 F1 只在 local/source 層 PASS，F2/F3/F4 與 security/privacy 未通過。舊 scenario 自評、舊 verifier receipt 或退休 checker PASS 不得改寫成最終核准；狀態維持 **Pilot-ready; verification gate blocked**。

## 已觀察的行為範圍與限制

- 地點比較應保留使用者原始地名，將可能筆誤或別名標為待確認，沒有 exact pin 時不猜座標、精確光害或成功率。
- Dated request 必須重用既有 Decision Skill 的完整 contract；Advisory Skill 不得用缺輸入規則覆蓋已知 hard access failure 或自行創造平行 Go/No-Go 邏輯。
- 合法旅宿登記、一般定價與聯絡資料不等於指定日期有房、當次價格成立或已完成交易；無法公開驗證時必須明說。
- 構圖、參數與影像只在明確要求且器材條件確認後提供；[概念參考圖](../tests/assets/advise-taiwan-astro-trip/fenniaolin-d7200-11mm-composition-reference.png) 是 informed approximation，不是精確光學、天氣、天空亮度、銀河位置或現地預測。
- Complete-trip mode 只在明確 whole-trip request 啟用；查詢不等於聯絡、訂房、付款或導航動作。
- 「南澳」等區域沒有實際 shooting pin 時，不能精確比較前景、距離、人造光、進出與現地安全。
- 歷史救援、管理或道路資料可支持風險提示，但不能自行證明目前全面開放或封閉；真實出行前仍須重查最新管理、道路、海況與天氣。

## 下一步與狀態門檻

下一步改為依 [verification reconciliation checkpoint](astro-advisory-verification-reconciliation-2026-08-08.md) 重新凍結 current hashes、收斂 authoritative QA surface、補 Case 04 與 exact-pin runtime proof，並只在全部 gates 有 current evidence 時更新 final status。在此之前：

- Extension 只標記為 **Pilot-ready; verification gate blocked**，不標記 final complete、PASS 或 independently verified。
- Sprint 6 維持 **Not started; next cross-domain specialist Pilot**。
- 不以退休 Todo 6／7 checker、prose fixtures、assistant assertions、官方 validator 或 scope 不涵蓋本 Skill 的 repo regression 代替 behavioral approval。

Midpoint 的 **adjust** 與後續 **continue** 都已保存；implementation 已完成，但 2026-08-08 independent review 已明確拒絕 final approval，後續依 reconciliation checkpoint 收斂 blocker。
