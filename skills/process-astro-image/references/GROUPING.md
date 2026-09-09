# 日期／視野／濾鏡分組

`prepare_tile_runs.py` 將混合 session 拆成可獨立審查的 tile runs：

```text
DATE-OBS 日期
→ FILTER 濾鏡
→ RA/DEC 視野 anchor（預設半徑 0.4°）
→ 個別 Siril register／stack
→ 後續 mosaic 合成
```

視野 anchor 是候選分組，不是 plate solving 的最終證明；執行前仍要檢查 `groups.json` 與每組 dry-run。缺少 RA/DEC 的檔案會進入 unknown view，不能假設它們一定重疊。

使用方式：

```text
uv run --script scripts/prepare_tile_runs.py SESSION_DIR OUTPUT_DIR [--view-radius-deg 0.4]
```

輸出目錄包含 `groups.json`、每組的 `manifest.json`、Lights 符號連結與 `.ssf`。原始檔保持唯讀；每組後續以 `scripts/run_siril.py` 執行。
