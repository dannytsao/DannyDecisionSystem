# Siril dry-run contract

`generate_siril_script.py` 只產生 `.ssf`，不呼叫 Siril。Siril 的官方文件說明 `.ssf` 可由 GUI 的 `@` 指令或 `siril-cli -s` 執行；本 Skill 不會自動呼叫後者。取得明確核准後，可在新的隔離 run 目錄人工執行已審查腳本，並記錄 exit code、註冊比例與輸出檔。

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

`register -2pass` 後的 `seqapplyreg` 是必要步驟；它會產生供 `stack` 使用的已對齊序列。BXT／SXT／NXT、calibration mapping、QA 與真正執行留待後續核准的 adapter slice。
