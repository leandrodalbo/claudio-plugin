from datetime import date

import pytest

from tdcg.commands.tdcg_command import run_tdcg_command
from tdcg.core.errors import (
    AlreadySetUpError,
    DonePlanExistsError,
    InvalidConfigError,
    InvalidPlanError,
    NoConfigError,
    NoPlanError,
    NotEarlierPhaseError,
    NotLaterPhaseError,
    NotSetUpError,
    PhaseNotInRouteError,
    PhaseNotSkippableError,
    TestsShouldHaveFailedError,
    TestsShouldHavePassedError,
    UnknownInstructionError,
)
from tests.support.constants import (
    ALREADY_SET_UP,
    CANT_SKIP_RED,
    CONFIG_FILE,
    CYCLE_ANSWER,
    DONE_PLAN_FILE,
    INSTRUCTIONS_THAT_NEED_A_PROJECT,
    MOVES_THAT_NEED_PASSING_TESTS,
    MOVES_THAT_RUN_NO_TESTS,
    NOT_EARLIER_SPECIFY_TO_GREEN,
    NOT_LATER_GREEN_TO_RED,
    NOT_SET_UP,
    PHASE_FILE,
    PHASE_NOT_IN_ROUTE_BY_TYPE,
    PHASES_WITH_PASSING_TESTS,
    PLAN_ANSWER,
    PLAN_FILE,
    PLAN_FINISHED_ANSWER,
    PLAN_SCHEMA_FILE,
    SAMPLE_CYCLE_KEY,
    SET_UP_ANSWER,
    SKIP_NOTE,
    TDCG_DIR,
    TDCG_INSTRUCTIONS,
    TESTS_SHOULD_HAVE_FAILED,
    TESTS_SHOULD_HAVE_PASSED_BY_PHASE,
    UNKNOWN_INSTRUCTION,
    WRONG_INSTRUCTIONS,
)
from tests.support.plugin_files import load_plan_schema_source
from tests.support.sample_commands import FAILING, LEAVES_A_MARKER, MARKER, PASSING
from tests.support.sample_configs import build_config_with_test_command, build_config_without_field
from tests.support.sample_plans import (
    build_plan_with_all_cycles_done,
    build_plan_with_cycle_field_set_to,
    build_plan_with_one_cycle_left,
    build_plan_without_field,
    build_valid_plan,
)
from tests.support.sample_projects import write_project_in
from tests.support.tdcg_files import (
    has_tdcg_path,
    load_tdcg_json,
    load_tdcg_text,
    write_tdcg_json,
    write_tdcg_state,
    write_tdcg_text,
)


# init
def test_init_starts_at_plan(tmp_path):
    assert run_tdcg_command(tmp_path, ["init"]) == SET_UP_ANSWER
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"


def test_init_copies_the_plan_schema(tmp_path):
    run_tdcg_command(tmp_path, ["init"])
    assert load_tdcg_text(tmp_path, PLAN_SCHEMA_FILE) == load_plan_schema_source()


def test_init_writes_no_plan(tmp_path):
    run_tdcg_command(tmp_path, ["init"])
    assert not has_tdcg_path(tmp_path, PLAN_FILE)


def test_init_writes_no_config(tmp_path):
    """Claude helps write it in PLAN; /claudio:next from PLAN says it's missing."""
    run_tdcg_command(tmp_path, ["init"])
    assert not has_tdcg_path(tmp_path, CONFIG_FILE)


def test_init_when_already_set_up_changes_nothing(tmp_path):
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(AlreadySetUpError) as error:
        run_tdcg_command(tmp_path, ["init"])
    assert str(error.value) == ALREADY_SET_UP
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "GREEN"
    assert not has_tdcg_path(tmp_path, PLAN_SCHEMA_FILE)


# not set up
@pytest.mark.parametrize("words", INSTRUCTIONS_THAT_NEED_A_PROJECT)
def test_without_tdcg_folder_only_init_works(tmp_path, words):
    with pytest.raises(NotSetUpError) as error:
        run_tdcg_command(tmp_path, words)
    assert str(error.value) == NOT_SET_UP
    assert not (tmp_path / TDCG_DIR).exists()


# words that mean nothing
@pytest.mark.parametrize("words", WRONG_INSTRUCTIONS)
def test_a_wrong_instruction_shows_the_list_and_changes_nothing(tmp_path, words):
    write_project_in(tmp_path, "SPECIFY")
    with pytest.raises(UnknownInstructionError) as error:
        run_tdcg_command(tmp_path, words)
    assert str(error.value) == UNKNOWN_INSTRUCTION.format(words=" ".join(words))
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


# status
def test_status_in_a_cycle_says_where_we_are_and_lists_the_instructions(tmp_path):
    write_project_in(tmp_path, "GREEN")
    where = CYCLE_ANSWER.format(phase="GREEN", key=SAMPLE_CYCLE_KEY, type="behaviour")
    assert run_tdcg_command(tmp_path, ["status"]) == f"{where}\n{TDCG_INSTRUCTIONS}"


def test_status_in_plan_needs_no_plan_yet(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "PLAN")
    assert run_tdcg_command(tmp_path, ["status"]) == f"{PLAN_ANSWER}\n{TDCG_INSTRUCTIONS}"


def test_status_changes_nothing(tmp_path):
    write_project_in(tmp_path, "GREEN")
    run_tdcg_command(tmp_path, ["status"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "GREEN"


# next: the checks come first
def test_next_without_a_plan_is_an_error(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "PLAN")
    with pytest.raises(NoPlanError):
        run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"


def test_next_without_a_config_is_an_error(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "PLAN")
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    with pytest.raises(NoConfigError):
        run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"


def test_next_with_a_bad_plan_runs_no_tests_and_stays(tmp_path):
    plan = build_plan_without_field("goal")
    write_tdcg_state(tmp_path, "RED", plan, build_config_with_test_command(LEAVES_A_MARKER))
    with pytest.raises(InvalidPlanError):
        run_tdcg_command(tmp_path, ["next"])
    assert not (tmp_path / MARKER).exists()
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "RED"


def test_next_with_a_bad_config_stays(tmp_path):
    write_tdcg_state(
        tmp_path, "SPECIFY", build_valid_plan(), build_config_without_field("test_files")
    )
    with pytest.raises(InvalidConfigError):
        run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


# next: moving along the route
@pytest.mark.parametrize(("left", "reached"), MOVES_THAT_RUN_NO_TESTS)
def test_next_moves_on_without_running_the_tests(tmp_path, left, reached):
    write_tdcg_state(
        tmp_path, left, build_valid_plan(), build_config_with_test_command(LEAVES_A_MARKER)
    )
    answer = run_tdcg_command(tmp_path, ["next"])
    assert answer == CYCLE_ANSWER.format(phase=reached, key=SAMPLE_CYCLE_KEY, type="behaviour")
    assert load_tdcg_text(tmp_path, PHASE_FILE) == reached
    assert not (tmp_path / MARKER).exists()


def test_next_leaves_red_when_the_tests_fail(tmp_path):
    write_tdcg_state(tmp_path, "RED", build_valid_plan(), build_config_with_test_command(FAILING))
    run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PROMPT"


def test_next_stays_in_red_when_the_tests_pass(tmp_path):
    write_tdcg_state(tmp_path, "RED", build_valid_plan(), build_config_with_test_command(PASSING))
    with pytest.raises(TestsShouldHaveFailedError) as error:
        run_tdcg_command(tmp_path, ["next"])
    assert str(error.value) == TESTS_SHOULD_HAVE_FAILED
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "RED"


@pytest.mark.parametrize(("left", "reached"), MOVES_THAT_NEED_PASSING_TESTS)
def test_next_moves_on_when_the_tests_pass(tmp_path, left, reached):
    write_tdcg_state(tmp_path, left, build_valid_plan(), build_config_with_test_command(PASSING))
    run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == reached


@pytest.mark.parametrize("phase", PHASES_WITH_PASSING_TESTS)
def test_next_stays_when_the_tests_fail(tmp_path, phase):
    write_tdcg_state(tmp_path, phase, build_valid_plan(), build_config_with_test_command(FAILING))
    with pytest.raises(TestsShouldHavePassedError) as error:
        run_tdcg_command(tmp_path, ["next"])
    assert str(error.value) == TESTS_SHOULD_HAVE_PASSED_BY_PHASE[phase]
    assert load_tdcg_text(tmp_path, PHASE_FILE) == phase


# next: the cycle's type sets the route and the test result
def test_next_follows_the_route_of_the_cycle_type(tmp_path):
    plan = build_plan_with_cycle_field_set_to(SAMPLE_CYCLE_KEY, "type", "refactor")
    write_tdcg_state(tmp_path, "SPECIFY", plan, build_config_with_test_command(PASSING))
    answer = run_tdcg_command(tmp_path, ["next"])
    assert answer == CYCLE_ANSWER.format(phase="PROMPT", key=SAMPLE_CYCLE_KEY, type="refactor")


def test_next_gives_the_type_to_the_test_check(tmp_path):
    """Coverage tests are for work that already exists: they must pass in RED."""
    plan = build_plan_with_cycle_field_set_to(SAMPLE_CYCLE_KEY, "type", "coverage")
    write_tdcg_state(tmp_path, "RED", plan, build_config_with_test_command(PASSING))
    run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PROMPT"


# next: leaving COMMIT
def test_next_from_commit_goes_to_the_next_cycle(tmp_path):
    write_project_in(tmp_path, "COMMIT")
    assert run_tdcg_command(tmp_path, ["next"]) == CYCLE_ANSWER.format(
        phase="SPECIFY", key="2b", type="behaviour"
    )
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


def test_next_from_commit_marks_the_cycle_done(tmp_path):
    write_project_in(tmp_path, "COMMIT")
    run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_json(tmp_path, PLAN_FILE)["cycles"][1]["done"] is True


def test_next_from_the_last_commit_finishes_the_plan(tmp_path):
    plan = build_plan_with_one_cycle_left()
    write_tdcg_state(tmp_path, "COMMIT", plan, build_config_with_test_command(PASSING))
    assert run_tdcg_command(tmp_path, ["next"]) == PLAN_FINISHED_ANSWER
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"
    assert not has_tdcg_path(tmp_path, PLAN_FILE)
    assert load_tdcg_json(tmp_path, DONE_PLAN_FILE)["status"] == "done"


def test_next_with_every_cycle_done_finishes_the_plan(tmp_path):
    """What the "no cycle left" message tells the user to do."""
    write_tdcg_state(
        tmp_path, "PLAN", build_plan_with_all_cycles_done(), build_config_with_test_command(PASSING)
    )
    assert run_tdcg_command(tmp_path, ["next"]) == PLAN_FINISHED_ANSWER
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"
    assert not has_tdcg_path(tmp_path, PLAN_FILE)


def test_next_can_finish_the_plan_after_a_name_clash_is_cleared(tmp_path):
    plan = build_plan_with_one_cycle_left()
    write_tdcg_state(tmp_path, "COMMIT", plan, build_config_with_test_command(PASSING))
    write_tdcg_text(tmp_path, DONE_PLAN_FILE, "old plan")
    with pytest.raises(DonePlanExistsError):
        run_tdcg_command(tmp_path, ["next"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "COMMIT"

    (tmp_path / TDCG_DIR / DONE_PLAN_FILE).unlink()
    assert run_tdcg_command(tmp_path, ["next"]) == PLAN_FINISHED_ANSWER


# next --skipTo
def test_skip_moves_and_answers(tmp_path):
    write_tdcg_state(tmp_path, "GREEN", build_valid_plan(), build_config_with_test_command(PASSING))
    answer = run_tdcg_command(tmp_path, ["next", "--skipTo", "COMMIT"])
    assert answer == CYCLE_ANSWER.format(phase="COMMIT", key=SAMPLE_CYCLE_KEY, type="behaviour")
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "COMMIT"


def test_skip_notes_each_skipped_phase_in_the_cycle(tmp_path):
    write_tdcg_state(tmp_path, "GREEN", build_valid_plan(), build_config_with_test_command(PASSING))
    run_tdcg_command(tmp_path, ["next", "--skipTo", "COMMIT"])
    today = date.today().isoformat()
    assert load_tdcg_json(tmp_path, PLAN_FILE)["cycles"][1]["notes"] == [
        "COMMIT wraps to SPECIFY",
        SKIP_NOTE.format(phase="REVIEW", date=today),
        SKIP_NOTE.format(phase="REFACTOR", date=today),
    ]


def test_skip_runs_the_tests_of_the_phase_it_leaves(tmp_path):
    write_tdcg_state(tmp_path, "GREEN", build_valid_plan(), build_config_with_test_command(FAILING))
    with pytest.raises(TestsShouldHavePassedError):
        run_tdcg_command(tmp_path, ["next", "--skipTo", "COMMIT"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "GREEN"


def test_skip_with_a_bad_plan_stays(tmp_path):
    plan = build_plan_without_field("goal")
    write_tdcg_state(tmp_path, "REVIEW", plan, build_config_with_test_command(PASSING))
    with pytest.raises(InvalidPlanError):
        run_tdcg_command(tmp_path, ["next", "--skipTo", "COMMIT"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "REVIEW"


def test_skip_over_a_phase_that_must_happen_stays_and_notes_nothing(tmp_path):
    write_project_in(tmp_path, "SPECIFY")
    with pytest.raises(PhaseNotSkippableError) as error:
        run_tdcg_command(tmp_path, ["next", "--skipTo", "GREEN"])
    assert str(error.value) == CANT_SKIP_RED
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"
    assert load_tdcg_json(tmp_path, PLAN_FILE)["cycles"][1]["notes"] == ["COMMIT wraps to SPECIFY"]


def test_skip_to_an_earlier_phase_is_an_error(tmp_path):
    write_tdcg_state(tmp_path, "GREEN", build_valid_plan(), build_config_with_test_command(PASSING))
    with pytest.raises(NotLaterPhaseError) as error:
        run_tdcg_command(tmp_path, ["next", "--skipTo", "RED"])
    assert str(error.value) == NOT_LATER_GREEN_TO_RED


# back
def test_back_moves_and_answers(tmp_path):
    write_project_in(tmp_path, "GREEN")
    answer = run_tdcg_command(tmp_path, ["back", "RED"])
    assert answer == CYCLE_ANSWER.format(phase="RED", key=SAMPLE_CYCLE_KEY, type="behaviour")
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "RED"


def test_back_runs_no_tests(tmp_path):
    write_tdcg_state(
        tmp_path, "GREEN", build_valid_plan(), build_config_with_test_command(LEAVES_A_MARKER)
    )
    run_tdcg_command(tmp_path, ["back", "RED"])
    assert not (tmp_path / MARKER).exists()


def test_back_to_a_later_phase_is_an_error(tmp_path):
    write_project_in(tmp_path, "SPECIFY")
    with pytest.raises(NotEarlierPhaseError) as error:
        run_tdcg_command(tmp_path, ["back", "GREEN"])
    assert str(error.value) == NOT_EARLIER_SPECIFY_TO_GREEN


def test_back_to_a_phase_the_cycle_type_does_not_have_is_an_error(tmp_path):
    plan = build_plan_with_cycle_field_set_to(SAMPLE_CYCLE_KEY, "type", "refactor")
    write_tdcg_state(tmp_path, "GREEN", plan, build_config_with_test_command(PASSING))
    with pytest.raises(PhaseNotInRouteError) as error:
        run_tdcg_command(tmp_path, ["back", "RED"])
    assert str(error.value) == PHASE_NOT_IN_ROUTE_BY_TYPE["refactor"]


def test_back_with_a_bad_plan_stays(tmp_path):
    plan = build_plan_without_field("goal")
    write_tdcg_state(tmp_path, "GREEN", plan, build_config_with_test_command(PASSING))
    with pytest.raises(InvalidPlanError):
        run_tdcg_command(tmp_path, ["back", "RED"])
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "GREEN"


# back PLAN: the way out when the plan is broken
def test_back_to_plan_answers(tmp_path):
    write_project_in(tmp_path, "GREEN")
    assert run_tdcg_command(tmp_path, ["back", "PLAN"]) == PLAN_ANSWER
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"


def test_back_to_plan_works_with_a_bad_plan(tmp_path):
    plan = build_plan_without_field("goal")
    write_tdcg_state(tmp_path, "GREEN", plan, build_config_with_test_command(PASSING))
    assert run_tdcg_command(tmp_path, ["back", "PLAN"]) == PLAN_ANSWER


def test_back_to_plan_works_with_no_plan_at_all(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    assert run_tdcg_command(tmp_path, ["back", "PLAN"]) == PLAN_ANSWER


def test_back_to_plan_from_plan_is_an_error(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "PLAN")
    with pytest.raises(NotEarlierPhaseError):
        run_tdcg_command(tmp_path, ["back", "PLAN"])
