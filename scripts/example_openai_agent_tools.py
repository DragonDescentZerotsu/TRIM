#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.reasoning.agent_tools import build_openai_tool_runtime
from trim.reasoning.agent_tools.tools import SUPPORTED_NEIGHBORS_PER_LABEL


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minimal example for task-aware OpenAI agent tools."
    )
    parser.add_argument("--task", default="CYP3A4_Substrate_CarbonMangels")
    parser.add_argument(
        "--smiles",
        default="C[C@@H]1CC[C@H]2[C@@H](C)[C@@H](OC(=O)CCC(=O)O)O[C@@H]3O[C@@]4(C)CC[C@@H]1[C@@]23OO4",
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
        help="Optional tool cache root.",
    )
    parser.add_argument(
        "--neighbors-per-label",
        type=int,
        default=3,
        choices=list(SUPPORTED_NEIGHBORS_PER_LABEL),
        help="Number of positive and negative neighbors per label for compare_similar_mols.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    task = args.task
    smiles = args.smiles
    neighbors_per_label = int(args.neighbors_per_label)

    runtime_kwargs = {}
    if args.tool_cache_root:
        runtime_kwargs["tool_cache_root"] = args.tool_cache_root
    runtime = build_openai_tool_runtime(**runtime_kwargs)

    print(f"Task: {task}")
    print(f"SMILES: {smiles}")
    print(f"Neighbors per label: {neighbors_per_label}")
    print()

    if not args.skip_schema:
        print("OpenAI tool schemas:")
        print(json.dumps(runtime.tools, indent=2, ensure_ascii=False))
        print()

    print("1) Single-molecule tool")
    global_text = runtime.call_tool(
        "get_mol_properties_and_fg",
        {"smiles": smiles},
        task=task,
        # This argument is accepted for consistency but ignored by this tool.
        neighbors_per_label=neighbors_per_label,
    )
    print(global_text)
    print()

    print("2) Similar-neighbor tool")
    local_text = runtime.call_tool(
        "compare_similar_mols",
        {"smiles": smiles},
        task=task,
        neighbors_per_label=neighbors_per_label,
    )
    print(local_text)
    print()

    print("3) OpenAI function-call execution")
    mock_tool_call = {
        "type": "function_call",
        "function": {
            "name": "compare_similar_mols",
            "arguments": json.dumps({"smiles": smiles}),
        },
    }
    tool_result = runtime.call_openai_function_call(
        mock_tool_call,
        task=task,
        # The LLM only supplied smiles; the outer runtime supplies task and neighbor count.
        neighbors_per_label=neighbors_per_label,
    )
    print(tool_result)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
