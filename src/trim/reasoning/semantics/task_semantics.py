from __future__ import annotations

import json
import re
from pathlib import Path

from trim.reasoning.task_user_prompts import DEFAULT_TASK_USER_PROMPT_ROOT
from trim.utils.paths import DATA_ROOT


LEGACY_PROMPT_ROOT = Path("/data1/tianang/Projects/Intern-S1/DataPrepare/TDC_valid_prompts_label_scaffold")
DEFAULT_PROMPT_ROOTS = [
    DEFAULT_TASK_USER_PROMPT_ROOT,
    DATA_ROOT / "prompts" / "TDC_valid_prompts_label_scaffold",
    LEGACY_PROMPT_ROOT,
]

OPTION_PATTERN = re.compile(
    r"\(A\)\s*(.*?)\s*\(B\)\s*(.*?)(?:\nDrug SMILES:|\nPlease think|$)",
    re.DOTALL,
)


def load_task_label_semantics(
    task: str,
    prompt_root: str | Path | None = None,
) -> dict[int, dict[str, str]] | None:
    if prompt_root is not None:
        candidate_roots = [Path(prompt_root)]
    else:
        candidate_roots = list(DEFAULT_PROMPT_ROOTS)

    for root in candidate_roots:
        json_path = Path(root) / f"{task}.json"
        if json_path.exists():
            with json_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            messages = payload.get("messages")
            if not isinstance(messages, list) or not messages:
                return None
            prompt_text = str(messages[0].get("content", ""))
            match = OPTION_PATTERN.search(prompt_text)
            if match is None:
                return None
            option_a_text = " ".join(match.group(1).split())
            option_b_text = " ".join(match.group(2).split())
            return {
                0: {
                    "option": "A",
                    "text": option_a_text,
                },
                1: {
                    "option": "B",
                    "text": option_b_text,
                },
            }

        jsonl_path = Path(root) / f"{task}.jsonl"
        if not jsonl_path.exists():
            continue

        with jsonl_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                prompt_text = str(record.get("text", ""))
                match = OPTION_PATTERN.search(prompt_text)
                if match is None:
                    return None
                option_a_text = " ".join(match.group(1).split())
                option_b_text = " ".join(match.group(2).split())
                return {
                    0: {
                        "option": "A",
                        "text": option_a_text,
                    },
                    1: {
                        "option": "B",
                        "text": option_b_text,
                    },
                }
    return None
