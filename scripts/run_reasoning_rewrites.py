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

from trim.reasoning.rewrite.llm import build_llm_request_config
from trim.reasoning.rewrite.pipeline import (
    DEFAULT_CANDIDATE_ROOT,
    DEFAULT_FILTERED_ROOT,
    DEFAULT_REWRITE_OUTPUT_ROOT,
    resolve_task_list,
    run_rewrite_batch,
)
from trim.utils.io import save_json
from trim.utils.paths import resolve_project_path, serialize_project_path


DEFAULT_GLOBAL_ROOT = "outputs/reasoning_evidence/global/all_tasks_core_pka_no_fr_keep_nan"
DEFAULT_LOCAL_ROOT = "outputs/reasoning_evidence/local/all_tasks_core_pka_no_fr_counts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render rewrite prompts, send them to an LLM, and save parsed JSON outputs."
    )
    parser.add_argument("--provider", required=True, choices=["openrouter", "openai", "vllm"])
    parser.add_argument("--model", required=True, help="Model name exposed by the selected provider")
    parser.add_argument(
        "--mode",
        default="all",
        choices=["global", "local", "hybrid", "all"],
        help="Which rewrite stage(s) to run. 'all' runs global, local, then hybrid.",
    )
    parser.add_argument("--split", default="train")
    parser.add_argument("--task", action="append", dest="tasks", default=None)
    parser.add_argument("--filtered-root", default=str(DEFAULT_FILTERED_ROOT))
    parser.add_argument("--global-root", default=DEFAULT_GLOBAL_ROOT)
    parser.add_argument("--local-root", default=DEFAULT_LOCAL_ROOT)
    parser.add_argument("--playbook-root", default="playbooks")
    parser.add_argument(
        "--allow-missing-playbook",
        action="store_true",
        help="Allow no-playbook rewrite runs to proceed when playbooks/<task>.md is missing.",
    )
    parser.add_argument("--candidate-root", default=str(DEFAULT_CANDIDATE_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_REWRITE_OUTPUT_ROOT))
    parser.add_argument("--template-root", default="prompt_templates/reasoning_sft")
    parser.add_argument("--max-samples", type=int, default=None)
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--retry-delay-s", type=float, default=0.0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--timeout-s", type=int, default=300)
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--api-key", default=None, help="Optional explicit API key override")
    parser.add_argument("--dotenv-path", default=".env")
    parser.add_argument("--overwrite", action="store_true", help="Re-run even if output JSON already exists")
    return parser.parse_args()


def _variant_input_requested(args: argparse.Namespace) -> bool:
    return args.global_root != DEFAULT_GLOBAL_ROOT or args.local_root != DEFAULT_LOCAL_ROOT


def _guard_variant_cache_roots(args: argparse.Namespace) -> None:
    if not _variant_input_requested(args):
        return
    default_roots = {
        "--filtered-root": str(DEFAULT_FILTERED_ROOT),
        "--candidate-root": str(DEFAULT_CANDIDATE_ROOT),
        "--output-root": str(DEFAULT_REWRITE_OUTPUT_ROOT),
    }
    still_default = [
        flag
        for flag, default_value in default_roots.items()
        if str(getattr(args, flag.removeprefix("--").replace("-", "_"))) == default_value
    ]
    if still_default:
        raise ValueError(
            "Variant evidence roots were requested, but these downstream cache roots still point to legacy defaults: "
            f"{', '.join(still_default)}. Choose variant-specific roots for filters, candidates, and rewrite outputs."
        )


def main() -> int:
    args = parse_args()
    _guard_variant_cache_roots(args)
    llm_config = build_llm_request_config(
        provider=args.provider,
        model=args.model,
        api_base=args.api_base,
        api_key=args.api_key,
        temperature=args.temperature,
        max_tokens=args.max_output_tokens,
        timeout_s=args.timeout_s,
        dotenv_path=args.dotenv_path,
    )

    tasks = resolve_task_list(
        filtered_root=args.filtered_root,
        split=args.split,
        requested_tasks=args.tasks,
    )

    summaries = []
    for task in tasks:
        summary = run_rewrite_batch(
            task=task,
            split=args.split,
            mode=args.mode,
            llm_config=llm_config,
            filtered_root=args.filtered_root,
            global_root=args.global_root,
            local_root=args.local_root,
            playbook_root=args.playbook_root,
            allow_missing_playbook=args.allow_missing_playbook,
            candidate_root=args.candidate_root,
            output_root=args.output_root,
            template_root=args.template_root,
            max_samples=args.max_samples,
            max_concurrency=args.max_concurrency,
            max_retries=args.max_retries,
            retry_delay_s=args.retry_delay_s,
            skip_existing=not args.overwrite,
        )
        summaries.append(summary)

    run_summary = {
        "schema_version": "trim_reasoning_rewrite_run_summary_v1",
        "provider": llm_config.provider,
        "model": llm_config.model,
        "mode": args.mode,
        "split": args.split,
        "max_concurrency": int(args.max_concurrency),
        "max_retries": int(args.max_retries),
        "retry_delay_s": float(args.retry_delay_s),
        "tasks": tasks,
        "output_root": serialize_project_path(resolve_project_path(args.output_root)),
        "candidate_root": serialize_project_path(resolve_project_path(args.candidate_root)),
        "summaries": summaries,
    }
    summary_dir = resolve_project_path(args.output_root) / llm_config.provider
    save_json(summary_dir / "last_run_summary.json", run_summary)
    print(json.dumps(run_summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
