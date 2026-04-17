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

## vLLM Load Balancing with HAProxy

If a single local `vllm serve` instance is too slow for reasoning rewrites, a practical setup is:

- host multiple identical vLLM servers on different ports
- put HAProxy in front of them
- point TRIM to one HAProxy endpoint via `--api-base`

The resulting flow looks like:

```text
scripts/run_reasoning_rewrites.py
  -> http://127.0.0.1:9000/v1
    -> HAProxy
      -> http://127.0.0.1:8001/v1
      -> http://127.0.0.1:8002/v1
      -> http://127.0.0.1:8003/v1
      -> http://127.0.0.1:8004/v1
```

### 1. Start Multiple vLLM Backends

Use the same model and the same served model name on every backend. For example:

```bash
vllm serve /path/to/model --port 8001 --served-model-name gpt-oss-120b
vllm serve /path/to/model --port 8002 --served-model-name gpt-oss-120b
vllm serve /path/to/model --port 8003 --served-model-name gpt-oss-120b
vllm serve /path/to/model --port 8004 --served-model-name gpt-oss-120b
```

Before adding HAProxy, verify that each backend responds:

```bash
curl -sS http://127.0.0.1:8001/v1/models
curl -sS http://127.0.0.1:8002/v1/models
curl -sS http://127.0.0.1:8003/v1/models
curl -sS http://127.0.0.1:8004/v1/models
```

### 2. Create an HAProxy Config

Save a config such as `/tmp/haproxy-vllm.cfg`:

```cfg
global
    log stdout format raw local0 info
    maxconn 4096

defaults
    mode http
    log global
    option httplog
    option dontlognull
    timeout connect 5s
    timeout client 600s
    timeout server 600s
    timeout http-request 30s
    retries 2
    option redispatch

frontend vllm_front
    bind 127.0.0.1:9000
    default_backend vllm_back

backend vllm_back
    balance leastconn
    option httpchk GET /v1/models
    http-check expect status 200

    http-response set-header X-Served-By %[srv_name]

    server g1 127.0.0.1:8001 check inter 5s fall 2 rise 1
    server g2 127.0.0.1:8002 check inter 5s fall 2 rise 1
    server g3 127.0.0.1:8003 check inter 5s fall 2 rise 1
    server g4 127.0.0.1:8004 check inter 5s fall 2 rise 1
```

Notes:

- `balance leastconn` is a good default for rewrite workloads with uneven sample runtimes.
- `GET /v1/models` is used as a health check.
- `X-Served-By` makes it easy to confirm which backend handled a response.
- Keep HAProxy timeouts at least as large as the TRIM rewrite timeout, and usually a bit larger.

### 3. Validate and Start HAProxy

Check the config:

```bash
haproxy -f /tmp/haproxy-vllm.cfg -c
```

Run in the foreground first while debugging:

```bash
haproxy -f /tmp/haproxy-vllm.cfg -db
```

Then verify the proxy endpoint:

```bash
curl -i http://127.0.0.1:9000/v1/models
```

If you repeat that request several times, the `X-Served-By` response header should rotate across `g1`, `g2`, `g3`, and `g4`.

### 4. Point TRIM to HAProxy

Once the proxy is up, pass the HAProxy endpoint to the rewrite script:

```bash
/data1/tianang/anaconda3/envs/vllm/bin/python scripts/run_reasoning_rewrites.py \
  --provider vllm \
  --model gpt-oss-120b \
  --api-base http://127.0.0.1:9000/v1 \
  --mode all \
  --split train \
  --task AMES \
  --max-concurrency 4 \
  --timeout-s 600
```

TRIM still sees only one OpenAI-compatible endpoint. HAProxy handles distribution across the backend vLLM instances.

### 5. Recommended Rollout Strategy

For a new deployment, the safest order is:

1. Start two vLLM backends, not four.
2. Verify each backend directly with `curl .../v1/models`.
3. Start HAProxy and verify `http://127.0.0.1:9000/v1/models`.
4. Run a small TRIM smoke test such as `--max-samples 5`.
5. Increase `--max-concurrency` gradually.
6. Add more backend ports only after the smaller setup is stable.

### 6. Practical Caveats

- All backends should expose the same `--served-model-name`, because TRIM sends one `model` string in the request payload.
- HAProxy does not rewrite the JSON body, so mixing different served model names behind one proxy is not recommended.
- Existing `result.json` files are reused unless `--overwrite` is passed.
- If many samples fail with `timed out`, first lower `--max-concurrency` and increase `--timeout-s` before increasing retries.
