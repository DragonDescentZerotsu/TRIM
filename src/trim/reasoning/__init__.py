"""Reasoning utilities for TRIM.

Keep package import side effects minimal so lightweight helpers can be used
without pulling in heavier optional dependencies from submodules.
"""

from .task_user_prompts import (
    DEFAULT_TASK_USER_PROMPT_ROOT,
    export_task_user_prompts_for_tasks,
    infer_drug_task_user_prompt_template,
    load_task_user_prompt_payload,
    render_task_user_message,
    render_task_user_messages,
)
from .agent_sft import (
    AGENT_REASONING_SFT_SCHEMA_VERSION,
    DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT,
    build_agent_reasoning_sft_datasets,
    build_agent_reasoning_sft_for_task,
    build_agent_reasoning_sft_record,
)

__all__ = [
    "AGENT_REASONING_SFT_SCHEMA_VERSION",
    "DEFAULT_AGENT_REASONING_SFT_OUTPUT_ROOT",
    "DEFAULT_TASK_USER_PROMPT_ROOT",
    "build_agent_reasoning_sft_datasets",
    "build_agent_reasoning_sft_for_task",
    "build_agent_reasoning_sft_record",
    "export_task_user_prompts_for_tasks",
    "infer_drug_task_user_prompt_template",
    "load_task_user_prompt_payload",
    "render_task_user_message",
    "render_task_user_messages",
]
