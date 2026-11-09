from pathlib import Path

from tdcg.core.constants import PHASE_FILE, TDCG_DIR
from tdcg.core.errors import (
    NotEarlierPhaseError,
    NotLaterPhaseError,
    PhaseNotSkippableError,
    UnknownPhaseError,
)
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.phase import Phase
from tdcg.state.claudio_switch import turn_back_on


def read_phase(project: Path) -> Phase:
    path = _build_phase_path(project)
    if not path.exists():
        return Phase.PLAN

    word = path.read_text().strip()
    try:
        return Phase(word)
    except ValueError:
        raise UnknownPhaseError(word, path) from None


def move_to_next_phase(project: Path, cycle_type: CycleType) -> Phase:
    phase = _find_phase_after(read_phase(project), cycle_type)
    _write_phase(project, phase)
    return phase


def move_back_to(project: Path, target: Phase, cycle_type: CycleType) -> Phase:
    current = read_phase(project)
    if _find_step(target, cycle_type) >= _find_step(current, cycle_type):
        raise NotEarlierPhaseError(current.value, target.value)

    _write_phase(project, target)
    return target


def skip_to(project: Path, target: Phase, cycle_type: CycleType) -> list[Phase]:
    """The user leaving the route (/claudio:next --skipTo). Gives back the phases jumped over, so
    the command can note them in the cycle."""
    current = read_phase(project)
    skipped = _find_phases_between(current, target, cycle_type)
    for phase in skipped:
        _ensure_skippable(phase, cycle_type)

    _write_phase(project, target)
    return skipped


def restart_at_plan(project: Path) -> None:
    """A new project or a finished plan: PLAN from anywhere, even from PLAN itself, which
    move_back_to refuses."""
    _write_phase(project, Phase.PLAN)


def _find_phase_after(phase: Phase, cycle_type: CycleType) -> Phase:
    """COMMIT is on every route, so only the other phases need the route check (_find_step)."""
    if phase is Phase.COMMIT:
        return Phase.SPECIFY
    next_step = _find_step(phase, cycle_type) + 1
    return cycle_type.steps[next_step]


def _find_phases_between(current: Phase, target: Phase, cycle_type: CycleType) -> list[Phase]:
    current_step = _find_step(current, cycle_type)
    target_step = _find_step(target, cycle_type)
    if target_step <= current_step:
        raise NotLaterPhaseError(current.value, target.value)
    return cycle_type.steps[current_step + 1 : target_step]


def _find_step(phase: Phase, cycle_type: CycleType) -> int:
    cycle_type.ensure_has_step(phase)
    return cycle_type.steps.index(phase)


def _ensure_skippable(phase: Phase, cycle_type: CycleType) -> None:
    if not phase.is_skippable:
        raise PhaseNotSkippableError(phase.value, cycle_type.value)


def _write_phase(project: Path, phase: Phase) -> None:
    """A new phase also ends "Claudio off after a bug", which only lasts one phase."""
    path = _build_phase_path(project)
    path.parent.mkdir(exist_ok=True)
    path.write_text(phase.value)
    turn_back_on(project)


def _build_phase_path(project: Path) -> Path:
    return project / TDCG_DIR / PHASE_FILE
