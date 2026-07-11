#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
hermes_output="${repo_root}/tests/expected/hermes-promotional-output.md"
missing_output="${repo_root}/tests/expected/hermes-missing-source-output.md"
codex_output="${repo_root}/examples/promotional-agent-workflow.md"

if [[ "$(rg -c '^## 【' "$hermes_output")" -ne 10 ]]; then
  echo "Hermes 快照缺少必要的十個區塊。" >&2
  exit 1
fi

if rg -q 'PersonalKM|Resolver Layer' "$hermes_output"; then
  echo "Hermes 快照混入其他專案記憶。" >&2
  exit 1
fi

rg -q '不建議建立知識卡' "$hermes_output"
rg -q '是否值得建立知識卡：否' "$hermes_output"
rg -q '沒有實際內容' "$missing_output"
rg -q '請提供' "$missing_output"

if rg -q '^## 【' "$missing_output"; then
  echo "缺少來源時不應產生十區塊報告。" >&2
  exit 1
fi

if [[ "$(rg -c '^### 【' "$codex_output")" -ne 10 ]]; then
  echo "Codex 範例缺少必要的十個區塊。" >&2
  exit 1
fi

echo "跨 Agent 回歸檢查通過。"
