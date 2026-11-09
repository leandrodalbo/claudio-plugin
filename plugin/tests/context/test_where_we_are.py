import pytest

from tdcg.context.where_we_are import build_where_we_are
from tests.support.constants import (
    ALL_PHASES,
    BROKEN_PLAN_START,
    BROKEN_PLAN_WHAT_TO_DO,
    OFF_IN_PHASE_FILE,
    PHASE_FILE,
    PLAN_FILE,
    SAMPLE_CYCLE_FILES,
    SAMPLE_CYCLE_KEY,
    SAMPLE_CYCLE_WHAT,
    UNKNOWN_PHASE_PROBLEM,
    WHERE_WE_ARE_IN_CYCLE,
    WHERE_WE_ARE_IN_PLAN,
    WHERE_WE_ARE_OFF,
    WHERE_WE_ARE_PROBLEM,
)
from tests.support.sample_configs import build_valid_config
from tests.support.sample_plans import build_plan_with_cycle_field_set_to
from tests.support.sample_projects import write_project_in
from tests.support.skill_files import build_phase_rules_path
from tests.support.tdcg_files import write_tdcg_state, write_tdcg_text


def test_no_tdcg_folder_tells_nothing(tmp_path):
    assert build_where_we_are(tmp_path) is None


def test_plan_says_which_files_may_change(tmp_path):
    write_project_in(tmp_path, "PLAN")
    assert build_where_we_are(tmp_path) == WHERE_WE_ARE_IN_PLAN.format(
        rules=build_phase_rules_path("PLAN")
    )


@pytest.mark.parametrize("phase", ALL_PHASES[1:])
def test_a_cycle_phase_names_the_cycle_its_type_files_and_rules(tmp_path, phase):
    write_project_in(tmp_path, phase)
    assert build_where_we_are(tmp_path) == WHERE_WE_ARE_IN_CYCLE.format(
        phase=phase,
        key=SAMPLE_CYCLE_KEY,
        what=SAMPLE_CYCLE_WHAT,
        type="behaviour",
        files=SAMPLE_CYCLE_FILES,
        rules=build_phase_rules_path(phase),
    )


def test_the_cycle_type_comes_from_the_plan(tmp_path):
    plan = build_plan_with_cycle_field_set_to(SAMPLE_CYCLE_KEY, "type", "refactor")
    write_tdcg_state(tmp_path, "GREEN", plan, build_valid_config())
    assert build_where_we_are(tmp_path) == WHERE_WE_ARE_IN_CYCLE.format(
        phase="GREEN",
        key=SAMPLE_CYCLE_KEY,
        what=SAMPLE_CYCLE_WHAT,
        type="refactor",
        files=SAMPLE_CYCLE_FILES,
        rules=build_phase_rules_path("GREEN"),
    )


def test_off_after_a_bug_says_the_rules_are_off(tmp_path):
    write_project_in(tmp_path, "GREEN")
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    assert build_where_we_are(tmp_path) == WHERE_WE_ARE_OFF.format(phase="GREEN")


# problems: the guards' own message, one case per file it comes from
def test_a_phase_file_problem_is_told(tmp_path):
    write_project_in(tmp_path, "GREEN")
    write_tdcg_text(tmp_path, PHASE_FILE, "BANANA")
    assert build_where_we_are(tmp_path) == WHERE_WE_ARE_PROBLEM.format(
        problem=UNKNOWN_PHASE_PROBLEM.format(word="BANANA", path=tmp_path / ".tdcg" / PHASE_FILE)
    )


def test_a_plan_problem_is_told(tmp_path):
    write_project_in(tmp_path, "GREEN")
    write_tdcg_text(tmp_path, PLAN_FILE, "not json")
    line = build_where_we_are(tmp_path)
    assert line.startswith(BROKEN_PLAN_START)
    assert BROKEN_PLAN_WHAT_TO_DO in line
