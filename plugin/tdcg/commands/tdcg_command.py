"""What each /claudio command does."""

import shutil
from datetime import date
from pathlib import Path

from tdcg.checks.test_check import ensure_tests_as_expected
# The module itself, not its names: `match` reads a dotted name as a value to compare with.
from tdcg.core import constants, messages
from tdcg.core.errors import AlreadySetUpError, NotSetUpError, UnknownInstructionError
from tdcg.core.plugin_folder import SCHEMA_FOLDER
from tdcg.domain.cycle import Cycle
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.phase import Phase
from tdcg.state.claudio_switch import is_claudio_on
from tdcg.state.config_check import ensure_config_valid
from tdcg.state.phase_file import (
    move_back_to,
    move_to_next_phase,
    read_phase,
    restart_at_plan,
    skip_to,
)
from tdcg.state.plan_check import ensure_plan_valid
from tdcg.state.plan_file import (
    add_cycle_note,
    complete_plan,
    find_next_cycle,
    finish_cycle,
    is_plan_done,
)


def run_tdcg_command(project: Path, words: list[str]) -> str:
    """Called by the command hook with the instruction and the words typed after it. Gives back
    the answer for the user, or raises a TdcgError that says what is wrong."""
    if words == [constants.INIT_WORD]:
        return _set_up(project)
    if not is_claudio_on(project):
        raise NotSetUpError()
    return _run_instruction(project, words)


def _run_instruction(project: Path, words: list[str]) -> str:
    match words:
        case [constants.STATUS_WORD]:
            return _say_where_we_are(project)
        case [constants.NEXT_WORD]:
            return _move_to_next(project)
        case [constants.NEXT_WORD, constants.SKIP_TO_OPTION, word] if _is_phase(word):
            return _skip_ahead(project, Phase(word))
        case [constants.BACK_WORD, word] if _is_phase(word):
            return _move_back(project, Phase(word))
    raise UnknownInstructionError(constants.WORD_SEPARATOR.join(words))


def _is_phase(word: str) -> bool:
    return word in Phase.__members__


def _set_up(project: Path) -> str:
    if is_claudio_on(project):
        raise AlreadySetUpError()
    restart_at_plan(project)
    schema_copy = project / constants.TDCG_DIR / constants.PLAN_SCHEMA_FILE
    shutil.copy(SCHEMA_FOLDER / constants.PLAN_SCHEMA_FILE, schema_copy)
    return messages.SET_UP_ANSWER


def _say_where_we_are(project: Path) -> str:
    return messages.WHERE_WE_ARE_AND_INSTRUCTIONS.format(where=_build_answer(project))


def _move_to_next(project: Path) -> str:
    """Every cycle done means the plan is finished, in any phase: also how a plan that couldn't be
    filed under done/ is tried again."""
    _ensure_plan_and_config_valid(project)
    if is_plan_done(project):
        return _finish_plan(project)
    cycle = find_next_cycle(project)
    phase = read_phase(project)
    ensure_tests_as_expected(project, phase, cycle.type)
    if phase is Phase.COMMIT:
        return _leave_commit(project, cycle)
    move_to_next_phase(project, cycle.type)
    return _build_answer(project)


def _leave_commit(project: Path, cycle: Cycle) -> str:
    finish_cycle(project, cycle.key)
    if is_plan_done(project):
        return _finish_plan(project)
    move_to_next_phase(project, cycle.type)
    return _build_answer(project)


def _finish_plan(project: Path) -> str:
    complete_plan(project)
    restart_at_plan(project)
    return messages.PLAN_FINISHED_ANSWER


def _skip_ahead(project: Path, target: Phase) -> str:
    _ensure_plan_and_config_valid(project)
    cycle = find_next_cycle(project)
    ensure_tests_as_expected(project, read_phase(project), cycle.type)
    today = date.today().isoformat()
    for skipped in skip_to(project, target, cycle.type):
        note = messages.SKIP_NOTE.format(phase=skipped.value, date=today)
        add_cycle_note(project, cycle.key, note)
    return _build_answer(project)


def _move_back(project: Path, target: Phase) -> str:
    if target is Phase.PLAN:
        return _move_back_to_plan(project)
    _ensure_plan_and_config_valid(project)
    move_back_to(project, target, find_next_cycle(project).type)
    return _build_answer(project)


def _move_back_to_plan(project: Path) -> str:
    """The way out of a broken plan, so the plan is neither checked nor read. A behaviour cycle
    has the full route: every phase is on it."""
    move_back_to(project, Phase.PLAN, CycleType.BEHAVIOUR)
    return messages.PLAN_ANSWER


def _ensure_plan_and_config_valid(project: Path) -> None:
    """The hooks only do a quick read and trust this check, made on every phase move."""
    ensure_plan_valid(project)
    ensure_config_valid(project)


def _build_answer(project: Path) -> str:
    """Where we are now. PLAN has no cycle, and may have no plan yet."""
    phase = read_phase(project)
    if phase is Phase.PLAN:
        return messages.PLAN_ANSWER
    cycle = find_next_cycle(project)
    return messages.CYCLE_ANSWER.format(phase=phase.value, key=cycle.key, type=cycle.type.value)
