from __future__ import annotations

import sys
from types import SimpleNamespace

from trim.reasoning.agent_tools.openai_runtime import (
    OpenAITaskAgentToolBundle,
    build_task_bound_openai_tool_bundle,
)


class _FakeRunner:
    def get_mol_properties_and_fg(self, smiles: str) -> str:
        return f"global::{smiles}"

    def compare_similar_mols(self, smiles: str) -> str:
        return f"local::{smiles}"


def test_openai_tool_bundle_dispatches_tool_calls():
    bundle = OpenAITaskAgentToolBundle(
        task="BBB_Martins",
        tool_runner=_FakeRunner(),
        tool_schemas=[{"name": "get_mol_properties_and_fg"}, {"name": "compare_similar_mols"}],
    )

    assert bundle.call_tool("get_mol_properties_and_fg", {"smiles": "CCO"}) == "global::CCO"
    assert bundle.call_tool("compare_similar_mols", '{"smiles":"CCN"}') == "local::CCN"


def test_openai_tool_bundle_accepts_openai_style_function_payload():
    bundle = OpenAITaskAgentToolBundle(
        task="BBB_Martins",
        tool_runner=_FakeRunner(),
        tool_schemas=[{"name": "get_mol_properties_and_fg"}, {"name": "compare_similar_mols"}],
    )

    tool_call = {
        "type": "function_call",
        "function": {
            "name": "compare_similar_mols",
            "arguments": '{"smiles":"CCCl"}',
        },
    }
    assert bundle.call_openai_function_call(tool_call) == "local::CCCl"

    object_style_tool_call = SimpleNamespace(
        name="get_mol_properties_and_fg",
        arguments='{"smiles":"CCC"}',
    )
    assert bundle.call_openai_function_call(object_style_tool_call) == "global::CCC"


def test_build_task_bound_openai_tool_bundle_uses_task_bound_schema_and_runner(monkeypatch):
    class _FakeToolsClass:
        @classmethod
        def from_task(cls, **kwargs):
            return _FakeRunner()

    monkeypatch.setitem(
        sys.modules,
        "trim.reasoning.agent_tools.tools",
        SimpleNamespace(TaskReasoningAgentTools=_FakeToolsClass),
    )

    bundle = build_task_bound_openai_tool_bundle(task="BBB_Martins")
    assert bundle.task == "BBB_Martins"
    assert [tool["name"] for tool in bundle.tools] == [
        "get_mol_properties_and_fg",
        "compare_similar_mols",
    ]
    assert "BBB_Martins" in bundle.tools[1]["description"]
