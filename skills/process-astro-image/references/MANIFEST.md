# Manifest and dry-run contract

`build_manifest.py` 是 Pilot 的安全 intake 工具，不是影像處理器。

## Invocation

```text
uv run skills/process-astro-image/scripts/build_manifest.py SESSION_DIR [--output MANIFEST.json]
```

若未指定 `--output`，JSON 會輸出到 stdout；指定輸出路徑時，工具只建立或覆寫該新 manifest 路徑，不會寫入 session 內的原始影像。

## Frame classification

- `light`：支援的 FITS／RAW 檔案中，檔名與路徑沒有 `dark`、`flat`、`bias` 或 `offset` token。
- `dark`：含 `dark` token。
- `flat`：含 `flat` token。
- `bias`：含 `bias` 或 `offset` token。
- `unknown`：非支援影像副檔名或無法初步分類的檔案；存在時會阻擋 dry-run。

這是 intake 分類，不代表已驗證 FITS header。不同尺寸、bit depth、CFA、濾鏡或 session metadata 必須由後續 header gate 檢查。

`.DS_Store` 與本工具產生的 `manifest.json` 會被視為 sidecar，不會被當成影像；其他未知檔案仍會阻擋 preflight。

## FITS header gate

目前 Pilot 會讀取 FITS primary header 的 `SIMPLE`、`BITPIX`、`NAXIS1`、`NAXIS2`，並記錄可選的 `BAYERPAT` 與 `FILTER`。缺少必要欄位、非 ASCII header、非正尺寸或不是 `SIMPLE = T` 時，該檔案標為 `metadata_status=invalid`，整個 preflight 進入 `blocked`。

已解析 FITS 必須有一致的寬度、高度、`BITPIX` 與 Bayer pattern；filter 可以不同，以支援 LRGB 或多濾鏡 session。RAW 檔案沒有 FITS header，會標為 `pending`，在後續 RAW metadata gate 完成前不得執行 recipe。

## Safety invariants

- 每個檔案以相對於 session root 的路徑記錄。
- 每個檔案計算 SHA-256；不可因建立 manifest 而改寫輸入檔。
- `preflight.status=ready_for_review` 只表示有 Lights 且沒有未知檔案，不表示可以直接執行。
- `plan.execution_enabled` 在 Pilot slice 固定為 `false`。
- 缺少 Lights 或存在 unknown frame 時，`preflight.status=blocked` 並列出對應 check 名稱。
