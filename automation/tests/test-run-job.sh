#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
artifact_dir="$(mktemp -d)"
log_file="${artifact_dir}/runner.log"
trap 'rm -rf "${artifact_dir}"' EXIT

if ! DDS_ARTIFACT_DIR="${artifact_dir}" \
  DDS_JOB_NAME="dds-regression-test" \
  DDS_RUN_ID="test-run-001" \
  bash "${repo_root}/automation/run-job.sh" >"${log_file}"; then
  echo "runner should complete the approved regression job" >&2
  exit 1
fi

result_file="${artifact_dir}/run-result.json"
test -f "${result_file}"
rg -q '"job_name":"dds-regression-test"' "${result_file}"
rg -q '"run_id":"test-run-001"' "${result_file}"
rg -q '"status":"succeeded"' "${result_file}"
rg -q '跨 Agent 回歸檢查通過。' "${log_file}"

if DDS_RUN_MODE="unsupported" DDS_ARTIFACT_DIR="${artifact_dir}" \
  bash "${repo_root}/automation/run-job.sh" >"${artifact_dir}/invalid-mode.log" 2>&1; then
  echo "runner should reject an unsupported mode" >&2
  exit 1
fi

rg -q 'unsupported DDS_RUN_MODE: unsupported' "${artifact_dir}/invalid-mode.log"

echo "Cloud runner end-to-end test passed."
