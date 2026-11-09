"""Quick read of the plan for the hooks: plain json, no schema. The full check is plan_check.py."""

import json
from dataclasses import replace
from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import (
    CYCLES,
    DONE,
    DONE_DIR,
    ENCODING,
    FILE_NAME_DASH,
    FILES,
    GOAL,
    JSON_EXTENSION,
    JSON_INDENT,
    KEY,
    NEW_LINE,
    NOTES,
    PLAN_FILE,
    STATUS,
    TDCG_DIR,
    TITLE,
    TITLE_SPACE,
)
from tdcg.core.errors import (
    BrokenPlanError,
    CycleAlreadyDoneError,
    CycleNotFoundError,
    DonePlanExistsError,
    NoCycleLeftError,
    NoPlanError,
)
from tdcg.domain.cycle import Cycle
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.plan import Plan
from tdcg.domain.plan_status import PlanStatus
from tdcg.state.json.field_types import describe_wrong_type, is_list_of_text
from tdcg.state.json.json_file import load_json_object


def read_plan(project: Path) -> Plan | None:
    path = build_plan_path(project)
    if not path.exists():
        return None
    return _build_plan(_load_plan_data(path), path)


def find_next_cycle(project: Path) -> Cycle:
    """The cycle being worked on: the first one not done. None left is an error: the helper that
    owns the rule throws for it, so callers don't test for None."""
    path = build_plan_path(project)
    plan = _build_plan(_load_required_plan_data(path), path)
    for cycle in plan.cycles:
        if not cycle.done:
            return cycle
    raise NoCycleLeftError()


def is_plan_done(project: Path) -> bool:
    """Raises when there is no plan, or a broken one: "done" can't be answered without it."""
    path = build_plan_path(project)
    plan = _build_plan(_load_required_plan_data(path), path)
    return all(cycle.done for cycle in plan.cycles)


def finish_cycle(project: Path, key: str) -> None:
    path = build_plan_path(project)
    data = _load_required_plan_data(path)
    cycle = _find_cycle(data, key, path)
    if cycle[DONE]:
        raise CycleAlreadyDoneError(key)

    cycle[DONE] = True
    _write(path, data)


def add_cycle_note(project: Path, key: str, note: str) -> None:
    path = build_plan_path(project)
    data = _load_required_plan_data(path)
    _find_cycle(data, key, path)[NOTES].append(note)
    _write(path, data)


def complete_plan(project: Path) -> None:
    path = build_plan_path(project)
    data = _load_required_plan_data(path)
    done_path = _build_done_path(project, data[TITLE])
    if done_path.exists():
        raise DonePlanExistsError(done_path)

    done_path.parent.mkdir(exist_ok=True)
    _mark_completed(data)
    _write(done_path, data)
    path.unlink()


def build_plan_path(project: Path) -> Path:
    return project / TDCG_DIR / PLAN_FILE


def _load_required_plan_data(path: Path) -> dict:
    if not path.exists():
        raise NoPlanError(path)
    return _load_plan_data(path)


def _load_plan_data(path: Path) -> dict:
    """Builds the plan once, so a broken one fails before anything reads or writes it."""
    data = load_json_object(path, BrokenPlanError)
    _build_plan(data, path)
    return data


def _build_plan(data: dict, path: Path) -> Plan:
    plan = _build_plan_from_fields(data, path)
    for cycle in plan.cycles:
        _ensure_guard_fields_typed(cycle, path)
    return plan


def _build_plan_from_fields(data: dict, path: Path) -> Plan:
    """Python's own checks name what's wrong: a missing field (KeyError), a missing or unknown
    cycle field (TypeError from the dataclass), an unknown status (ValueError from the enum)."""
    try:
        cycles = [_build_cycle(fields) for fields in data[CYCLES]]
        return Plan(data[TITLE], PlanStatus(data[STATUS]), data[GOAL], cycles)
    except KeyError as error:
        raise BrokenPlanError([messages.MISSING_FIELD.format(field=error)], path) from error
    except (TypeError, ValueError) as error:
        raise BrokenPlanError([str(error)], path) from error


def _build_cycle(fields: dict) -> Cycle:
    """The plan holds the type as a word; the enum turns it into the type (or a ValueError)."""
    cycle = Cycle(**fields)
    return replace(cycle, type=CycleType(cycle.type))


def _ensure_guard_fields_typed(cycle: Cycle, path: Path) -> None:
    """Text in place of a list would be read letter by letter, and "*" matches every file."""
    if not is_list_of_text(cycle.files):
        problem = describe_wrong_type(FILES, messages.LIST_OF_TEXT, cycle.files)
        raise BrokenPlanError([messages.CYCLE_PROBLEM.format(key=cycle.key, problem=problem)], path)
    if not isinstance(cycle.done, bool):
        problem = describe_wrong_type(DONE, messages.TRUE_OR_FALSE, cycle.done)
        raise BrokenPlanError([messages.CYCLE_PROBLEM.format(key=cycle.key, problem=problem)], path)


def _find_cycle(data: dict, key: str, path: Path) -> dict:
    cycle = next((cycle for cycle in data[CYCLES] if cycle[KEY] == key), None)
    if cycle is None:
        raise CycleNotFoundError(key, path)
    return cycle


def _mark_completed(data: dict) -> None:
    for cycle in data[CYCLES]:
        cycle[DONE] = True
    data[STATUS] = PlanStatus.DONE.value


def _write(path: Path, data: dict) -> None:
    text = json.dumps(data, indent=JSON_INDENT, ensure_ascii=False)
    path.write_text(text + NEW_LINE, encoding=ENCODING)


def _build_done_path(project: Path, title: str) -> Path:
    name = title.lower().replace(TITLE_SPACE, FILE_NAME_DASH)
    return project / TDCG_DIR / DONE_DIR / f"{name}{JSON_EXTENSION}"
