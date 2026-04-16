---
name: openrouter-credits
description: Check the remaining OpenRouter credits or balance for a management key alias. Use when the user asks to query OpenRouter credits, balance, remaining money, remaining budget, or how much is left on an OpenRouter key.
---

# OpenRouter Credits

Use this skill when the user wants the balance for an OpenRouter management key.

## Workflow

1. Treat the user's "key" as an alias by default, not as a raw secret.
2. Run:

```bash
sh .agents/skills/openrouter-credits/scripts/check_openrouter_credits.sh <alias>
```

3. Report the parsed balance summary back to the user.
4. Never print the full management key back in the response.

## Alias Resolution

- `default` or `main`:
  - first tries `OPENROUTER_MANAGEMENT_KEY`
  - then tries `OPENROUTER_MANAGEMENT_KEY_DEFAULT`
- any other alias such as `prod`, `research`, or `bbb-rewrite`:
  - normalize to upper snake case
  - read `OPENROUTER_MANAGEMENT_KEY_<ALIAS>`

Examples:

- `prod` -> `OPENROUTER_MANAGEMENT_KEY_PROD`
- `bbb-rewrite` -> `OPENROUTER_MANAGEMENT_KEY_BBB_REWRITE`

If the env var is missing, explain exactly which env var name should be set.

## Notes

- Prefer alias-based lookup even if the user informally says "key".
- Only use a raw management key if the user explicitly provides one and asks to use it directly.
- If the network call fails because of sandbox restrictions, rerun with escalation.
