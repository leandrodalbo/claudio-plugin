"""Is Claudio on in this project, and is it off for this phase after a bug."""

from pathlib import Path

from tdcg.core.constants import ENCODING, OFF_IN_PHASE_FILE, TDCG_DIR
from tdcg.domain.phase import Phase


def is_claudio_on(project: Path) -> bool:
    """No .tdcg/ folder means Claudio is off in this project."""
    return (project / TDCG_DIR).is_dir()


def turn_off_in(project: Path, phase: Phase) -> None:
    _build_off_path(project).write_text(phase.value, encoding=ENCODING)


def is_off_in(project: Path, phase: Phase) -> bool:
    path = _build_off_path(project)
    return path.exists() and path.read_text(encoding=ENCODING).strip() == phase.value


def turn_back_on(project: Path) -> None:
    _build_off_path(project).unlink(missing_ok=True)


def _build_off_path(project: Path) -> Path:
    return project / TDCG_DIR / OFF_IN_PHASE_FILE
