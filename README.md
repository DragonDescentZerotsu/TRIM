# TRIM

TRIM is the new standalone project for scaffold-split TDC molecular classification. The current phase focuses on a pure-ML system with:

- a migrated global single-molecule EBM
- cached descriptor / FG / similarity assets owned through TRIM-local paths
- retrieval and pairwise-local infrastructure for the next phase of positive-neighbor / negative-neighbor EBMs

The main entrypoints are:

- `scripts/prepare_legacy_assets.py`
- `scripts/train_global_ebm.py`
- `scripts/evaluate_global_ebm.py`
- `scripts/train_pair_pos.py`
- `scripts/train_pair_neg.py`
- `scripts/run_local_only.py`
- `scripts/run_hybrid.py`

Project-local outputs are written under `outputs/`.

## Agent Tools

TRIM also exposes two task-bound text-returning tools for the reasoning / agent phase:

- `get_mol_properties_and_fg(smiles)`
- `compare_similar_mols(smiles)`

The recommended entrypoint is `build_task_bound_openai_tool_bundle(...)`, which keeps the OpenAI tool schemas and the runtime implementation aligned.

### Local Python Usage

```python
from trim.reasoning.agent_tools import build_task_bound_openai_tool_bundle

bundle = build_task_bound_openai_tool_bundle(task="BBB_Martins")

global_text = bundle.call_tool(
    "get_mol_properties_and_fg",
    {"smiles": "O=C(c1ccccc1)c1ccc2n1CCC2C(=O)O"},
)

local_text = bundle.call_tool(
    "compare_similar_mols",
    {"smiles": "O=C(c1ccccc1)c1ccc2n1CCC2C(=O)O"},
)

print(global_text)
print()
print(local_text)
```

### OpenAI Function Calling Usage

```python
import json

from trim.reasoning.agent_tools import build_task_bound_openai_tool_bundle

bundle = build_task_bound_openai_tool_bundle(task="BBB_Martins")
tools = bundle.tools

tool_call = {
    "type": "function_call",
    "function": {
        "name": "compare_similar_mols",
        "arguments": json.dumps({"smiles": "O=C(c1ccccc1)c1ccc2n1CCC2C(=O)O"}),
    },
}

tool_result_text = bundle.call_openai_function_call(tool_call)
print(tool_result_text)
```

### Smoke Test

Run the bundled example script:

```bash
/data1/tianang/anaconda3/envs/vllm/bin/python scripts/example_openai_agent_tools.py \
  --task BBB_Martins \
  --smiles 'O=C(c1ccccc1)c1ccc2n1CCC2C(=O)O' \
  --skip-schema
```

This script now also prints a small cache timing demo for both tools.

## Tool Cache

Tool payloads are cached under:

- `outputs/reasoning_agent_tools/tool_cache/<feature_set_name>/<task>/<cache_namespace>/<tool_name>/<sha1(smiles)>.json`

Notes:

- `compare_similar_mols` cache is task-scoped, not shared across tasks.
- The cache is keyed by task plus SMILES, not by an explicit train/valid/test directory.
- The saved payload still contains the original `smiles` field inside the JSON, even though the filename is hashed.

To prewarm the cache for all tasks and all unique SMILES across `train/valid/test`:

```bash
/data1/tianang/anaconda3/envs/vllm/bin/python scripts/prewarm_agent_tool_cache.py \
  --max-concurrency 16
```

The prewarm summary is written to:

- `outputs/reasoning_agent_tools/tool_cache_prewarm/<feature_set_name>/manifest.json`

If another project wants the simplest possible integration path, the easiest option is to keep TRIM as a dependency or submodule and call `build_task_bound_openai_tool_bundle(...)` directly, instead of copying `tools.py` in isolation. The runtime depends on TRIM task manifests, processed splits, similarity caches, and saved model bundles.
