from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
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


def _coerce_task(task: object) -> str:
    task_name = str(task).strip()
    if not task_name:
        raise ValueError("Task must be a non-empty string")
    return task_name


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


def _call_tool_runner(
    tool_runner: Any,
    *,
    name: str,
    smiles: str,
    neighbors_per_label: int = 3,
) -> str:
    if name == "get_mol_properties_and_fg":
        return tool_runner.get_mol_properties_and_fg(smiles)
    if name == "compare_similar_mols":
        return tool_runner.compare_similar_mols(smiles, neighbors_per_label=neighbors_per_label)
    raise ValueError(f"Unsupported tool name: {name}")


def _build_task_tool_runner(
    *,
    task: str,
    feature_set_name: str,
    manifest_root: str | Path,
    dataset_root: str | Path,
    cache_root: str | Path,
    tool_cache_root: str | Path,
    enable_tool_cache: bool,
) -> Any:
    from .tools import TaskReasoningAgentTools

    return TaskReasoningAgentTools.from_task(
        task=task,
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
        tool_cache_root=tool_cache_root,
        enable_tool_cache=enable_tool_cache,
    )


@dataclass
class OpenAIAgentToolRuntime:
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT
    tool_cache_root: str | Path = OUTPUTS_ROOT / "reasoning_agent_tools" / "tool_cache"
    enable_tool_cache: bool = True
    tool_schemas: list[dict[str, object]] | None = None

    def __post_init__(self) -> None:
        self._tool_runner_cache: dict[str, Any] = {}
        self._tool_runner_lock = Lock()
        if self.tool_schemas is None:
            self.tool_schemas = build_openai_agent_tool_schemas()

    @property
    def tools(self) -> list[dict[str, object]]:
        return deepcopy(self.tool_schemas)

    def get_runner(self, task: str) -> Any:
        task_name = _coerce_task(task)
        cached_runner = self._tool_runner_cache.get(task_name)
        if cached_runner is not None:
            return cached_runner

        with self._tool_runner_lock:
            cached_runner = self._tool_runner_cache.get(task_name)
            if cached_runner is not None:
                return cached_runner

            tool_runner = _build_task_tool_runner(
                task=task_name,
                feature_set_name=self.feature_set_name,
                manifest_root=self.manifest_root,
                dataset_root=self.dataset_root,
                cache_root=self.cache_root,
                tool_cache_root=self.tool_cache_root,
                enable_tool_cache=self.enable_tool_cache,
            )
            self._tool_runner_cache[task_name] = tool_runner
            return tool_runner

    def call_tool(
        self,
        name: str,
        arguments: str | Mapping[str, Any],
        *,
        task: str,
        neighbors_per_label: int = 3,
    ) -> str:
        normalized_arguments = _coerce_arguments(arguments)
        smiles = normalized_arguments["smiles"]
        tool_runner = self.get_runner(task)
        return _call_tool_runner(
            tool_runner,
            name=name,
            smiles=smiles,
            neighbors_per_label=neighbors_per_label,
        )

    def call_openai_function_call(
        self,
        tool_call: Any,
        *,
        task: str,
        neighbors_per_label: int = 3,
    ) -> str:
        name = _read_tool_call_field(tool_call, "name")
        arguments = _read_tool_call_field(tool_call, "arguments")
        if not isinstance(name, str) or not name:
            raise ValueError("Could not read tool-call name from OpenAI function call payload")
        if arguments is None:
            raise ValueError("Could not read tool-call arguments from OpenAI function call payload")
        return self.call_tool(
            name=name,
            arguments=arguments,
            task=task,
            neighbors_per_label=neighbors_per_label,
        )


@dataclass
class OpenAITaskAgentToolBundle:
    task: str
    tool_runner: Any
    tool_schemas: list[dict[str, object]]

    @property
    def tools(self) -> list[dict[str, object]]:
        return deepcopy(self.tool_schemas)

    def call_tool(
        self,
        name: str,
        arguments: str | Mapping[str, Any],
        *,
        neighbors_per_label: int = 3,
    ) -> str:
        normalized_arguments = _coerce_arguments(arguments)
        smiles = normalized_arguments["smiles"]
        return _call_tool_runner(
            self.tool_runner,
            name=name,
            smiles=smiles,
            neighbors_per_label=neighbors_per_label,
        )

    def call_openai_function_call(
        self,
        tool_call: Any,
        *,
        neighbors_per_label: int = 3,
    ) -> str:
        name = _read_tool_call_field(tool_call, "name")
        arguments = _read_tool_call_field(tool_call, "arguments")
        if not isinstance(name, str) or not name:
            raise ValueError("Could not read tool-call name from OpenAI function call payload")
        if arguments is None:
            raise ValueError("Could not read tool-call arguments from OpenAI function call payload")
        return self.call_tool(name=name, arguments=arguments, neighbors_per_label=neighbors_per_label)


def build_openai_tool_runtime(
    *,
    feature_set_name: str = DEFAULT_AGENT_TOOL_FEATURE_SET_NAME,
    manifest_root: str | Path = DEFAULT_AGENT_TOOL_MANIFEST_ROOT,
    dataset_root: str | Path = DEFAULT_PROCESSED_DATA_ROOT,
    cache_root: str | Path = DEFAULT_SIMILARITY_CACHE_ROOT,
    tool_cache_root: str | Path = OUTPUTS_ROOT / "reasoning_agent_tools" / "tool_cache",
    enable_tool_cache: bool = True,
) -> OpenAIAgentToolRuntime:
    return OpenAIAgentToolRuntime(
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
        tool_cache_root=tool_cache_root,
        enable_tool_cache=enable_tool_cache,
        tool_schemas=build_openai_agent_tool_schemas(),
    )


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
    task_name = _coerce_task(task)
    runtime = build_openai_tool_runtime(
        feature_set_name=feature_set_name,
        manifest_root=manifest_root,
        dataset_root=dataset_root,
        cache_root=cache_root,
        tool_cache_root=tool_cache_root,
        enable_tool_cache=enable_tool_cache,
    )

    return OpenAITaskAgentToolBundle(
        task=task_name,
        tool_runner=runtime.get_runner(task_name),
        tool_schemas=build_openai_agent_tool_schemas(task=task_name),
    )


__all__ = [
    "OpenAIAgentToolRuntime",
    "OpenAITaskAgentToolBundle",
    "SUPPORTED_OPENAI_TOOL_NAMES",
    "build_openai_tool_runtime",
    "build_task_bound_openai_tool_bundle",
]
