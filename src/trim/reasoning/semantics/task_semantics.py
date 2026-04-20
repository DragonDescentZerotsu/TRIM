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

BRIEF_TASK_SEMANTICS_BY_TASK = {
    "AMES": "mutagenicity (not mutagenic or mutagenic)",
    "BBB_Martins": "BBB crossing status (does not cross the BBB or crosses the BBB)",
    "Bioavailability_Ma": "oral bioavailability (<20% or >=20%)",
    "CYP2C9_Substrate_CarbonMangels": "CYP2C9 substrate status (not a substrate or substrate)",
    "CYP2D6_Substrate_CarbonMangels": "CYP2D6 substrate status (not a substrate or substrate)",
    "CYP3A4_Substrate_CarbonMangels": "CYP3A4 substrate status (not a substrate or substrate)",
    "Carcinogens_Lagunin": "carcinogenicity (not a carcinogen or carcinogen)",
    "ClinTox": "clinical toxicity (not toxic or toxic)",
    "DILI": "drug-induced liver injury risk (cannot cause DILI or can cause DILI)",
    "HIA_Hou": "human intestinal absorption (cannot be absorbed or can be absorbed)",
    "PAMPA_NCATS": "PAMPA membrane permeability (not permeable or permeable in a PAMPA assay)",
    "Pgp_Broccatelli": "P-glycoprotein inhibition status (not a Pgp inhibitor or Pgp inhibitor)",
    "SARSCoV2_3CLPro_Diamond": (
        "SARS-CoV-2 3CL protease binding (does not bind or binds SARS-CoV-2 3CL protease)"
    ),
    "SARSCoV2_Vitro_Touret": (
        "SARS-CoV-2 replication inhibition (does not inhibit or inhibits SARS-CoV-2 replication)"
    ),
    "Skin_Reaction": "skin reaction risk (does not cause a skin reaction or causes a skin reaction)",
    "hERG": "hERG blocking liability (does not block hERG or blocks hERG)",
}


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


def load_brief_task_semantics(
    task: str,
    prompt_root: str | Path | None = None,
) -> str:
    brief = BRIEF_TASK_SEMANTICS_BY_TASK.get(task)
    if brief:
        return brief

    semantics = load_task_label_semantics(task, prompt_root=prompt_root)
    if semantics is not None:
        label_zero = str(semantics.get(0, {}).get("text", "")).strip()
        label_one = str(semantics.get(1, {}).get("text", "")).strip()
        if label_zero and label_one:
            return f"whether it {label_zero} or {label_one}"

    return task.replace("_", " ")
