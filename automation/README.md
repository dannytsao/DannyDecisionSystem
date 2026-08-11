# DDS Cloud Runner

這個目錄提供第一個可離開 Mac 執行的 DDS Cloud Run Job 入口。

目前唯一允許的 job 是 `regression`，它執行 Repository 既有的
`tests/validate-regression.sh`。這是雲端化基礎與安全 pilot，不宣稱已完成
任何正式外部資料、LLM、Email 或 Astro Advisory 自動化。

## 本機驗證

從 Repository 根目錄執行：

```bash
bash automation/tests/test-run-job.sh
```

直接執行 runner 時，可以指定可重複追蹤的 job 與 run ID：

```bash
DDS_JOB_NAME=dds-regression \
DDS_RUN_ID=local-001 \
DDS_ARTIFACT_DIR=/tmp/dds-runner \
bash automation/run-job.sh
```

Runner 會在 artifact directory 產生：

- `run-result.json`：狀態、exit code、時間與 log 路徑。
- `<run-id>.log`：本次 regression 的完整輸出。

`DDS_JOB_NAME` 與 `DDS_RUN_ID` 僅接受英數字、`.`、`_`、`-`，避免把未受控
內容直接放進 artifact 路徑或 JSON metadata。Runner 不接受任意 shell command，
也沒有外部傳送開關。

## GitHub Actions staging pilot

`.github/workflows/dds-regression-cloud-pilot.yml` 提供一條不依賴 Mac 的 staging
路徑：GitHub runner 會每天台北時間 08:07 執行同一個 `run-job.sh`，也可以使用
`workflow_dispatch` 手動觸發。GitHub 的 scheduled workflow 只會從 default branch
執行，因此這個 branch 的 workflow 必須先經過 review 並合併後，排程才會生效。

這條路徑只執行 regression，不讀取 secrets、不寄送外部訊息，也不代表 Cloud Run
production deployment 已完成。

## 建立 Cloud Run Job（部署前操作）

以下指令只是一份部署 runbook；本次變更不會替你執行雲端部署。

從 Repository 根目錄建立 image：

```bash
docker build -f automation/Dockerfile -t REGION-docker.pkg.dev/PROJECT_ID/dds/dds-runner:TAG .
docker push REGION-docker.pkg.dev/PROJECT_ID/dds/dds-runner:TAG
```

建立或更新 Cloud Run Job：

```bash
gcloud run jobs deploy dds-regression \
  --image REGION-docker.pkg.dev/PROJECT_ID/dds/dds-runner:TAG \
  --region REGION \
  --set-env-vars DDS_JOB_NAME=dds-regression
```

接著用 Cloud Scheduler 的專用 service account 觸發 Cloud Run Job。排程使用
`Asia/Taipei` 時區，並將每次執行視為 at-least-once；正式 job 必須保留
`CLOUD_RUN_EXECUTION` 或明確傳入的 `DDS_RUN_ID`，且 downstream side effect
必須以 run ID 做冪等處理。

例如，每天台北時間 08:07 觸發：

```bash
gcloud scheduler jobs create http dds-regression-daily \
  --location SCHEDULER_REGION \
  --schedule="7 8 * * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://run.googleapis.com/v2/projects/PROJECT_ID/locations/REGION/jobs/dds-regression:run" \
  --http-method=POST \
  --oauth-service-account-email="SCHEDULER_SERVICE_ACCOUNT"
```

## 尚未包含

- Cloud Scheduler resource 的實際建立。
- 生產 secrets 或 service account。
- 外部天氣、天文、LLM、Email adapter。
- 正式資料庫、結果保存與告警服務。

這些項目需要先決定 provider、資料保存方式與外部權限，不能由本機 runner
自動推定。
