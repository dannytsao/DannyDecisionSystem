---
name: process-astro-image
description: Inspect an astrophotography session and produce a safe, reproducible dry-run post-processing plan with manifest, calibration grouping, Siril and RC-Astro prerequisites, QA gates, and explicit failure handling. Use for deep-sky FITS or camera-RAW post-processing planning and controlled local execution; do not use for deciding whether to travel or shoot, and do not overwrite raw files.
---

# Process Astro Image

## Job to be done

將一組天文影像整理成可核准、可重跑、可稽核的後期處理計畫。LLM 可以解釋或提出 recipe，但像素處理只由已檢查的本機工具 adapter 執行。

## Required inputs

- Session 目錄，或明確的 Lights、Darks、Flats、Bias 檔案。
- 影像目標與意圖，例如自然星場、starless、窄頻或 LRGB。
- 本機 Siril CLI 與使用者已授權的 RC-Astro CLI。

Pilot slice 使用 `scripts/build_manifest.py` 建立輸入清單與 dry-run JSON，再由 `scripts/generate_siril_script.py` 產生只供審查的 `.ssf`。它會掃描 FITS／RAW 副檔名、依檔名與目錄初步分組、計算 SHA-256，並對 FITS primary header 執行最小必要 gate。含多日期或 mosaic 視野時，使用 `scripts/prepare_tile_runs.py` 依 `DATE-OBS`、`FILTER` 與 RA/DEC 建立隔離 tile runs。執行方式與輸出格式見 [MANIFEST.md](references/MANIFEST.md)、[GROUPING.md](references/GROUPING.md) 與 [SIRIL.md](references/SIRIL.md)。

缺少 Lights、出現未知檔案、資料不一致、工具／模型／授權不可用，或未取得使用者核准時，必須回報 `blocked`／`Insufficient evidence`，不可猜測或繼續執行。

## Process

1. 保持原始 session 唯讀，先建立 manifest 與 checksum。
2. 檢查檔案類型、初步 frame kind、FITS header、拍攝日期／視野／濾鏡與可重跑的輸入路徑。
3. 產生 dry-run recipe：Siril 校準／註冊／堆疊，接著依核准 recipe 使用 RC-Astro BXT／SXT／NXT，最後 QA 與報告；目前只產生 Siril `.ssf`，不執行。
4. 把需要使用者決定的 recipe、缺漏資料與主要風險列出，等待核准。
5. 本 Skill 目前仍不會自動呼叫工具；取得明確核准後，含混合視野時先用 `scripts/prepare_tile_runs.py` 建立隔離 tile runs，再使用 `scripts/run_siril.py` 逐一執行已審查的 Siril `.ssf`，並自動呼叫 DNG/TIFF companion exporter。任一步驟失敗都必須寫入 `Failed/failed-report.md` 並停止；RC-Astro 仍未開放。
6. 完成 tile run 後使用 `scripts/tile_qa.py` 產生註冊率摘要、排除 frame 清單與預覽 contact sheet。註冊被排除是品質選擇，不自動視為工具失敗；輸出 companion 缺漏或 QA 工具錯誤仍須寫入 `Failed/failed-report.md`。
7. Tile QA 通過後，使用 `scripts/plate_solve_tiles.py` 對每個 `result_linear.fit` 做 WCS 解算，輸出獨立的 `plate_solved.fit` 與 `qa/plate-solve.json`；解算只確認座標，不直接代表可合成。解算失敗會保留逐 tile log 並寫入 `Failed/failed-report.md`。

## Required output

每次 intake 至少產生：

- `manifest`：相對路徑、frame kind、副檔名、大小、SHA-256 與可用的 FITS metadata。
- `groups.json`：日期、濾鏡、視野 tile 與每組輸入檔案清單；每組可獨立重跑。
- `preflight`：`ready_for_review` 或 `blocked`，以及 blocking checks。
- `plan`：步驟、需核准旗標與 `execution_enabled=false`。
- Siril `.ssf`：絕對路徑、保守的 convert／register／seqapplyreg／stack／preview 命令，供人工檢查。
- Result companions：每個 `result*.fit` 優先產生同 stem 的真正 DNG；若 DNG 工具或驗證失敗，改由 Siril 產生同 stem 的 `.tif`（或 `.tiff`）。兩者都失敗時才寫入 `Failed/failed-report.md`，不得只改副檔名。
- 警告：FITS header、工具版本、模型與授權等尚未完成的 gate。
- tile QA：`tile-qa.md`、`qa/tile-qa.json` 與 `qa/contact-sheet.png`；這些是 mosaic 前的審查資料，不代表最終影像已通過科學或美學 QA。
- plate solving：`plate-solve.md`、`qa/plate-solve.json`、`qa/plate-solve-logs/` 與各 tile 的 `plate_solved.fit`；必須先用 WCS footprint 驗證重疊，再產生 mosaic recipe。

後續完整 run 還必須保存校準後、堆疊後、BXT／SXT／NXT 後的中間產物、QA 與 `report.md`；預覽不是科學測量或成功保證。

## Boundaries

- 不取代 `plan-astro-photo-session` 的出勤 Go／Conditional／No-Go 判斷。
- 不修改 DDS Runtime，不建立 LINE、雲端服務、排程或自動下載模型。
- 不把單一 LLM、GUI、Siril 或 RC-Astro 當作 DDS 核心；工具必須透過可替換 adapter。
- 不複製 GPL 專案程式碼；外部參考專案的 commit 與 LICENSE／NOTICE 必須在實作前固定並審查。

## Validation

- `scripts/build_manifest.py` 的測試涵蓋可審查的 Lights + calibration 與缺 Lights／未知檔案的 failure path。
- 原始檔 SHA-256 不因 intake 改變。
- `execution_enabled` 在此 Pilot slice 永遠為 `false`。
- 人工執行不會改變 manifest 的 `execution_enabled=false`；它是受控驗證，不是 DDS Runtime 的正式 execution adapter。
- 使用相同輸入內容重跑時，檔案清單、分類與 hash 應一致；時間或工具環境差異要明確列出。
