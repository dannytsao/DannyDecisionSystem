# Tile QA

`tile_qa.py` 讀取每個 tile 的 Siril `process/light_.seq`，整理總張數、成功註冊張數、被排除的原始檔名與 result FITS companion 狀態。它會寫出：

- `tile-qa.md`：繁體中文摘要與需複查清單。
- `qa/tile-qa.json`：供後續 agent 或 mosaic adapter 使用的結構化資料。
- `qa/contact-sheet.png`：所有 tile 預覽的縮圖總覽。

預設註冊率門檻為 80%，只是人工複查排序，不是自動刪除或重跑規則。被 Siril 排除的 frame 屬於品質選擇；只有工具執行失敗、輸出缺漏或 companion 驗證失敗才是 `Failed/failed-report.md` 的工具層級失敗。

Contact sheet 若出現多邊形黑邊、大片空白或明顯背景梯度，先裁切有效重疊區並完成 plate solving，再進行 mosaic；不要在 RC-Astro 中用銳化或降噪掩蓋註冊／覆蓋問題。

## Plate solving

`plate_solve_tiles.py` 以 FITS header 的 RA/DEC、250 mm 焦長與 2.9 µm 像素尺寸作為初始值，呼叫 Siril 1.4 的 `platesolve`。它把 WCS 寫到新的 `plate_solved.fit`，不會覆寫 `result_linear.fit`；每個 tile 的完整 Siril log 保存在 `qa/plate-solve-logs/`。

解算成功只表示座標可被辨識。下一步仍須讀取 WCS footprint，確認 tile 的真實重疊、裁切邊界與不同年度的尺度／方向，再允許 mosaic adapter 執行。

## Mosaic dry-run

`prepare_mosaic_run.py` 讀取 `qa/plate-solve.json`，只選擇狀態為「通過」且 tile 名稱含 IRCUT 的 `plate_solved.fit`。它以符號連結建立隔離 `Lights/`，輸出 `mosaic-input.json` 與執行前說明；不再把所有 tile 放入同一個 Siril `register` sequence。

`wcs_mosaic.py` 使用 `astropy.wcs` 與 `reproject.reproject_and_coadd`，依所有 tile 的 WCS footprint 建立共同 TAN 網格，再逐 channel 做 bilinear 重投影、共同背景中位數對齊與 overlap background matching。它會產生 `result_wcs_mosaic.fit`、`wcs-mosaic.md`、`qa/wcs-mosaic.json` 與只供審查的 `wcs-mosaic-preview.ssf`。背景／平場梯度仍需人工預覽 QA，不可只看幾何覆蓋率。

原生 Siril mosaic 是可選的交叉驗證流程：`generate_native_mosaic_script.py` 產生 `seqplatesolve -force -nocache` → `seqapplyreg -framing=max` → `stack -maximize -overlap_norm -feather` 的腳本。它可以提高跨視野幾何配準的可重現性，但不會自動消除沒有 flat 造成的整片梯度；若預覽仍看得到 tile 邊界，QA 必須標示失敗並回到 flat／pseudo-flat 校正。

`mosaic_qa.py` 會再讀取執行後的 `process/tile_.seq`。若實際註冊數低於門檻，即使 Siril 回傳 0，也會產生中文 `mosaic-qa.md` 與 `Failed/failed-report.md`；這可避免把只有部分 tile 的影像誤當成完整 mosaic。
