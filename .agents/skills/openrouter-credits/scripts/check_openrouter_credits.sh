#!/usr/bin/env sh
set -eu

API_URL="https://openrouter.ai/api/v1/credits"
alias_name="${1:-default}"

normalize_alias() {
  printf '%s' "$1" | tr '[:lower:]- ' '[:upper:]__' | tr -cd 'A-Z0-9_'
}

resolve_env_var() {
  case "$1" in
    default|main)
      if [ -n "${OPENROUTER_MANAGEMENT_KEY:-}" ]; then
        printf '%s\n' "OPENROUTER_MANAGEMENT_KEY"
        return 0
      fi
      if [ -n "${OPENROUTER_MANAGEMENT_KEY_DEFAULT:-}" ]; then
        printf '%s\n' "OPENROUTER_MANAGEMENT_KEY_DEFAULT"
        return 0
      fi
      printf '%s\n' "OPENROUTER_MANAGEMENT_KEY"
      return 1
      ;;
    OPENROUTER_MANAGEMENT_KEY|OPENROUTER_MANAGEMENT_KEY_*)
      printf '%s\n' "$1"
      return 0
      ;;
    *)
      normalized="$(normalize_alias "$1")"
      printf 'OPENROUTER_MANAGEMENT_KEY_%s\n' "$normalized"
      return 0
      ;;
  esac
}

env_var_name="$(resolve_env_var "$alias_name" || true)"

case "$env_var_name" in
  OPENROUTER_MANAGEMENT_KEY|OPENROUTER_MANAGEMENT_KEY_*)
    ;;
  *)
    echo "Could not determine an environment variable for alias '$alias_name'." >&2
    exit 1
    ;;
esac

eval "management_key=\${$env_var_name:-}"

if [ -z "${management_key:-}" ] && [ -f ".env" ]; then
  management_key="$(
    python3 - "$env_var_name" ".env" <<'PY'
import re
import sys

target_key = sys.argv[1]
env_path = sys.argv[2]
pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")

with open(env_path, "r", encoding="utf-8") as handle:
    for raw_line in handle:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        key, value = match.groups()
        if key != target_key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        print(value)
        raise SystemExit(0)
PY
  )"
fi

if [ -z "${management_key:-}" ]; then
  echo "Missing OpenRouter management key for alias '$alias_name'." >&2
  echo "Expected environment variable: $env_var_name" >&2
  exit 1
fi

response="$(
  curl -fsS "$API_URL" \
    -H "Authorization: Bearer $management_key"
)"

printf '%s' "$response" | python3 - "$alias_name" <<'PY'
import json
import sys

alias = sys.argv[1]

try:
    payload = json.load(sys.stdin)
except json.JSONDecodeError as exc:
    print(f"alias: {alias}")
    print(f"parse_error: {exc}")
    raise SystemExit(1)

data = payload.get("data", payload)
if not isinstance(data, dict):
    print(f"alias: {alias}")
    print("raw_response:")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    raise SystemExit(0)

def pick_number(container, keys):
    for key in keys:
        value = container.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None

total_credits = pick_number(
    data,
    [
        "total_credits",
        "credits",
        "credit_limit",
        "limit",
    ],
)
total_usage = pick_number(
    data,
    [
        "total_usage",
        "usage",
        "used_credits",
        "spent",
    ],
)
remaining_credits = pick_number(
    data,
    [
        "remaining_credits",
        "remaining",
        "balance",
        "remaining_balance",
    ],
)

if remaining_credits is None and total_credits is not None and total_usage is not None:
    remaining_credits = total_credits - total_usage

print(f"alias: {alias}")
if total_credits is not None:
    print(f"total_credits: {total_credits:.6f}")
if total_usage is not None:
    print(f"total_usage: {total_usage:.6f}")
if remaining_credits is not None:
    print(f"remaining_credits: {remaining_credits:.6f}")

if total_credits is None and total_usage is None and remaining_credits is None:
    print("raw_response:")
    print(json.dumps(payload, indent=2, ensure_ascii=True))
PY
