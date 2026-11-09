from pathlib import Path

import pytest

from tdcg.core.errors import ShellChangesBlockedError, TdcgError, TdcgFolderRemovedError
from tdcg.domain.file_stamp import FileStamp
from tdcg.guards.shell_guard import ensure_changed_files_allowed, find_changed_files
from tests.support.constants import FREE_FILE, FREE_FILES
from tests.support.sample_configs import build_config_with_free_files, build_valid_config
from tests.support.sample_plans import build_plan_with_all_cycles_done, build_valid_plan
from tests.support.sample_projects import write_project_in
from tests.support.tdcg_files import write_tdcg_state

# The sample plan's current cycle "2" has "tdcg/state/*.py" and "tests/state/test_phase_file.py";
# the sample config's test files are "tests/**".
SOURCE_IN_CYCLE = Path("tdcg/state/phase_file.py")
SOURCE_NOT_IN_CYCLE = Path("tdcg/core/errors.py")
TEST_IN_CYCLE = Path("tests/state/test_phase_file.py")

A = Path("a.py")
B = Path("b.py")
STAMP = FileStamp(100, 10)


# find_changed_files: no disk, only the two snapshots
def test_same_snapshots_have_no_changes():
    assert find_changed_files({A: STAMP}, {A: STAMP}) == []


def test_file_only_after_is_new():
    assert find_changed_files({}, {A: STAMP}) == [A]


def test_file_only_before_is_changed():
    """Listed before and not after: e.g. a changed file put back the way git has it."""
    assert find_changed_files({A: STAMP}, {}) == [A]


def test_different_time_is_a_change():
    assert find_changed_files({A: FileStamp(100, 10)}, {A: FileStamp(101, 10)}) == [A]


def test_different_size_is_a_change():
    assert find_changed_files({A: FileStamp(100, 10)}, {A: FileStamp(100, 11)}) == [A]


def test_file_gone_after_is_a_change():
    assert find_changed_files({A: STAMP}, {A: None}) == [A]


def test_gone_file_that_comes_back_is_a_change():
    """Gone before, back as git has it after, so not listed at all: still a change."""
    assert find_changed_files({A: None}, {}) == [A]


def test_file_gone_before_and_after_is_no_change():
    assert find_changed_files({A: None}, {A: None}) == []


def test_changes_come_sorted():
    assert find_changed_files({}, {B: STAMP, A: STAMP}) == [A, B]


# ensure_changed_files_allowed: the 3.2 rules for each changed file
def test_no_changes_are_allowed(tmp_path):
    write_project_in(tmp_path, "RED")
    ensure_changed_files_allowed(tmp_path, [])


def test_red_allows_a_test_file_in_the_cycle(tmp_path):
    write_project_in(tmp_path, "RED")
    ensure_changed_files_allowed(tmp_path, [TEST_IN_CYCLE])


def test_red_blocks_a_source_file_with_the_rule_reason(tmp_path):
    write_project_in(tmp_path, "RED")
    with pytest.raises(ShellChangesBlockedError) as error:
        ensure_changed_files_allowed(tmp_path, [SOURCE_IN_CYCLE])
    assert "The shell changed files the rules don't allow" in str(error.value)
    assert f"RED only allows test files, and {SOURCE_IN_CYCLE} is not one" in str(error.value)


def test_message_says_not_to_undo(tmp_path):
    write_project_in(tmp_path, "RED")
    with pytest.raises(ShellChangesBlockedError, match="don't undo it, the user decides"):
        ensure_changed_files_allowed(tmp_path, [SOURCE_IN_CYCLE])


def test_green_names_only_the_files_the_rules_block(tmp_path):
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(ShellChangesBlockedError) as error:
        ensure_changed_files_allowed(tmp_path, [SOURCE_IN_CYCLE, TEST_IN_CYCLE])
    assert str(TEST_IN_CYCLE) in str(error.value)
    assert str(SOURCE_IN_CYCLE) not in str(error.value)


def test_several_bad_files_are_all_listed_in_one_error(tmp_path):
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(ShellChangesBlockedError) as error:
        ensure_changed_files_allowed(tmp_path, [SOURCE_NOT_IN_CYCLE, TEST_IN_CYCLE])
    assert f"{SOURCE_NOT_IN_CYCLE} is not in cycle 2's files" in str(error.value)
    assert f"{TEST_IN_CYCLE} is a test file" in str(error.value)


def test_long_list_shows_the_first_20_reasons_and_counts_the_rest(tmp_path):
    """E.g. a formatter run over the whole project: no wall of text."""
    write_project_in(tmp_path, "GREEN")
    changed = [Path(f"tdcg/core/file_{number:02}.py") for number in range(25)]
    with pytest.raises(ShellChangesBlockedError) as error:
        ensure_changed_files_allowed(tmp_path, changed)
    assert str(error.value).count("is not in cycle 2's files") == 20
    assert "tdcg/core/file_19.py" in str(error.value)
    assert "tdcg/core/file_20.py" not in str(error.value)
    assert "and 5 more" in str(error.value)


def test_file_not_in_cycle_says_how_to_add_it(tmp_path):
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(ShellChangesBlockedError, match="Go back to PLAN to add it"):
        ensure_changed_files_allowed(tmp_path, [SOURCE_NOT_IN_CYCLE])


def test_same_reason_for_many_files_is_said_once(tmp_path):
    write_tdcg_state(tmp_path, "GREEN", build_plan_with_all_cycles_done(), build_valid_config())
    with pytest.raises(ShellChangesBlockedError) as error:
        ensure_changed_files_allowed(tmp_path, [SOURCE_IN_CYCLE, SOURCE_NOT_IN_CYCLE])
    assert str(error.value).count("Every cycle in the plan is done") == 1


def test_deleted_file_in_the_cycle_is_allowed(tmp_path):
    """The file is gone from disk; it still goes through the same rules."""
    write_project_in(tmp_path, "GREEN")
    ensure_changed_files_allowed(tmp_path, [Path("tdcg/state/gone.py")])


def test_move_inside_the_cycle_is_allowed(tmp_path):
    write_project_in(tmp_path, "GREEN")
    ensure_changed_files_allowed(tmp_path, [Path("tdcg/state/old.py"), Path("tdcg/state/new.py")])


def test_move_out_of_the_cycle_names_the_new_path(tmp_path):
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(ShellChangesBlockedError) as error:
        ensure_changed_files_allowed(tmp_path, [Path("tdcg/state/old.py"), SOURCE_NOT_IN_CYCLE])
    assert str(SOURCE_NOT_IN_CYCLE) in str(error.value)
    assert "tdcg/state/old.py" not in str(error.value)


def test_tdcg_files_are_locked_for_the_shell_too(tmp_path):
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(ShellChangesBlockedError, match=r"\.tdcg/off_in_phase is in \.tdcg/"):
        ensure_changed_files_allowed(tmp_path, [Path(".tdcg/off_in_phase")])


def test_plan_may_change_in_plan(tmp_path):
    write_project_in(tmp_path, "PLAN")
    ensure_changed_files_allowed(tmp_path, [Path(".tdcg/plan.json")])


@pytest.mark.parametrize("error", [ShellChangesBlockedError, TdcgFolderRemovedError])
def test_shell_guard_errors_are_claudio_errors(error):
    assert issubclass(error, TdcgError)


# the free list
def test_a_listed_file_changed_by_the_shell_is_allowed(tmp_path):
    config = build_config_with_free_files(FREE_FILES)
    write_tdcg_state(tmp_path, "SPECIFY", build_valid_plan(), config)
    ensure_changed_files_allowed(tmp_path, [Path(FREE_FILE)])
