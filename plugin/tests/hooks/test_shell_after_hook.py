import json
import shutil

import pytest

from tdcg.domain.hook_answer import HookAnswer, HookDecision
from tdcg.hooks import shell_after_hook
from tdcg.hooks.shell_before_hook import save_snapshot_before_command
from tdcg.hooks.shell_after_hook import decide_after_shell_command
from tdcg.state.shell_snapshot_file import load_snapshot
from tests.support.constants import OFF_IN_PHASE_FILE, PHASE_FILE
from tests.support.git_projects import write_project_file
from tests.support.hook_events import (
    CALL_ID,
    build_after_bash_event,
    build_bash_event,
    build_edit_event,
    build_event_without_call_id,
)
from tests.support.hook_processes import (
    build_environment_for,
    find_modules_loaded_by,
    run_hook,
    run_hook_process,
)
from tests.support.sample_projects import write_git_project_in
from tests.support.tdcg_files import has_tdcg_path, load_tdcg_text, write_tdcg_text

HOOK_MODULE = "tdcg.hooks.shell_after_hook"

# The sample plan's current cycle "2" has "tdcg/state/*.py" and "tests/state/test_phase_file.py";
# the sample config's test files are "tests/**".
SOURCE_IN_CYCLE = "tdcg/state/phase_file.py"
SOURCE_NOT_IN_CYCLE = "tdcg/core/errors.py"
TEST_IN_CYCLE = "tests/state/test_phase_file.py"
COMMITTED_FILES = {SOURCE_IN_CYCLE: "a = 1", SOURCE_NOT_IN_CYCLE: "e = 1", TEST_IN_CYCLE: "t = 1"}

ALLOWED = HookAnswer(HookDecision.ALLOW, "")


def write_project_before_command(project, phase):
    """A git project in phase, and the snapshot the bash hook saves before the command runs."""
    write_git_project_in(project, phase, COMMITTED_FILES)
    save_snapshot_before_command(build_bash_event("some command"), project)


def decide_after_command(project, event_name="PostToolUse"):
    return decide_after_shell_command(build_after_bash_event("some command", event_name), project)


def make_ensure_changed_files_allowed_crash(monkeypatch):
    def crash(project, changed):
        raise KeyError("something Claudio did not expect")

    monkeypatch.setattr(shell_after_hook, "ensure_changed_files_allowed", crash)


# nothing to check
def test_no_snapshot_is_allowed(tmp_path, temp_folder):
    """No snapshot: Claudio was off before the command, or the command was blocked."""
    write_git_project_in(tmp_path, "RED", COMMITTED_FILES)
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "changed")
    assert decide_after_command(tmp_path) == ALLOWED


def test_command_that_changes_nothing_is_allowed(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    assert decide_after_command(tmp_path) == ALLOWED


def test_other_tools_are_allowed(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "changed")
    event = build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE)
    assert decide_after_shell_command(event, tmp_path) == ALLOWED


def test_event_without_a_call_id_is_allowed(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "changed")
    event = build_event_without_call_id("Bash", {"command": "some command"})
    assert decide_after_shell_command(event, tmp_path) == ALLOWED


# allowed changes
def test_red_allows_a_test_file_in_the_cycle(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, TEST_IN_CYCLE, "t = 22")
    assert decide_after_command(tmp_path) == ALLOWED


def test_git_ignored_files_are_allowed(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, "tdcg/state/__pycache__/phase_file.cpython-313.pyc", "x")
    write_project_file(tmp_path, ".pytest_cache/v/cache/lastfailed", "{}")
    assert decide_after_command(tmp_path) == ALLOWED


def test_green_allows_deleting_a_file_in_the_cycle(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "GREEN")
    (tmp_path / SOURCE_IN_CYCLE).unlink()
    assert decide_after_command(tmp_path) == ALLOWED


def test_green_allows_a_move_inside_the_cycle(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "GREEN")
    (tmp_path / SOURCE_IN_CYCLE).rename(tmp_path / "tdcg/state/renamed.py")
    assert decide_after_command(tmp_path) == ALLOWED


def test_plan_may_change_in_plan(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "PLAN")
    write_tdcg_text(tmp_path, "plan.json", load_tdcg_text(tmp_path, "plan.json") + " ")
    assert decide_after_command(tmp_path) == ALLOWED


# stopped
def test_red_stops_on_a_changed_source_file(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.STOP
    assert "The shell changed files the rules don't allow" in answer.message
    assert f"RED only allows test files, and {SOURCE_IN_CYCLE} is not one" in answer.message


def test_green_stop_names_only_the_blocked_file(tmp_path, temp_folder):
    """E.g. a formatter changes a source file and a test file."""
    write_project_before_command(tmp_path, "GREEN")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    write_project_file(tmp_path, TEST_IN_CYCLE, "t = 22")
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.STOP
    assert TEST_IN_CYCLE in answer.message
    assert SOURCE_IN_CYCLE not in answer.message


def test_file_changed_before_and_changed_again_is_noticed(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "RED", COMMITTED_FILES)
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    save_snapshot_before_command(build_bash_event("some command"), tmp_path)
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 333")
    assert decide_after_command(tmp_path).decision is HookDecision.STOP


def test_deleting_a_tracked_file_not_in_the_cycle_stops(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "GREEN")
    (tmp_path / SOURCE_NOT_IN_CYCLE).unlink()
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.STOP
    assert f"{SOURCE_NOT_IN_CYCLE} is not in cycle 2's files" in answer.message


def test_move_out_of_the_cycle_stops(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "GREEN")
    (tmp_path / SOURCE_IN_CYCLE).rename(tmp_path / "tdcg/core/moved.py")
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.STOP
    assert "tdcg/core/moved.py is not in cycle 2's files" in answer.message


def test_new_file_not_in_the_cycle_stops_and_says_how_to_add_it(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "GREEN")
    write_project_file(tmp_path, "tdcg/core/new.py", "x = 1")
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.STOP
    assert "Go back to PLAN to add it" in answer.message


def test_several_bad_files_give_one_stop_naming_each(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    write_project_file(tmp_path, SOURCE_NOT_IN_CYCLE, "e = 22")
    answer = decide_after_command(tmp_path)
    assert SOURCE_IN_CYCLE in answer.message
    assert SOURCE_NOT_IN_CYCLE in answer.message


def test_failed_command_is_checked_the_same_way(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    answer = decide_after_command(tmp_path, "PostToolUseFailure")
    assert answer.decision is HookDecision.STOP


def test_shell_writing_into_tdcg_stops(tmp_path, temp_folder):
    """E.g. Claude writing .tdcg/off_in_phase to turn the rules off."""
    write_project_before_command(tmp_path, "GREEN")
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.STOP
    assert ".tdcg/off_in_phase is in .tdcg/" in answer.message


def test_shell_moving_the_phase_stops(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    assert decide_after_command(tmp_path).decision is HookDecision.STOP


def test_removing_the_tdcg_folder_stops(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "GREEN")
    shutil.rmtree(tmp_path / ".tdcg")
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.STOP
    assert "removed .tdcg/" in answer.message


def test_stop_message_says_not_to_undo(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    assert "don't undo it, the user decides" in decide_after_command(tmp_path).message


def test_stop_does_not_turn_claudio_off(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    decide_after_command(tmp_path)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


# the snapshot
def test_snapshot_is_removed_after_the_check(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    decide_after_command(tmp_path)
    assert load_snapshot(CALL_ID) is None


def test_snapshot_is_removed_after_a_stop(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    decide_after_command(tmp_path)
    assert load_snapshot(CALL_ID) is None


# a bug in Claudio
def test_bug_warns_and_turns_claudio_off_for_this_phase(tmp_path, temp_folder, monkeypatch):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    make_ensure_changed_files_allowed_crash(monkeypatch)
    answer = decide_after_command(tmp_path)
    assert answer.decision is HookDecision.WARN
    assert "Claudio hit a bug" in answer.message
    assert load_tdcg_text(tmp_path, OFF_IN_PHASE_FILE) == "RED"


def test_claudio_off_before_the_command_is_not_checked(tmp_path, temp_folder):
    """Off after a bug earlier in the phase: the before hook saves no snapshot, so nothing to check.
    An off file written during the command is Claude's trick, not this (see the .tdcg/ test)."""
    write_git_project_in(tmp_path, "RED", COMMITTED_FILES)
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "RED")
    save_snapshot_before_command(build_bash_event("some command"), tmp_path)
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    assert decide_after_command(tmp_path) == ALLOWED


# main: what Claude Code sees
def run_after_hook(project, temp_folder):
    return run_hook(HOOK_MODULE, project, build_after_bash_event("some command"), temp_folder)


def test_main_allows_with_exit_0_and_no_output(tmp_path, temp_folder):
    write_project_before_command(tmp_path, "RED")
    result = run_after_hook(tmp_path, temp_folder)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_main_stops_claude_with_continue_false_and_the_reason(tmp_path, temp_folder):
    """PostToolUse can't block (the command already ran); `continue: false` stops Claude."""
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    result = run_after_hook(tmp_path, temp_folder)
    output = json.loads(result.stdout)
    assert result.returncode == 0
    assert output["continue"] is False
    assert SOURCE_IN_CYCLE in output["stopReason"]


def test_main_with_bad_input_warns_and_allows(tmp_path, temp_folder):
    result = run_hook_process(HOOK_MODULE, "not json", build_environment_for(tmp_path, temp_folder))
    assert result.returncode == 0
    assert "Claudio hit a bug" in json.loads(result.stdout)["systemMessage"]


@pytest.mark.parametrize("event_name", ["PostToolUse", "PostToolUseFailure"])
def test_main_reads_both_after_events(tmp_path, temp_folder, event_name):
    write_project_before_command(tmp_path, "RED")
    write_project_file(tmp_path, SOURCE_IN_CYCLE, "a = 22")
    event = build_after_bash_event("some command", event_name)
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert json.loads(result.stdout)["continue"] is False


# speed
def test_hook_does_not_load_jsonschema():
    assert "jsonschema" not in find_modules_loaded_by(HOOK_MODULE)
