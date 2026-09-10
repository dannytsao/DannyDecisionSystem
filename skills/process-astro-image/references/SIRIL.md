# Siril dry-run contract

`generate_siril_script.py` 只產生 `.ssf`，不呼叫 Siril。Siril 的官方文件說明 `.ssf` 可由 GUI 的 `@` 指令或 `siril-cli -s` 執行；本 Skill 不會自動呼叫後者。取得明確核准後，可在新的隔離 run 目錄人工執行已審查腳本，並記錄 exit code、註冊比例與輸出檔。

Siril 的 `save` 命令只寫 FITS；因此每個 `result*.fit` 產生後，必須再執行 `scripts/export_dng_sidecars.py`。該工具優先用 Siril 輸出 16-bit PPM，再用 DNGLab `makedng --map 0:raw` 寫出 Linear DNG，並用 DNGLab structure 檢查 `DNGVersion`。若 DNGLab 不可用或 DNG 驗證失敗，會改用 Siril `savetif32` 產生同 stem 的 TIFF。這些是已處理影像的 companion，不是原始 Bayer RAW；DNG 與 TIFF 都失敗時才會產生 `Failed/failed-report.md`，不會建立假 DNG。

官方參考：[Siril scripting](https://siril.readthedocs.io/en/stable/Scripts.html)、[Siril script files](https://siril.readthedocs.io/en/latest/scripts/Script-files.html)、[Siril commands 1.4.4](https://siril.readthedocs.io/en/stable/Commands.html)。

## Invocation

```text
uv run skills/process-astro-image/scripts/generate_siril_script.py SESSION_DIR [--output SCRIPT.ssf]
```

輸出預設落在 session 的上一層，且工具拒絕覆寫既有檔案或把 `.ssf` 寫進輸入 session。

## Supported Pilot recipe

產生器目前只接受：

- 所有輸入都是已通過最小 FITS header gate 的 FITS。
- 所有 Lights 位於同一個目錄。
- 不存在尚未明確配對的 Darks、Flats 或 Bias；有 calibration 時先阻擋，不靜默忽略。
- OSC 依 `BAYERPAT` 加入 `-debayer`；Mono 不加入。

產生的命令順序是：

```text
requires 1.4.0
cd <absolute session>
cd <absolute lights directory>
convert light -out=../process [-debayer]
cd ../process
register light -2pass -maxstars=500 -interp=lanczos3
seqapplyreg light -interp=lanczos3
stack r_light rej winsorized 3 3 -norm=auto -weight=wfwhm -out=../result -32b
cd ..
load result
save result_linear
autostretch
save result_autostretched
savepng result_preview
close
```

執行後的 DNG／TIFF 配對：

```text
uv run --script scripts/export_dng_sidecars.py RUN_DIR [--siril-cli PATH] [--dnglab PATH]
```

正式受控執行應使用 wrapper，確保 Siril 非零 exit 或 DNG/TIFF 配對都失敗時留下報告：

```text
uv run --script scripts/run_siril.py SCRIPT.ssf RUN_DIR [--siril-cli PATH]
```

`register -2pass` 後的 `seqapplyreg` 是必要步驟；它會產生供 `stack` 使用的已對齊序列。BXT／SXT／NXT、calibration mapping、QA 與真正執行留待後續核准的 adapter slice。

若一個資料夾包含多個日期或 mosaic 視野，先執行 `prepare_tile_runs.py`，再對每個 tile 產生與執行獨立 `.ssf`。已完成 plate solving 的跨視野合成，預設仍用 `scripts/wcs_mosaic.py` 作為可稽核基準；不要把沒有足夠星點重疊的 tile 放進同一個 `register` sequence。

若要試用 Siril 原生天文 mosaic，可先執行 `scripts/generate_native_mosaic_script.py RUN_DIR` 產生 review-only `.ssf`，確認後再以 `run_siril.py` 執行。此 recipe 使用 `seqplatesolve -force -nocache`（每張 tile 使用自己的 WCS/視野資訊）、`seqapplyreg -framing=max`，以及 `stack -maximize -overlap_norm -feather=150 -norm=addscale`。`-nocache` 對跨日期／跨視野資料很重要；若省略，Siril 可能只用第一張影像的星表範圍而漏解其他 tile。原生 mosaic 仍必須人工檢查背景接縫，沒有 flat 時不得直接視為最終成品。
