from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
DEFAULT_VLLM_API_BASE = "http://127.0.0.1:8000/v1"
DEFAULT_DOTENV_PATH = Path(__file__).resolve().parents[4] / ".env"


@dataclass(frozen=True)
class LLMRequestConfig:
    provider: str
    model: str
    api_base: str
    api_key: str | None
    temperature: float
    max_tokens: int | None
    timeout_s: int


def _parse_dotenv(dotenv_path: str | Path | None = None) -> dict[str, str]:
    path = DEFAULT_DOTENV_PATH if dotenv_path is None else Path(dotenv_path)
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("export "):
            value = value[len("export ") :].strip()
        if (
            len(value) >= 2
            and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'"))
        ):
            value = value[1:-1]
        values[key] = value
    return values


def _read_env_with_dotenv(name: str, *, dotenv_path: str | Path | None = None) -> str | None:
    value = os.environ.get(name)
    if value:
        return value
    return _parse_dotenv(dotenv_path).get(name)


def _read_dotenv_with_env_fallback(name: str, *, dotenv_path: str | Path | None = None) -> str | None:
    value = _parse_dotenv(dotenv_path).get(name)
    if value:
        return value
    return os.environ.get(name)


def _default_api_base(provider: str) -> str:
    if provider == "openrouter":
        return DEFAULT_OPENROUTER_API_BASE
    if provider == "vllm":
        return DEFAULT_VLLM_API_BASE
    raise ValueError(f"Unsupported LLM provider: {provider}")


def _default_api_key(provider: str, *, dotenv_path: str | Path | None = None) -> str | None:
    if provider == "openrouter":
        return _read_dotenv_with_env_fallback("OPENROUTER_API_KEY", dotenv_path=dotenv_path)
    if provider == "vllm":
        return _read_env_with_dotenv("VLLM_API_KEY", dotenv_path=dotenv_path) or _read_env_with_dotenv(
            "OPENAI_API_KEY", dotenv_path=dotenv_path
        )
    raise ValueError(f"Unsupported LLM provider: {provider}")


def build_llm_request_config(
    *,
    provider: str,
    model: str,
    api_base: str | None = None,
    api_key: str | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    timeout_s: int = 300,
    dotenv_path: str | Path | None = None,
) -> LLMRequestConfig:
    resolved_provider = str(provider).strip().lower()
    resolved_api_base = (api_base or _default_api_base(resolved_provider)).rstrip("/")
    resolved_api_key = api_key if api_key is not None else _default_api_key(
        resolved_provider,
        dotenv_path=dotenv_path,
    )
    if resolved_provider == "openrouter" and not resolved_api_key:
        raise ValueError("OPENROUTER_API_KEY is required for provider=openrouter")
    return LLMRequestConfig(
        provider=resolved_provider,
        model=str(model),
        api_base=resolved_api_base,
        api_key=resolved_api_key,
        temperature=float(temperature),
        max_tokens=None if max_tokens is None else int(max_tokens),
        timeout_s=int(timeout_s),
    )


def _completion_headers(config: LLMRequestConfig) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    if config.provider == "openrouter":
        headers["HTTP-Referer"] = "https://github.com/openai/codex"
        headers["X-Title"] = "TRIM reasoning rewrite"
    return headers


def _extract_content_from_choice(choice: dict[str, Any]) -> str:
    message = choice.get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
                continue
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text" and isinstance(item.get("text"), str):
                chunks.append(item["text"])
        return "".join(chunks)
    return str(content)


def _post_json(*, url: str, headers: dict[str, str], payload: dict[str, Any], timeout_s: int) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url=url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=timeout_s) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM request failed with HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"LLM request failed: {exc}") from exc
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Expected JSON object response from completion API")
    return parsed


def run_chat_completion(*, prompt: str, config: LLMRequestConfig) -> dict[str, Any]:
    url = f"{config.api_base}/chat/completions"
    payload: dict[str, Any] = {
        "model": config.model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": config.temperature,
    }
    if config.max_tokens is not None:
        payload["max_tokens"] = config.max_tokens
    raw_response = _post_json(
        url=url,
        headers=_completion_headers(config),
        payload=payload,
        timeout_s=config.timeout_s,
    )
    choices = raw_response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("Completion response does not contain choices")
    content = _extract_content_from_choice(choices[0])
    return {
        "provider": config.provider,
        "model": config.model,
        "api_base": config.api_base,
        "request_payload": payload,
        "raw_response": raw_response,
        "content": content,
    }


def extract_json_from_response_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    fenced_blocks = []
    if "```" in stripped:
        parts = stripped.split("```")
        for block in parts[1::2]:
            fenced_blocks.append(block)
        for block in fenced_blocks:
            candidate = block
            newline_index = candidate.find("\n")
            if newline_index != -1:
                first_line = candidate[:newline_index].strip().lower()
                if first_line in {"json", "javascript"}:
                    candidate = candidate[newline_index + 1 :]
            candidate = candidate.strip()
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                try:
                    parsed = json.loads(_escape_control_chars_inside_strings(candidate))
                except json.JSONDecodeError:
                    continue
            if isinstance(parsed, dict):
                return parsed

    start = stripped.find("{")
    if start == -1:
        raise ValueError("No JSON object found in model response")
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(stripped)):
        char = stripped[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = stripped[start : index + 1]
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError:
                    parsed = json.loads(_escape_control_chars_inside_strings(candidate))
                if not isinstance(parsed, dict):
                    raise ValueError("Model response JSON must decode to an object")
                return parsed
    raise ValueError("Could not recover a complete JSON object from model response")


def _escape_control_chars_inside_strings(text: str) -> str:
    chars: list[str] = []
    in_string = False
    escape = False
    for char in text:
        if in_string:
            if escape:
                chars.append(char)
                escape = False
                continue
            if char == "\\":
                chars.append(char)
                escape = True
                continue
            if char == '"':
                chars.append(char)
                in_string = False
                continue
            if char == "\n":
                chars.append("\\n")
                continue
            if char == "\r":
                chars.append("\\r")
                continue
            if char == "\t":
                chars.append("\\t")
                continue
            chars.append(char)
            continue
        chars.append(char)
        if char == '"':
            in_string = True
            escape = False
    return "".join(chars)
