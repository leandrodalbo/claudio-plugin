from collections.abc import Iterator
from pathlib import Path

from tdcg.core.constants import TDCG_DIR
from tdcg.core.errors import ShellChangesBlockedError, TdcgError, TdcgFolderRemovedError
from tdcg.domain.file_stamp import Snapshot
from tdcg.guards.edit_guard import ensure_edit_allowed

# Not in a snapshot at all; different from None, which means listed as gone.
_NOT_LISTED = object()


def find_changed_files(before: Snapshot, after: Snapshot) -> list[Path]:
    """Files listed in only one snapshot, or with a different stamp. Sorted."""
    changed = []
    for path in sorted(before.keys() | after.keys()):
        if _is_changed(path, before, after):
            changed.append(path)
    return changed


def ensure_changed_files_allowed(project: Path, changed: list[Path]) -> None:
    """The edit rules (3.2) for each changed file. Raises one error with every reason, each said
    once (e.g. "every cycle is done" for many files)."""
    reasons = list(dict.fromkeys(_find_refusal_reasons(project, changed)))
    if reasons:
        raise ShellChangesBlockedError(reasons)


def ensure_tdcg_folder_kept(project: Path) -> None:
    """For a project where Claudio was on before the command."""
    if not (project / TDCG_DIR).is_dir():
        raise TdcgFolderRemovedError()


def _is_changed(path: Path, before: Snapshot, after: Snapshot) -> bool:
    return before.get(path, _NOT_LISTED) != after.get(path, _NOT_LISTED)


def _find_refusal_reasons(project: Path, changed: list[Path]) -> Iterator[str]:
    for file in changed:
        try:
            ensure_edit_allowed(project, file)
        except TdcgError as error:
            yield str(error)
