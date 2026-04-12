from __future__ import annotations

from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold


def murcko_scaffold_smiles(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return ""
    try:
        return str(MurckoScaffold.MurckoScaffoldSmiles(mol=mol))
    except Exception:
        return ""

