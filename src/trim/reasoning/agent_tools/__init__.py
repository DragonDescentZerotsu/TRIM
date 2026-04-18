from __future__ import annotations

from importlib import import_module


__all__ = [
    "AGENT_TOOL_SCHEMA_VERSION",
    "DEFAULT_AGENT_TOOL_CACHE_ROOT",
    "DEFAULT_AGENT_TOOL_FEATURE_SET_NAME",
    "DEFAULT_AGENT_TOOL_MANIFEST_ROOT",
    "DEFAULT_AGENT_TOOL_PREWARM_SUMMARY_ROOT",
    "OpenAIAgentToolRuntime",
    "OpenAITaskAgentToolBundle",
    "OPENAI_AGENT_TOOL_SCHEMAS",
    "SUPPORTED_AGENT_TOOL_NAMES",
    "SUPPORTED_OPENAI_TOOL_NAMES",
    "TaskReasoningAgentTools",
    "build_all_task_tool_manifests",
    "build_openai_agent_tool_schemas",
    "build_openai_tool_runtime",
    "build_task_bound_openai_tool_bundle",
    "build_task_tool_manifest",
    "get_task_tool_manifest_path",
    "load_task_tool_manifest",
    "prewarm_agent_tool_cache",
    "prewarm_agent_tool_cache_for_task",
]


_MODULE_BY_EXPORT = {
    "AGENT_TOOL_SCHEMA_VERSION": ".manifests",
    "DEFAULT_AGENT_TOOL_CACHE_ROOT": ".tools",
    "DEFAULT_AGENT_TOOL_FEATURE_SET_NAME": ".manifests",
    "DEFAULT_AGENT_TOOL_MANIFEST_ROOT": ".manifests",
    "TaskReasoningAgentTools": ".tools",
    "build_all_task_tool_manifests": ".manifests",
    "build_task_tool_manifest": ".manifests",
    "get_task_tool_manifest_path": ".manifests",
    "load_task_tool_manifest": ".manifests",
    "DEFAULT_AGENT_TOOL_PREWARM_SUMMARY_ROOT": ".prewarm",
    "SUPPORTED_AGENT_TOOL_NAMES": ".prewarm",
    "prewarm_agent_tool_cache": ".prewarm",
    "prewarm_agent_tool_cache_for_task": ".prewarm",
    "OPENAI_AGENT_TOOL_SCHEMAS": ".openai_schemas",
    "build_openai_agent_tool_schemas": ".openai_schemas",
    "OpenAIAgentToolRuntime": ".openai_runtime",
    "OpenAITaskAgentToolBundle": ".openai_runtime",
    "SUPPORTED_OPENAI_TOOL_NAMES": ".openai_runtime",
    "build_openai_tool_runtime": ".openai_runtime",
    "build_task_bound_openai_tool_bundle": ".openai_runtime",
}


def __getattr__(name: str):
    try:
        module_name = _MODULE_BY_EXPORT[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
