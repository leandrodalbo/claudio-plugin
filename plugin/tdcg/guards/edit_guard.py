from fnmatch import fnmatchcase
from pathlib import Path

from tdcg.core.constants import CONFIG_FILE, PLAN_FILE, TDCG_DIR
from tdcg.core.errors import (
    FileNotInCycleError,
    LockedTestFileError,
    NotATestFileError,
    OutsideProjectError,
    PhaseBlocksEditError,
    TdcgFolderLockedError,
)
from tdcg.domain.phase import Phase
from tdcg.state.config_file import read_config, read_free_files
from tdcg.state.phase_file import read_phase
from tdcg.core.plugin_folder import SKILL_FOLDER
from tdcg.state.plan_file import find_next_cycle

_TEST_PHASES = {Phase.RED}
_SOURCE_PHASES = {Phase.GREEN, Phase.REFACTOR}
_EDIT_PHASES = _TEST_PHASES | _SOURCE_PHASES
_FILES_CLAUDE_MAY_EDIT_IN_PLAN = {Path(TDCG_DIR) / PLAN_FILE, Path(TDCG_DIR) / CONFIG_FILE}


def ensure_edit_allowed(project: Path, file: Path) -> None:
    """Returns when Claude may change file; raises an error saying why not otherwise.
    The claudio skill is the user's own copy of the knowledge: it may change in any phase, even
    though it sits outside the project. The rest of the plugin stays locked. The user's free list
    comes after .tdcg/, so no pattern can unlock what Claudio runs on, and before the phase and
    the cycle, which it beats."""
    if _is_in_skill_folder(project, file):
        return
    relative = _find_path_in_project(project, file)
    phase = read_phase(project)
    if relative.is_relative_to(TDCG_DIR):
        _ensure_tdcg_edit_allowed(relative, phase)
        return
    if _matches_any(relative, read_free_files(project)):
        return
    _ensure_cycle_edit_allowed(project, relative, phase)


def _is_in_skill_folder(project: Path, file: Path) -> bool:
    """Resolved first, so `..` can't climb out of the skill into the plugin's Python."""
    return (project / file).resolve().is_relative_to(SKILL_FOLDER.resolve())


def _find_path_in_project(project: Path, file: Path) -> Path:
    """The file's path from the project folder. A relative file counts from the project."""
    root = project.resolve()
    absolute = (project / file).resolve()
    if not absolute.is_relative_to(root):
        raise OutsideProjectError(file)
    return absolute.relative_to(root)


def _ensure_tdcg_edit_allowed(relative: Path, phase: Phase) -> None:
    if phase is not Phase.PLAN or relative not in _FILES_CLAUDE_MAY_EDIT_IN_PLAN:
        raise TdcgFolderLockedError(relative)


def _ensure_cycle_edit_allowed(project: Path, relative: Path, phase: Phase) -> None:
    if phase not in _EDIT_PHASES:
        raise PhaseBlocksEditError(phase.value, relative)
    cycle = find_next_cycle(project)
    is_test = _matches_any(relative, read_config(project).test_files)
    if phase in _TEST_PHASES and not is_test:
        raise NotATestFileError(relative)
    if phase in _SOURCE_PHASES and is_test:
        raise LockedTestFileError(relative, phase.value)
    if not _matches_any(relative, cycle.files):
        raise FileNotInCycleError(relative, cycle.key)


def _matches_any(relative: Path, patterns: list[str]) -> bool:
    return any(fnmatchcase(relative.as_posix(), pattern) for pattern in patterns)
