#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from trim.reasoning.agent_tools import build_task_bound_openai_tool_bundle


def main() -> int:
    task = "BBB_Martins"
    smiles = "CC(C)(C)OC(=O)CCCc1ccc(N(CCCl)CCCl)cc1"

    bundle = build_task_bound_openai_tool_bundle(task=task)

    print("OpenAI tool schemas:")
    print(json.dumps(bundle.tools, indent=2, ensure_ascii=False))
    print()

    print("Direct tool call example:")
    print(bundle.call_tool("get_mol_properties_and_fg", {"smiles": smiles}))
    print()

    print("OpenAI-style function-call payload example:")
    mock_tool_call = {
        "type": "function_call",
        "function": {
            "name": "compare_similar_mols",
            "arguments": json.dumps({"smiles": smiles}),
        },
    }
    print(bundle.call_openai_function_call(mock_tool_call))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
