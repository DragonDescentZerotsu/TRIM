from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

from .openai_schemas import build_openai_agent_tool_schemas
from trim.utils.paths import (
    DEFAULT_PROCESSED_DATA_ROOT,
    DEFAULT_SIMILARITY_CACHE_ROOT,
    OUTPUTS_ROOT,
)

if TYPE_CHECKING:
    from .tools import TaskReasoningAgentTools


DEFAULT_AGENT_TOOL_FEATURE_SET_NAME = "fg_top_level+rdkit_descriptors_and_pka_easy_to_NLP_Lv1_core_pka_no_fr_counts"
DEFAULT_AGENT_TOOL_MANIFEST_ROOT = OUTPUTS_ROOT / "reasoning_agent_tools" / "manifests"


SUPPORTED_OPENAI_TOOL_NAMES = (
    "get_mol_properties_and_fg",
    "compare_similar_mols",
)


def _coerce_arguments(arguments: str | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(arguments, str):
        payload = json.loads(arguments)
    elif isinstance(arguments, Mapping):
        payload = dict(arguments)
    else:
        raise TypeError(f"Tool arguments must be a JSON string or mapping, got {type(arguments).__name__}")

    extra_keys = sorted(set(payload) - {"smiles"})
    if extra_keys:
        raise ValueError(f"Unexpected tool arguments: {extra_keys}")
    if "smiles" not in payload:
        raise ValueError("Tool arguments must include 'smiles'")
    smiles = payload["smiles"]
    if not isinstance(smiles, str) or not smiles.strip():
        raise ValueError("Tool argument 'smiles' must be a non-empty string")
    return {"smiles": smiles}


def _read_tool_call_field(tool_call: Any, field_name: str) -> Any:
    if isinstance(tool_call, Mapping):
        if field_name in tool_call:
            return tool_call[field_name]
        function_payload = tool_call.get("function")
        if isinstance(function_payload, Mapping) and field_name in function_payload:
            return function_payload[field_name]
        return None
    if hasattr(tool_call, field_name):
        return getattr(tool_call, field_name)
    function_payload = getattr(tool_call, "function", None)
    if function_payload is not None and hasattr(function_payload, field_name):
        return getattr(function_payload, field_name)
    return None


@dataclass
class OpenAITaskAgentToolBundle:
    task: str
    tool_runner: Any
    tool_schemas: list[dict[str, object]]

    @property
    def tools(self) -> list[dict[str, object]]:
        return deepcopy(self.tool_schemas)

    def call_tool(self, name: str, arguments: str | Mapping[str, Any]) -> str:
        normalized_arguments = _coerce_arguments(arguments)
        smiles = normalized_arguments["smiles"]
        if name == "get_mol_properties_and_fg":
            return self.tool_runner.get_mol_properties_and_fg(smiles)
        if name == "compare_similar_mols":
            return self.tool_runner.compare_similar_mols(smiles)
        raise ValueError(f"Unsupported tool name: {name}")

    def call_openai_function_call(self, tool_call: Any) -> str:
        name = _read_tool_call_field(tool_call, "name")
        arguments = _read_tool_call_field(tool_call, "arguments")
        if not isinstance(name, str) or not name:
            raise ValueError("Could not read tool-call name from OpenAI function call payload")
        if arguments is None:
            raise ValueError("Could not read tool-call arguments from OpenAI function call payload")
        return self.call_tool(name=name, arguments=arguments)


def build_task_bound_openai_tool_bundle(
    *,
    task: str,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    tool_cache_root: str | Path = OUTPUTS_ROOT / "reasoning_agent_tools" / "tool_cache",
    enable_tool_cache: bool = True,
) -> OpenAITaskAgentToolBundle:
    from .tools import TaskReasoningAgentTools

    return OpenAITaskAgentToolBundle(
        task=task,
        tool_runner=TaskReasoningAgentTools.from_task(
            task=task,
            feature_set_name=feature_set_name,
            manifest_root=manifest_root,
            dataset_root=dataset_root,
            cache_root=cache_root,
            tool_cache_root=tool_cache_root,
            enable_tool_cache=enable_tool_cache,
        ),
        tool_schemas=build_openai_agent_tool_schemas(task=task),
    )


__all__ = [
    "OpenAITaskAgentToolBundle",
    "SUPPORTED_OPENAI_TOOL_NAMES",
    "build_task_bound_openai_tool_bundle",
]
