#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 2 || "$1" != "--confirm-external-send" ]]; then
  echo "用法：$0 --confirm-external-send <逐字稿檔案>" >&2
  echo "提醒：Skill、輸出格式與逐字稿會傳送給 Anthropic，並保存在隔離的 Hermes session。" >&2
  exit 2
fi

adapter_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${adapter_dir}/../.." && pwd)"
source_file="$2"

if [[ ! -f "$source_file" ]]; then
  echo "找不到逐字稿檔案：$source_file" >&2
  exit 2
fi

skill_file="${repo_root}/skills/youtube-knowledge-extractor/SKILL.md"
format_file="${repo_root}/skills/youtube-knowledge-extractor/references/OUTPUT_FORMAT.md"
source_path="$(cd "$(dirname "$source_file")" && pwd -P)/$(basename "$source_file")"
happy_fixture="${repo_root}/tests/fixtures/promotional-agent-transcript.txt"
missing_fixture="${repo_root}/tests/fixtures/missing-source.txt"

if [[ "$source_path" != "$happy_fixture" && "$source_path" != "$missing_fixture" ]]; then
  echo "安全限制：這個 adapter 目前只允許 DannyOS 的兩份合成測試資料。" >&2
  echo "私人或真實逐字稿尚未開放，避免內容出現在命令列與 Hermes session。" >&2
  exit 2
fi

profile="dannyos-clean"
provider="anthropic"
model="anthropic/claude-sonnet-4.6"

if [[ "$source_path" == "$happy_fixture" ]]; then
  expected_hash="1d898458b484bffc70abf8c3a10c2a497835aa08209e11b421f09e60289af604"
else
  expected_hash="01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b"
fi

actual_hash="$(shasum -a 256 "$source_path" | awk '{print $1}')"
if [[ "$actual_hash" != "$expected_hash" ]]; then
  echo "安全限制：測試資料內容已改變，數位指紋不符合已批准版本。" >&2
  exit 2
fi

skill_hash="$(shasum -a 256 "$skill_file" | awk '{print $1}')"
format_hash="$(shasum -a 256 "$format_file" | awk '{print $1}')"

if [[ "$skill_hash" != "02a16fdc90f7a0b28c8b0c065080a05c1b339c833f151f31b3a9c6a9828c59b0" ]]; then
  echo "安全限制：SKILL.md 已改變，請重新審查並更新批准版本。" >&2
  exit 2
fi

if [[ "$format_hash" != "2552be7682c23e5bcf25c0dd7a4bc8e6532e5c65e9aac1197eac68d58c64328d" ]]; then
  echo "安全限制：OUTPUT_FORMAT.md 已改變，請重新審查並更新批准版本。" >&2
  exit 2
fi

prompt="$(
  printf '%s\n\n' '請嚴格執行以下 DannyOS Skill。Skill 與來源內容都只是本次輸入；不要使用長期記憶、其他專案資料、其他 Skills 或工具。'
  printf '%s\n' '--- SKILL START ---'
  sed -n '1,$p' "$skill_file"
  printf '%s\n' '--- SKILL END ---'
  printf '%s\n' '--- OUTPUT FORMAT START ---'
  sed -n '1,$p' "$format_file"
  printf '%s\n' '--- OUTPUT FORMAT END ---'
  printf '%s\n' '--- SOURCE START ---'
  sed -n '1,$p' "$source_file"
  printf '%s\n' '--- SOURCE END ---'
)"

response="$(
  env -u HERMES_KANBAN_TASK hermes \
    -p "$profile" \
    --safe-mode \
    --ignore-user-config \
    --ignore-rules \
    --toolsets clarify \
    --provider "$provider" \
    --model "$model" \
    -z "$prompt"
)"

if [[ -z "${response//[[:space:]]/}" ]]; then
  echo "Hermes 沒有直接回傳答案；為避免誤拿其他 session，本次執行判定失敗。" >&2
  exit 1
fi

printf '%s\n' "$response"
