#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.reasoning.agent_tools import build_openai_tool_runtime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Example usage for task-aware OpenAI agent tools, including cache timing."
    )
    parser.add_argument("--task", default="BBB_Martins")
    parser.add_argument(
        "--smiles",
        default="CC(C)(C)OC(=O)CCCc1ccc(N(CCCl)CCCl)cc1",
        help="SMILES to query with both tools.",
    )
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip printing the full OpenAI tool schemas.",
    )
    parser.add_argument(
        "--tool-cache-root",
        default=None,
        help="Optional tool cache root. Use a fresh tmp directory if you want a clean cold-vs-hot cache timing run.",
    )
    return parser.parse_args()


def _time_tool_call(runtime, *, task: str, tool_name: str, smiles: str) -> tuple[str, float]:
    started_at = time.perf_counter()
    result = runtime.call_tool(tool_name, {"smiles": smiles}, task=task)
    elapsed_s = time.perf_counter() - started_at
    return result, elapsed_s


def _print_cache_speed_demo(runtime, *, task: str, smiles: str) -> None:
    print("Cache timing demo:")
    tool_runner = runtime.get_runner(task)
    for tool_name in ("get_mol_properties_and_fg", "compare_similar_mols"):
        had_cache_before = tool_runner.has_cached_tool_payload(tool_name=tool_name, smiles=smiles)
        _, first_elapsed_s = _time_tool_call(runtime, task=task, tool_name=tool_name, smiles=smiles)
        has_cache_after_first = tool_runner.has_cached_tool_payload(tool_name=tool_name, smiles=smiles)
        _, second_elapsed_s = _time_tool_call(runtime, task=task, tool_name=tool_name, smiles=smiles)

        print(f"- {tool_name}")
        print(f"  cache existed before first call: {had_cache_before}")
        print(f"  cache exists after first call: {has_cache_after_first}")
        print(f"  first call elapsed: {first_elapsed_s:.3f}s")
        print(f"  second call elapsed: {second_elapsed_s:.3f}s")

    print()


def main() -> int:
    args = parse_args()
    task = args.task
    smiles = args.smiles

    runtime_kwargs = {}
    if args.tool_cache_root:
        runtime_kwargs["tool_cache_root"] = args.tool_cache_root
    runtime = build_openai_tool_runtime(**runtime_kwargs)

    print(f"Task: {task}")
    print(f"SMILES: {smiles}")
    print()

    if not args.skip_schema:
        print("OpenAI tool schemas:")
        print(json.dumps(runtime.tools, indent=2, ensure_ascii=False))
        print()

    print("Direct tool call example:")
    print(runtime.call_tool("get_mol_properties_and_fg", {"smiles": smiles}, task=task))
    print()

    print("OpenAI-style function-call payload example:")
    mock_tool_call = {
        "type": "function_call",
        "function": {
            "name": "compare_similar_mols",
            "arguments": json.dumps({"smiles": smiles}),
        },
    }
    print(runtime.call_openai_function_call(mock_tool_call, task=task))
    print()

    _print_cache_speed_demo(runtime, task=task, smiles=smiles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
