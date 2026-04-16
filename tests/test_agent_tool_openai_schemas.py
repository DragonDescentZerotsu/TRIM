from __future__ import annotations

from trim.reasoning.agent_tools import OPENAI_AGENT_TOOL_SCHEMAS, build_openai_agent_tool_schemas


def test_default_openai_agent_tool_schemas_have_expected_shape():
    assert len(OPENAI_AGENT_TOOL_SCHEMAS) == 2

    names = [tool["name"] for tool in OPENAI_AGENT_TOOL_SCHEMAS]
    assert names == ["get_mol_properties_and_fg", "compare_similar_mols"]

    for tool in OPENAI_AGENT_TOOL_SCHEMAS:
        assert tool["type"] == "function"
        assert tool["strict"] is True
        assert tool["parameters"]["type"] == "object"
        assert tool["parameters"]["required"] == ["smiles"]
        assert tool["parameters"]["additionalProperties"] is False
        assert tool["parameters"]["properties"]["smiles"]["type"] == "string"


def test_task_specific_openai_agent_tool_schema_mentions_task_name():
    tools = build_openai_agent_tool_schemas(task="BBB_Martins")
    compare_tool = next(tool for tool in tools if tool["name"] == "compare_similar_mols")
    assert "BBB_Martins" in compare_tool["description"]
