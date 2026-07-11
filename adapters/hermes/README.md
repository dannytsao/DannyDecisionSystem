# Hermes Adapter

這個 adapter 讓 Hermes Agent 在乾淨、可重複的環境中測試 DDS 接收的 YouTube Knowledge Extractor。目前是 DannyOS 階段留下的評估工具，不是一般私人逐字稿處理工具。

## 為什麼需要 adapter

Hermes 平常會自動帶入長期記憶。這對一般助理工作很方便，但不適合測試 Skill，因為舊專案資料可能混入新的影片摘要。

實測發現：

- 單用 `--safe-mode`，PersonalKM 舊記憶仍然出現在 system prompt。
- 用 `--clone` 建立 profile，也會把舊記憶複製過去。
- 從空白 profile 開始，只複製模型 API 設定，才能真正隔離舊記憶。

這不是 YouTube Skill 的錯，而是 Hermes 啟動時載入背景資料的方式不同。

## 一次性設定

建立乾淨 profile：

```bash
hermes profile create dannyos-clean --no-alias
cp ~/.hermes/.env ~/.hermes/profiles/dannyos-clean/.env
```

只複製 `.env` 是為了沿用模型連線設定；不要使用 `--clone`，也不要複製 `MEMORY.md`、`USER.md` 或 `SOUL.md`。`dannyos-clean` 是已測試的歷史 profile 名稱，暫時保留到遺留測試完成。

## 使用方式

```bash
adapters/hermes/run-youtube-extractor.sh --confirm-external-send <逐字稿檔案>
```

例如：

```bash
adapters/hermes/run-youtube-extractor.sh \
  --confirm-external-send \
  tests/fixtures/promotional-agent-transcript.txt
```

adapter 會：

1. 載入完整 `SKILL.md`。
2. 載入完整 `OUTPUT_FORMAT.md`。
3. 加入指定逐字稿。
4. 使用 `dannyos-clean` profile。
5. 關閉 Hermes 記憶規則與個人設定，只保留無法讀檔、執行命令或傳資料的 `clarify` 提問工具；同時移除可能自動開啟 Kanban 工具的環境變數。
6. 只把最後答案輸出到 terminal。

目前 Hermes CLI 沒有可用的 prompt-file 參數，完整測試內容會短暫出現在本機命令列，並保存在 `dannyos-clean` 的 session 資料庫。因此 adapter 只允許 repository 內兩份已批准的合成 fixture，不接受私人或真實逐字稿。傳送前會核對 Skill、輸出格式與 fixture 三者的 SHA-256 數位指紋，任何內容被修改都會拒絕傳送。

每次執行都必須加入 `--confirm-external-send`，提醒使用者內容會傳送到 Anthropic。沒有直接答案時 adapter 會報錯，不會抓取其他 session 的答案。

名詞白話說明：

- adapter：幫兩套工具接起來的小程式。
- profile：Hermes 的獨立設定空間，像一個乾淨的新帳號。
- session：一次執行留下的本機紀錄。
- fixture：專門用來重複測試的合成範例。

供應商固定為 Anthropic，模型固定為 `anthropic/claude-sonnet-4.6`，不接受環境變數覆寫，避免確認內容與實際傳送目的地不同。
