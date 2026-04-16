from __future__ import annotations

from trim.reasoning.rewrite.candidates import (
    REWRITE_CANDIDATE_SCHEMA_VERSION,
    build_rewrite_candidates,
    filter_rewrite_samples,
)
from trim.reasoning.rewrite.playbooks import DEFAULT_PLAYBOOK_ROOT, load_task_playbook
from trim.reasoning.rewrite.llm import (
    DEFAULT_OPENROUTER_API_BASE,
    DEFAULT_VLLM_API_BASE,
    build_llm_request_config,
    extract_json_from_response_text,
    run_chat_completion,
)
from trim.reasoning.rewrite.pipeline import (
    DEFAULT_CANDIDATE_ROOT,
    DEFAULT_FILTERED_ROOT,
    DEFAULT_REWRITE_OUTPUT_ROOT,
    build_candidates_from_filtered_records,
    extract_reasoning_text_for_mode,
    reasoning_key_for_mode,
    run_rewrite_batch,
    run_single_rewrite,
)
from trim.reasoning.rewrite.rendering import (
    DEFAULT_REWRITE_TEMPLATE_ROOT,
    render_rewrite_prompt,
)

__all__ = [
    "DEFAULT_PLAYBOOK_ROOT",
    "DEFAULT_OPENROUTER_API_BASE",
    "DEFAULT_REWRITE_TEMPLATE_ROOT",
    "DEFAULT_VLLM_API_BASE",
    "DEFAULT_FILTERED_ROOT",
    "DEFAULT_CANDIDATE_ROOT",
    "DEFAULT_REWRITE_OUTPUT_ROOT",
    "REWRITE_CANDIDATE_SCHEMA_VERSION",
    "build_rewrite_candidates",
    "build_candidates_from_filtered_records",
    "build_llm_request_config",
    "extract_reasoning_text_for_mode",
    "extract_json_from_response_text",
    "filter_rewrite_samples",
    "load_task_playbook",
    "reasoning_key_for_mode",
    "render_rewrite_prompt",
    "run_chat_completion",
    "run_rewrite_batch",
    "run_single_rewrite",
]
