# Tile QA

`tile_qa.py` 讀取每個 tile 的 Siril `process/light_.seq`，整理總張數、成功註冊張數、被排除的原始檔名與 result FITS companion 狀態。它會寫出：

- `tile-qa.md`：繁體中文摘要與需複查清單。
- `qa/tile-qa.json`：供後續 agent 或 mosaic adapter 使用的結構化資料。
- `qa/contact-sheet.png`：所有 tile 預覽的縮圖總覽。

預設註冊率門檻為 80%，只是人工複查排序，不是自動刪除或重跑規則。被 Siril 排除的 frame 屬於品質選擇；只有工具執行失敗、輸出缺漏或 companion 驗證失敗才是 `Failed/failed-report.md` 的工具層級失敗。

Contact sheet 若出現多邊形黑邊、大片空白或明顯背景梯度，先裁切有效重疊區並完成 plate solving，再進行 mosaic；不要在 RC-Astro 中用銳化或降噪掩蓋註冊／覆蓋問題。
