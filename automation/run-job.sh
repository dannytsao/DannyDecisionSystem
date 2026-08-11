#!/usr/bin/env bash

set -Eeuo pipefail

automation_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${automation_dir}/.." && pwd)"

job_name="${DDS_JOB_NAME:-dds-regression}"
run_id="${DDS_RUN_ID:-${CLOUD_RUN_EXECUTION:-local-$(date -u +%Y%m%dT%H%M%SZ)}}"
artifact_dir="${DDS_ARTIFACT_DIR:-/tmp/dds-runner}"
mode="${DDS_RUN_MODE:-regression}"

validate_identifier() {
  local name="$1"
  local value="$2"
  if [[ ! "${value}" =~ ^[A-Za-z0-9._-]+$ ]]; then
    echo "${name} contains unsupported characters" >&2
    exit 2
  fi
}

validate_identifier "DDS_JOB_NAME" "${job_name}"
validate_identifier "DDS_RUN_ID" "${run_id}"

if [[ "${mode}" != "regression" ]]; then
  echo "unsupported DDS_RUN_MODE: ${mode}" >&2
  exit 2
fi

mkdir -p "${artifact_dir}"
started_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
output_file="${artifact_dir}/${run_id}.log"
result_file="${artifact_dir}/run-result.json"

echo "dds.job.started job_name=${job_name} run_id=${run_id} mode=${mode}"

set +e
bash "${repo_root}/tests/validate-regression.sh" 2>&1 | tee "${output_file}"
command_status="${PIPESTATUS[0]}"
set -e

ended_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [[ "${command_status}" == "0" ]]; then
  status="succeeded"
else
  status="failed"
fi

printf '{"job_name":"%s","run_id":"%s","mode":"%s","status":"%s","exit_code":%s,"started_at":"%s","ended_at":"%s","output_file":"%s"}\n' \
  "${job_name}" \
  "${run_id}" \
  "${mode}" \
  "${status}" \
  "${command_status}" \
  "${started_at}" \
  "${ended_at}" \
  "${run_id}.log" >"${result_file}"

echo "dds.job.finished job_name=${job_name} run_id=${run_id} status=${status} exit_code=${command_status}"
exit "${command_status}"
