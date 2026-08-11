# Scheduled Task Prompt

建立排程前，請先替換所有雙大括號內的變數。

```md
使用 $monitor-astro-opportunity 的 Run mode 執行以下任務。

## 監測任務

- 地點：{{location_name}}
- 座標：{{coordinates}}
- 拍攝標的：{{target}}
- 預判範圍：{{forecast_window}}
- 時區：{{timezone}}

## 排程條件

- 生效日期：{{active_from}}
- 結束日期：{{active_until}}
- 執行頻率：{{frequency}}
- 執行時間：{{run_at}}
- 錯過排程：跳過，不補跑或補寄已過期的報告

## 每次執行流程

1. 如果執行日期不在生效期間內，停止執行且不要寄信。
2. 除非已指定固定日期，否則從本次執行日期起計算預判範圍。
3. 每個預判夜晚都必須使用 $plan-astro-photo-session 進行判斷。
4. 每次重新取得當下最新的氣象觀測、衛星或雷達、預報、天文、道路及安全資料。不得使用模型記憶或先前報告代替。
5. 如果無法確認關鍵資料的新鮮度或涵蓋範圍，輸出 `Defer` 或 `Insufficient evidence`。
6. 產生一份結論優先的繁體中文多日報告：先用一句話說明是否值得出勤，再為每個夜晚建立獨立標題卡片；使用短條列呈現氣象、月光與主要風險，不使用長句塞在寬表格欄位中。明確分開「天文最佳時段」與「出勤建議」。如果目前沒有值得推薦的日期，直接說明。
7. 透過 {{delivery_method}} 將報告傳送給 {{recipient}}。

## Email 主旨

DDS｜{{location_name}}未來{{forecast_window}}{{target}}機會｜YYYY-MM-DD

每次執行最多寄送一封 Email。Email 必須使用 UTF-8 且 body 非空；寄出後用 exact subject + `in:anywhere` 查回，讀取並驗證收件者與 body 非空，寄給 `me` 時若缺少 `INBOX` label 則補上。若無法確認是否寄送成功，不得重試；若寄送失敗或回查驗證失敗，將完整報告保留在 Scheduled task 結果中，並說明錯誤。
```
