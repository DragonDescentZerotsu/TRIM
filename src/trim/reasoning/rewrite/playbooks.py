from __future__ import annotations

from pathlib import Path

from trim.utils.paths import PROJECT_ROOT, resolve_project_path


DEFAULT_PLAYBOOK_ROOT = PROJECT_ROOT / "playbooks"


def resolve_playbook_root(playbook_root: str | Path | None = None) -> Path:
    if playbook_root is None:
        return DEFAULT_PLAYBOOK_ROOT.resolve()
    return resolve_project_path(playbook_root)


def load_task_playbook(
    task: str,
    *,
    playbook_root: str | Path | None = None,
) -> tuple[str, Path]:
    root = resolve_playbook_root(playbook_root)
    playbook_path = root / f"{task}.md"
    if not playbook_path.exists():
        raise FileNotFoundError(f"Playbook not found for task {task}: {playbook_path}")
    return playbook_path.read_text(encoding="utf-8").strip(), playbook_path.resolve()
