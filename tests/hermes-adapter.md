# Hermes Adapter 驗證紀錄

日期：2026-07-11

## 為什麼需要隔離

預設 Hermes 與使用 `--clone` 建立的 profile 都會載入既有 PersonalKM 記憶。這會讓影片中不存在的內容混入答案。

最後採用 `dannyos-clean` 空白 profile，只複製模型 API 連線設定，不複製記憶、SOUL、Skills 或 sessions。

## Happy path

輸入：`tests/fixtures/promotional-agent-transcript.txt`

結果：行為 PASS，最終安全版本尚待一次 runtime 重跑。

加入 `clarify` 與完整 hash 鎖定前的隔離 adapter 已使用精確 session ID 核對；Hermes 紀錄顯示 `tool_call_count: 0`、`output_tokens: 1881`，模型正常完成回答。最終版本只進一步收窄權限並增加內容鎖定，但 happy path 重跑受到外部用量上限阻擋，尚未完成。

- 完整輸出十個指定區塊。
- 使用繁體中文。
- 英文關鍵詞表格包含 English、中文、使用情境三欄。
- 保留三個來源支持的行動，沒有混入 PersonalKM 或 Resolver Layer。
- 將無 benchmark 的十倍效能宣稱列入查證。
- 知識卡區塊與最終「是否值得建立知識卡」判斷一致，皆為否。

## Missing-source path

輸入：`tests/fixtures/missing-source.txt`

結果：最終安全版本 PASS。

Hermes 在來源空白時停止產生報告，要求提供 YouTube URL、逐字稿、字幕、文章或使用者筆記，沒有猜測內容。

正式 adapter 直接回傳拒絕文字，沒有進入十區塊報告。

## Adapter 輸出備援

Hermes one-shot 偶爾已完成模型回答並存入 session，但父程序沒有及時取得直接輸出。為避免誤拿上一次或同時執行的答案，正式 adapter 不再自動抓取最新 session；直接輸出空白就判定失敗。

人工測試需要查閱 session 時，必須先取得本次 session ID，再用 `--session-id` 精確匯出。

## 外部傳送限制

Hermes CLI 目前沒有可用的 prompt-file 參數。為避免私人內容出現在命令列或 session，adapter 只允許 `tests/fixtures/` 中兩份已批准的合成資料，並要求明確加入 `--confirm-external-send`。其他檔案會直接拒絕。

Skill、輸出格式與兩份 fixture 都以 SHA-256 數位指紋鎖定內容；檔名相同但內容不同也會拒絕。供應商和模型固定為 Anthropic Claude Sonnet，不接受環境變數覆寫。

Hermes 空 toolsets 會退回預設工具，因此 adapter 改為只提供 `clarify`。這個工具只能提出問題，不能讀檔、執行命令或傳送資料；正式測試的工具呼叫數仍為 0。

啟動 Hermes 時另用 `env -u HERMES_KANBAN_TASK` 清除可能自動附加 Kanban 工具的環境變數，確保實際權限不會比文件宣告更大。
