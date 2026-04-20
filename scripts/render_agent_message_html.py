#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "data"
    / "sft"
    / "agent_reasoning_messages"
    / "openrouter"
    / "openai__gpt-5.4-mini"
    / "train"
    / "AMES.jsonl"
)
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "visualizations"
    / "agent_reasoning_messages"
    / "AMES_trace.html"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one record from an agent reasoning messages JSONL file into a simple HTML page."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to the source JSONL file.",
    )
    parser.add_argument(
        "--sample-index",
        type=int,
        default=None,
        help="Optional sample_index to render. Defaults to the first non-empty JSONL record.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to the output HTML file.",
    )
    return parser.parse_args()


def load_record(path: Path, *, sample_index: int | None = None) -> dict[str, Any]:
    if sample_index is not None and sample_index < 0:
        raise ValueError(f"sample_index must be non-negative, got {sample_index}")

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected a JSON object on line {line_number} of {path}")
            if sample_index is not None:
                try:
                    record_sample_index = int(payload["sample_index"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Record on line {line_number} of {path} does not contain an integer sample_index"
                    ) from exc
                if record_sample_index != sample_index:
                    continue
            return payload
    if sample_index is not None:
        raise ValueError(f"No JSON object record with sample_index={sample_index} found in {path}")
    raise ValueError(f"No JSON object records found in {path}")


def escape_text(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def pretty_json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def render_block(title: str, body: str) -> str:
    return (
        '<section class="block">'
        f'<div class="block-title">{escape_text(title)}</div>'
        f'<pre>{escape_text(body)}</pre>'
        "</section>"
    )


def render_tool_calls(message: dict[str, Any]) -> str:
    tool_calls = message.get("tool_calls")
    if not isinstance(tool_calls, list) or not tool_calls:
        return ""

    parts: list[str] = ['<section class="block"><div class="block-title">Tool Calls</div>']
    for index, tool_call in enumerate(tool_calls, start=1):
        function_payload = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
        name = function_payload.get("name", "unknown")
        raw_arguments = function_payload.get("arguments", "")
        parsed_arguments: Any
        try:
            parsed_arguments = json.loads(raw_arguments) if raw_arguments else {}
        except json.JSONDecodeError:
            parsed_arguments = raw_arguments
        parts.append(
            '<div class="tool-call">'
            f'<div class="tool-call-name">Call {index}: {escape_text(name)}</div>'
            f'<pre>{escape_text(pretty_json_text(parsed_arguments))}</pre>'
            "</div>"
        )
    parts.append("</section>")
    return "".join(parts)


def render_message(message: dict[str, Any], index: int) -> str:
    role = str(message.get("role", "unknown"))
    role_class = role.lower().replace("_", "-")
    parts = [
        f'<article class="message message-{escape_text(role_class)}">',
        '<div class="message-header">',
        f'<span class="role-badge role-{escape_text(role_class)}">{escape_text(role.title())}</span>',
        f'<span class="message-index">Message {index}</span>',
        "</div>",
    ]

    if role == "tool":
        tool_name = message.get("name", "")
        tool_call_id = message.get("tool_call_id", "")
        parts.append(
            '<div class="meta-line">'
            f'Tool name: <code>{escape_text(tool_name)}</code>'
            f' | Tool call id: <code>{escape_text(tool_call_id)}</code>'
            "</div>"
        )

    thinking = message.get("thinking")
    if isinstance(thinking, str) and thinking.strip():
        parts.append(render_block("Thinking", thinking))

    content = message.get("content")
    if isinstance(content, str) and content.strip():
        parts.append(render_block("Content", content))

    tool_calls_html = render_tool_calls(message)
    if tool_calls_html:
        parts.append(tool_calls_html)

    parts.append("</article>")
    return "".join(parts)


def render_html(record: dict[str, Any], source_path: Path) -> str:
    messages = record.get("messages")
    if not isinstance(messages, list):
        raise ValueError(f"Record from {source_path} does not contain a messages list")

    task = record.get("task") or source_path.stem
    split = record.get("split") or "unknown split"
    sample_index = record.get("sample_index")
    sft_mode = record.get("sft_mode") or "full"
    title = f"{task} {sft_mode} Trace"
    meta_items = [
        ("SFT mode", sft_mode),
        ("Task", record.get("task")),
        ("Split", record.get("split")),
        ("Sample index", record.get("sample_index")),
        ("Sample id", record.get("sample_id")),
        ("Ground-truth label", record.get("gt_label")),
        ("Final answer", record.get("final_answer_option")),
        ("SMILES", record.get("smiles")),
    ]
    meta_html = "".join(
        '<div class="meta-item">'
        f'<div class="meta-label">{escape_text(label)}</div>'
        f'<div class="meta-value">{escape_text(value)}</div>'
        "</div>"
        for label, value in meta_items
    )

    source_paths = record.get("source_paths")
    source_paths_html = ""
    if isinstance(source_paths, dict) and source_paths:
        source_paths_html = (
            "<details class=\"source-paths\" open>"
            "<summary>Source Paths</summary>"
            f"<pre>{escape_text(pretty_json_text(source_paths))}</pre>"
            "</details>"
        )

    messages_html = "".join(
        render_message(message, index=index)
        for index, message in enumerate(messages, start=1)
        if isinstance(message, dict)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape_text(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f1ea;
      --panel: #fffdf8;
      --border: #d9d0c3;
      --text: #1f1a14;
      --muted: #6f6559;
      --user: #d7eadf;
      --assistant: #e8ddc8;
      --tool: #d9e6f5;
      --shadow: 0 12px 30px rgba(80, 58, 35, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(188, 166, 137, 0.24), transparent 28%),
        linear-gradient(180deg, #f8f4ee 0%, var(--bg) 100%);
      color: var(--text);
    }}

    .page {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}

    .hero {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 24px;
      box-shadow: var(--shadow);
      margin-bottom: 20px;
    }}

    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.1;
    }}

    .subtitle {{
      margin: 0;
      color: var(--muted);
      font-size: 16px;
    }}

    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}

    .meta-item {{
      background: rgba(255, 250, 242, 0.9);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 14px;
      min-width: 0;
    }}

    .meta-label {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 6px;
    }}

    .meta-value {{
      font-size: 15px;
      line-height: 1.45;
      overflow-wrap: anywhere;
    }}

    .source-paths {{
      margin-top: 16px;
      background: rgba(255, 250, 242, 0.9);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 14px;
    }}

    .timeline {{
      display: grid;
      gap: 16px;
    }}

    .message {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 18px;
      box-shadow: var(--shadow);
    }}

    .message-user {{
      border-left: 8px solid var(--user);
    }}

    .message-assistant {{
      border-left: 8px solid var(--assistant);
    }}

    .message-tool {{
      border-left: 8px solid var(--tool);
    }}

    .message-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}

    .role-badge {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}

    .role-user {{
      background: var(--user);
    }}

    .role-assistant {{
      background: var(--assistant);
    }}

    .role-tool {{
      background: var(--tool);
    }}

    .message-index {{
      color: var(--muted);
      font-size: 13px;
    }}

    .meta-line {{
      margin-bottom: 12px;
      color: var(--muted);
      font-size: 14px;
    }}

    .block {{
      margin-top: 12px;
    }}

    .block-title {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
      margin-bottom: 6px;
    }}

    .tool-call {{
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 12px;
      background: rgba(245, 242, 234, 0.7);
      margin-top: 10px;
    }}

    .tool-call-name {{
      font-weight: 700;
      margin-bottom: 6px;
    }}

    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.5;
      font-size: 14px;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    }}

    code {{
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 0.95em;
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>{escape_text(title)}</h1>
      <p class="subtitle">A single-record viewer for sample {escape_text(sample_index)} from the {escape_text(split)} split in {escape_text(source_path.as_posix())}.</p>
      <div class="meta-grid">{meta_html}</div>
      {source_paths_html}
    </section>
    <section class="timeline">
      {messages_html}
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    record = load_record(input_path, sample_index=args.sample_index)
    html_text = render_html(record, input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_text, encoding="utf-8")
    print(f"Wrote HTML viewer to {output_path}")


if __name__ == "__main__":
    main()
