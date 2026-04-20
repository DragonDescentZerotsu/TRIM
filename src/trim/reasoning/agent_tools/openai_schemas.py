from __future__ import annotations

from copy import deepcopy


def _smiles_only_parameters() -> dict[str, object]:
    return {
        "type": "object",
        "properties": {
            "smiles": {
                "type": "string",
                "description": "SMILES string for the molecule to analyze.",
            }
        },
        "required": ["smiles"],
        "additionalProperties": False,
    }


def _compare_tool_description(task: str | None) -> str:
    task_scope = f" for task {task}" if task else " for the current task"
    return (
        "Retrieve text-form local analog evidence"
        f"{task_scope}. The input SMILES must belong to that task dataset so the tool can identify "
        "the query split and retrieve the nearest training-set neighbors. The tool returns plain text "
        "with a short definition of query/neighbor/delta, then positive and negative neighbors "
        "(the executing runtime chooses how many per label, defaulting to 3), each with "
        "neighbor/query/delta values for the 36 dense properties plus functional-group differences."
    )


def build_openai_agent_tool_schemas(*, task: str | None = None) -> list[dict[str, object]]:
    shared_parameters = _smiles_only_parameters()
    schemas = [
        {
            "type": "function",
            "name": "get_mol_properties_and_fg",
            "description": (
                "Return plain-text single-molecule property evidence. The tool outputs one line per "
                "dense property in 'display_name: value' form for the 36 default dense properties, "
                "followed by the molecule's present functional groups and their counts. When the "
                "strongest acidic pKa or strongest basic pKa is undefined, the text explicitly says "
                "'not applicable (no acidic/basic site)'."
            ),
            "parameters": deepcopy(shared_parameters),
            "strict": True,
        },
        {
            "type": "function",
            "name": "compare_similar_mols",
            "description": _compare_tool_description(task),
            "parameters": deepcopy(shared_parameters),
            "strict": True,
        },
    ]
    return schemas


OPENAI_AGENT_TOOL_SCHEMAS = build_openai_agent_tool_schemas()


__all__ = [
    "OPENAI_AGENT_TOOL_SCHEMAS",
    "build_openai_agent_tool_schemas",
]
