# 天文影像後期處理 Agent Skill Proposal

Status: Accepted for Pilot（尚未建立正式 Skill 或修改 DDS Runtime）

Scope approval: Danny 於 2026-09-01 同意先建立 Proposal，並以本文件的 Pilot 範圍作為下一步實作邊界。

## Name

`process-astro-image`

## Problem

深空影像後期處理會反覆遇到資料整理、校準檔配對、Siril 流程選擇、RC-Astro 參數、星點與背景品質檢查，以及中間結果保存等問題。手動執行容易覆寫原始資料、遺失參數，或在資料不足時產生看似完成但不可追溯的結果。

這個能力的 Job to be done 是：

> 將一組天文影像安全地整理成可核准、可重跑、可稽核的後期處理流程，並由確定性的影像工具執行，而不是讓 LLM 直接修改像素。

## Type

- [x] Supporting Skill
- [ ] Decision Skill
- [ ] Shared Utility
- [ ] Independent Tool

它提供資料證據、處理計畫與受控執行；不取代 `plan-astro-photo-session` 的「是否值得出發拍攝」決策。

## Inputs and Evidence

### 最少必要輸入

- 影像 session 目錄或明確的 Lights/Darks/Flats/Bias 清單。
- 拍攝目標與處理意圖，例如自然星場、星點抑制、窄頻或 LRGB。
- 可讀取的 FITS header，至少包含影像尺寸、資料型別與必要的 CFA／濾鏡資訊。
- 本機可執行工具與版本：Siril CLI，以及使用者已授權並可執行的 RC-Astro CLI。

### 可選輸入

- 相機、濾鏡、焦距、binning、gain／offset 等設備資訊。
- 使用者指定的 recipe、輸出格式、品質門檻與是否需要 starless 結果。
- 既有 master calibration、前次 manifest 或重新執行的 run ID。

### 缺少輸入時

- 缺少校準檔、FITS metadata 不一致、工具不存在、模型未安裝或授權不可用時，停止在 preflight，輸出 `Insufficient evidence` 或 `Blocked`，不得猜測或繼續寫入結果。
- 原始檔案一律視為唯讀；任何寫入都必須落在新的 run 目錄。

## Proposed Workflow

```text
建立 manifest 與 checksum
→ 讀取 FITS header、分類與配對校準檔
→ 產生 dry-run recipe 與風險摘要
→ 使用者核准
→ Siril 校準／註冊／堆疊
→ RC-Astro BXT／SXT／NXT（依核准 recipe）
→ QA、預覽與中間產物保存
→ 產生可重跑的報告
```

LLM 僅可提出或解釋 recipe；實際檔案處理由 Siril／RC-Astro adapter 執行。每一步要記錄工具版本、參數、輸入 hash、輸出路徑與失敗原因。

## Output

每次 run 必須產生：

- `manifest`：輸入檔案、header 摘要、checksum 與分類結果。
- `plan`：dry-run 顯示的步驟、參數、預期輸出與風險。
- 中間產物：校準後、註冊後、堆疊後、BXT／SXT／NXT 後及最終輸出。
- `qa`：NaN、裁切、背景平坦度、星點統計、必要時的 SNR 或 histogram 摘要。
- `report.md`：結論、版本、模型、參數、警告、失敗步驟與重跑方式。
- Result companions：每個 `result*.fit` 都必須有同 stem 的 `result*.dng`；DNG 無法產生或驗證時必須輸出 `failed-report.md`，不得只改副檔名。
- 前後預覽；預覽不得被當成精確科學測量或成功保證。

## Reference Projects and Reuse Policy

以下專案只作為設計與 adapter 參考，第一版不直接 vendoring：

| 專案 | 參考價值 | 採用方式 | 授權注意 |
| --- | --- | --- | --- |
| [ASTRO-1](https://github.com/ohlee-one/astro-1) | 設定檔、dry-run、`pipeline → engines` 分層 | 參考流程與設定模型，重新實作 DDS adapter | MIT；保留原授權聲明 |
| [siril-astro-processor](https://github.com/portkeys/siril-astro-processor) | Skill 觸發、預檢、OSC／Mono 偵測、recipes、中間產物 | 參考 Skill contract 與 Siril script 產生方式 | MIT；先固定研究用 commit |
| [Muphrid](https://github.com/Jomonsugi/muphrid) | LangGraph、變體比較、QA 指標、人工核准與 checkpoint | 只吸收 Agent／HITL 設計，不直接併入核心 | GPL-3.0；另有 LLM API、GraXpert 等依賴 |
| [poto-siril](https://github.com/TomyCesaille/poto-siril) | Session 整理、校準檔匹配、Siril preprocessing | 參考 intake／calibration 層 | GPL-3.0；不複製程式碼進 DDS |
| [naztronaut/siril-scripts](https://github.com/naztronaut/siril-scripts) | Seestar／OSC、多批次與背景處理 | 只挑選適用設備的腳本概念 | GPL-3.0-or-later；確認資料型態後使用 |

進入實作前，必須固定實際 commit、讀取 LICENSE／NOTICE，並確認是否需要隔離 GPL 程式碼。不得以「參考」名義複製可構成衍生作品的程式碼。

## Existing Overlap

- `skills/plan-astro-photo-session/`：負責特定日期與地點的拍攝 Go／Conditional／No-Go；本 Skill 不重寫天氣或出勤決策。
- `skills/advise-taiwan-astro-trip/`：負責地點、住宿與旅程支援；本 Skill 不做訂房或交通操作。
- DDS Runtime：只使用既有的 skill orchestration、evidence、risk、checkpoint 邊界；本 Proposal 不修改 Runtime。
- Siril 與 RC-Astro：視為可替換的 Tool Adapter，不把任何單一 GUI、LLM 或模型當成 DDS 核心。

## Risk and Failure Cost

### 主要風險

- 覆寫或誤刪原始影像。
- 校準檔或 CFA／濾鏡分類錯誤，造成不可逆的錯誤堆疊。
- BXT／SXT／NXT 過度處理，產生 halo、星點變形或背景偽影。
- 工具版本、模型或授權變動，使重跑結果不同或無法執行。
- 報告只顯示命令成功，卻沒有獨立 QA 或可讀取的輸出。

### 必須 fail closed 的情況

- 輸入 hash 改變或輸出路徑落入原始目錄。
- 影像尺寸、bit depth、濾鏡或 CFA metadata 不一致。
- 缺少必要校準資料、工具、模型或有效授權。
- QA 發現 NaN、嚴重裁切、空輸出或預期步驟未執行。
- 使用者尚未核准 dry-run recipe。

## Pilot

Pilot 僅使用本機資料與本機工具，不建立雲端服務、LINE 介面、排程或自動下載模型。

### Case 1 — Happy path：OSC／Seestar session

- 輸入：同一相機與濾鏡的一組 Lights，含可匹配的 calibration。
- 預期：建立 manifest，dry-run 後經核准完成 Siril 校準／堆疊，再執行 RC-Astro recipe，保留中間檔與報告。
- 驗收：原始 hash 不變；run 可從 manifest 重跑；報告含版本、參數與 QA。

### Case 2 — 多批次：LRGB 或雙窄頻

- 輸入：多 session、不同濾鏡或不同曝光條件，需分組後合成。
- 預期：先顯示分組與合成計畫；不得把不同 metadata 的資料靜默混合。
- 驗收：每個 filter／session 可追溯；失敗時能只重跑受影響分支。

### Case 3 — Failure path：資料或環境不足

- 輸入：缺少 Flats、header 不一致、RC-Astro 模型／授權不可用，或 QA 發現空輸出。
- 預期：在 preflight 或 QA 停止，明確列出補件／修復方式；不產生誤導性的「完成」結論。
- 驗收：不覆寫原始檔、不洩漏憑證、不繼續執行後續步驟。

## Pilot Acceptance Criteria

Pilot 通過前，必須證明：

1. dry-run 能清楚呈現完整處理計畫與風險。
2. 原始資料唯讀，所有輸出都有 run 目錄與 checksum。
3. Siril 與 RC-Astro 執行結果可由報告重建。
4. 缺資料、缺工具、缺模型、授權失效及 QA 失敗都會 fail closed。
5. 同一 manifest 與 recipe 可重跑，差異能指出工具／模型／參數變更。
6. 不修改 DDS Runtime，不與既有出勤決策 Skill 重疊。

## Decision

- [x] Accept for Pilot
- [ ] Merge with Existing Capability
- [x] Keep Independent
- [ ] Reject

### Danny 仍需在 Pilot midpoint 決定

- `continue`：進入正式 Skill skeleton 與本機 adapter 實作。
- `adjust`：調整資料類型、設備、recipe 或 QA 範圍。
- `stop`：保留 Proposal，不建立正式能力。

本文件通過後只代表允許進入 Pilot，不代表 Skill 已完成、RC-Astro 已被 DDS 正式支援，或 DDS Sprint 6 已開始。

## Pilot progress — 2026-09-01

已完成第一個安全 intake slice：

- 正式 Skill skeleton 與 UI metadata 已建立。
- `build_manifest.py` 可掃描 FITS／RAW、分類 frame kind、計算 SHA-256 並產生不可執行的 dry-run plan。
- FITS primary header gate 已檢查 `SIMPLE`、`BITPIX`、`NAXIS1`、`NAXIS2`，並記錄 `BAYERPAT`／`FILTER`。
- 無 Lights、未知檔案、無效 FITS header 或已解析 FITS metadata 不一致時會 fail closed。
- Siril dry-run script generator 已可從通過 gate 的單一 Lights 目錄產生絕對路徑 `.ssf`；OSC／Mono 會依 `BAYERPAT` 選擇是否加入 `-debayer`。
- 目前測試與 validator 通過；此 slice 的 `execution_enabled` 固定為 `false`。

尚未開始 Siril／RC-Astro tool execution adapter。Calibration mapping、RAW metadata、QA 與實際執行仍未開放；兩者都不得在未核准 recipe 下執行。

## Real-data Pilot execution evidence — M106, 2026-09-09

- Input: `/Users/dannytsao/Documents/M106/`，其中 `Lights/` 有 10 個 `.fit` 檔案；根目錄的 macOS `.DS_Store` 已由 intake 明確忽略。
- Manifest: `ready_for_review`；`light=10`、`dark=0`、`flat=0`、`bias=0`、`unknown=0`。
- Parsed metadata: 所有檔案一致為 1080×1920、16-bit、`BAYERPAT=GRBG`、`FILTER=IRCUT`；10 個檔案 checksum 均已記錄。
- Dry-run: `/Users/dannytsao/Documents/M106-siril-dry-run.ssf` 已產生，包含 OSC `-debayer`、`register -2pass`、`seqapplyreg`、加權 rejection stack 與預覽保存。
- Isolated execution: 為避免寫入原始 session，將 Lights 原樣複製到 `/Users/dannytsao/Documents/M106-pilot-run-20260909/`，並以 `/Applications/Siril.app/Contents/MacOS/siril-cli -s /Users/dannytsao/Documents/M106-pilot-run-20260909.ssf` 執行；Siril 1.4.4 exit code=0。
- Registration result: 10 個 frame 轉換成功，但只有 3/10 成功註冊；其餘 7 個被 Siril 排除。`result.fit`（32-bit FITS）、`result_linear.fit`、`result_autostretched.fit` 與 `result_preview.png` 已產生，因此這是「工具流程成功、影像品質條件式通過」而非完整 10-frame 成功。
- DNG companions: 使用 DNGLab 0.8.0 將每個 result FITS 經 16-bit PPM 中介轉為 Linear DNG，並以 structure 檢查 `DNGVersion`；`result.dng`、`result_linear.dng`、`result_autostretched.dng` 均已產生。這些是已處理影像的 companion，不宣稱保留原始 Bayer RAW 語義。
- Failure diagnosis: `light_.seq` 只為 frame 8–10 寫入 registration transform；FITS header 顯示 frame 7→8 有 3 分 34 秒間隔且 RA/DEC 分組改變。轉換後像素峰值也顯示 frame 1–7 明顯較弱（max 40,188–43,231、>50,000 像素為 0），frame 8–10 則為 max 63,500–65,202、>50,000 像素 22–27 個。證據支持「構圖變化 + 前 7 張星點對比不足」的組合原因；無法僅由現有資料判定是失焦、透光度、追蹤或其他拍攝因素。
- Visual/quality caveat: 預覽仍呈現明顯雜訊，且目前只有 3 張 frame 進入 stack；不得把它視為 M106 最終成品或 RC-Astro 輸入品質已獲保證。
- Safety: 原始 `/Users/dannytsao/Documents/M106/Lights/` 10 個檔案與隔離副本 SHA-256 完全一致；原始 session 未被改寫。RC-Astro、calibration mapping 與獨立 QA 仍未開放。
- Recovery note: 首次腳本使用 Siril 不接受的絕對 `-out` 寫法而中止；錯誤產物已移至 `/Users/dannytsao/Documents/M106-pilot-failed-20260909/` 保留，後續腳本改用官方相對輸出路徑後重跑成功。
