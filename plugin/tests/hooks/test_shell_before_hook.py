import json
from pathlib import Path

import pytest

from tdcg.domain.hook_answer import HookAnswer, HookDecision
from tdcg.hooks import shell_before_hook
from tdcg.hooks.shell_before_hook import decide_git_in_command, save_snapshot_before_command
from tdcg.state.shell_snapshot_file import load_snapshot
from tests.support.constants import ALL_PHASES, OFF_IN_PHASE_FILE, PHASE_FILE
from tests.support.git_projects import write_project_file
from tests.support.hook_events import (
    CALL_ID,
    build_bash_event,
    build_edit_event,
    build_event_without_call_id,
    build_event_without_input,
)
from tests.support.hook_processes import (
    build_environment_for,
    build_environment_without_project,
    find_modules_loaded_by,
    run_hook,
    run_hook_process,
)
from tests.support.sample_projects import write_git_project_in, write_project_in
from tests.support.tdcg_files import has_tdcg_path, load_tdcg_text, write_tdcg_text

HOOK_MODULE = "tdcg.hooks.shell_before_hook"

ALLOWED = HookAnswer(HookDecision.ALLOW, "")


def make_ensure_git_allowed_crash(monkeypatch):
    def crash(command):
        raise KeyError("something Claudio did not expect")

    monkeypatch.setattr(shell_before_hook, "ensure_git_allowed", crash)


# Claudio off
def test_project_without_tdcg_folder_allows_everything(tmp_path):
    assert decide_git_in_command(build_bash_event("git commit"), tmp_path) == ALLOWED


# which events are checked
def test_git_read_command_is_allowed(tmp_path):
    write_project_in(tmp_path, "GREEN")
    assert decide_git_in_command(build_bash_event("git status"), tmp_path) == ALLOWED


@pytest.mark.parametrize("phase", ALL_PHASES)
def test_git_write_command_is_blocked_in_every_phase(tmp_path, phase):
    write_project_in(tmp_path, phase)
    answer = decide_git_in_command(build_bash_event("git commit -m 'x'"), tmp_path)
    assert answer.decision is HookDecision.BLOCK


def test_other_tools_are_allowed(tmp_path):
    write_project_in(tmp_path, "GREEN")
    assert decide_git_in_command(build_edit_event("Edit", tmp_path / "a.py"), tmp_path) == ALLOWED


def test_event_without_a_command_is_allowed(tmp_path):
    write_project_in(tmp_path, "GREEN")
    assert decide_git_in_command(build_event_without_input("Bash"), tmp_path) == ALLOWED


@pytest.mark.parametrize("tool_input", [None, "text", ["a"]])
def test_tool_input_that_is_not_an_object_is_allowed(tmp_path, tool_input):
    write_project_in(tmp_path, "GREEN")
    event = {**build_event_without_input("Bash"), "tool_input": tool_input}
    assert decide_git_in_command(event, tmp_path) == ALLOWED


@pytest.mark.parametrize("command", [None, 42, ["git", "commit"]])
def test_command_that_is_not_text_is_allowed(tmp_path, command):
    write_project_in(tmp_path, "GREEN")
    event = {**build_event_without_input("Bash"), "tool_input": {"command": command}}
    assert decide_git_in_command(event, tmp_path) == ALLOWED


# blocked by a rule
def test_block_reason_is_the_rule_message(tmp_path):
    write_project_in(tmp_path, "GREEN")
    answer = decide_git_in_command(build_bash_event("git push"), tmp_path)
    assert answer == HookAnswer(
        HookDecision.BLOCK,
        "git push is blocked: Claudio keeps git read-only (status, diff, log, show, blame, ls-files). "
        "Run it yourself.",
    )


def test_rule_blocks_do_not_turn_claudio_off(tmp_path):
    write_project_in(tmp_path, "GREEN")
    decide_git_in_command(build_bash_event("git commit"), tmp_path)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


# a bug in Claudio
def test_bug_warns_and_allows(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_git_allowed_crash(monkeypatch)
    answer = decide_git_in_command(build_bash_event("git status"), tmp_path)
    assert answer.decision is HookDecision.WARN
    assert "Claudio hit a bug" in answer.message
    assert "something Claudio did not expect" in answer.message
    assert "off until the next phase" in answer.message


def test_bug_turns_claudio_off_for_this_phase(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_git_allowed_crash(monkeypatch)
    decide_git_in_command(build_bash_event("git status"), tmp_path)
    assert load_tdcg_text(tmp_path, OFF_IN_PHASE_FILE) == "GREEN"


def test_after_a_bug_commands_in_the_same_phase_are_allowed_without_checks(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_git_allowed_crash(monkeypatch)
    decide_git_in_command(build_bash_event("git status"), tmp_path)
    monkeypatch.undo()
    assert decide_git_in_command(build_bash_event("git commit"), tmp_path) == ALLOWED


def test_claudio_is_back_on_in_the_next_phase(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_git_allowed_crash(monkeypatch)
    decide_git_in_command(build_bash_event("git status"), tmp_path)
    monkeypatch.undo()
    write_tdcg_text(tmp_path, PHASE_FILE, "REFACTOR")
    answer = decide_git_in_command(build_bash_event("git commit"), tmp_path)
    assert answer.decision is HookDecision.BLOCK


# the snapshot before each command (3.4), saved only when Claudio is on and the command allowed
def make_take_snapshot_crash(monkeypatch):
    def crash(project):
        raise KeyError("something Claudio did not expect")

    monkeypatch.setattr(shell_before_hook, "take_snapshot", crash)


def test_snapshot_is_saved_under_the_call_id(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    write_project_file(tmp_path, "tdcg/state/new.py", "x = 1")
    answer = save_snapshot_before_command(build_bash_event("ls"), tmp_path)
    assert answer == ALLOWED
    assert Path("tdcg/state/new.py") in load_snapshot(CALL_ID)


def test_no_snapshot_without_tdcg_folder(tmp_path, temp_folder):
    assert save_snapshot_before_command(build_bash_event("ls"), tmp_path) == ALLOWED
    assert load_snapshot(CALL_ID) is None


def test_no_snapshot_for_other_tools(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    event = build_edit_event("Edit", tmp_path / "a.py")
    assert save_snapshot_before_command(event, tmp_path) == ALLOWED
    assert load_snapshot(CALL_ID) is None


def test_no_snapshot_without_a_call_id(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    event = build_event_without_call_id("Bash", {"command": "ls"})
    assert save_snapshot_before_command(event, tmp_path) == ALLOWED
    assert not list(temp_folder.rglob("*.json"))


def test_no_git_repo_is_ignored(tmp_path, temp_folder):
    """Without git nothing tracks file changes: Claudio stays out of the way (decided 2026-11-06)."""
    write_project_in(tmp_path, "GREEN")
    assert save_snapshot_before_command(build_bash_event("ls"), tmp_path) == ALLOWED
    assert load_snapshot(CALL_ID) is None


def test_background_command_is_ignored(tmp_path, temp_folder):
    """Dev servers, watchers, long runs: Claudio leaves them alone (decided 2026-11-06)."""
    write_git_project_in(tmp_path, "GREEN", {})
    event = build_bash_event("npm run dev")
    event["tool_input"]["run_in_background"] = True
    assert save_snapshot_before_command(event, tmp_path) == ALLOWED
    assert load_snapshot(CALL_ID) is None


def test_no_git_repo_does_not_turn_claudio_off(tmp_path, temp_folder):
    write_project_in(tmp_path, "GREEN")
    save_snapshot_before_command(build_bash_event("ls"), tmp_path)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


def test_no_snapshot_while_claudio_is_off_after_a_bug(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    assert save_snapshot_before_command(build_bash_event("ls"), tmp_path) == ALLOWED
    assert load_snapshot(CALL_ID) is None


def test_snapshot_bug_warns_and_turns_claudio_off(tmp_path, temp_folder, monkeypatch):
    write_git_project_in(tmp_path, "GREEN", {})
    make_take_snapshot_crash(monkeypatch)
    answer = save_snapshot_before_command(build_bash_event("ls"), tmp_path)
    assert answer.decision is HookDecision.WARN
    assert "Claudio hit a bug" in answer.message
    assert load_tdcg_text(tmp_path, OFF_IN_PHASE_FILE) == "GREEN"


# main: what Claude Code sees
def test_main_without_project_dir_warns_and_allows(temp_folder):
    environment = build_environment_without_project(temp_folder)
    result = run_hook_process(HOOK_MODULE, json.dumps(build_bash_event("git commit")), environment)
    assert result.returncode == 0
    assert "Claudio hit a bug" in json.loads(result.stdout)["systemMessage"]


def test_main_with_bad_input_warns_and_allows(tmp_path, temp_folder):
    environment = build_environment_for(tmp_path, temp_folder)
    result = run_hook_process(HOOK_MODULE, "not json", environment)
    assert result.returncode == 0
    assert "Claudio hit a bug" in json.loads(result.stdout)["systemMessage"]


def test_main_allows_with_exit_0_and_no_output(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    result = run_hook(HOOK_MODULE, tmp_path, build_bash_event("git status"), temp_folder)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_main_saves_the_snapshot_when_the_command_is_allowed(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    run_hook(HOOK_MODULE, tmp_path, build_bash_event("git status"), temp_folder)
    assert load_snapshot(CALL_ID) is not None


def test_main_saves_no_snapshot_when_the_command_is_blocked(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    run_hook(HOOK_MODULE, tmp_path, build_bash_event("git commit"), temp_folder)
    assert load_snapshot(CALL_ID) is None


def test_main_blocks_with_exit_2_and_the_reason_on_stderr(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    result = run_hook(HOOK_MODULE, tmp_path, build_bash_event("git commit"), temp_folder)
    assert result.returncode == 2
    assert "git commit is blocked" in result.stderr


def test_main_warns_with_exit_0_and_a_system_message(tmp_path, temp_folder):
    write_git_project_in(tmp_path, "GREEN", {})
    # a phase file that is a folder, not a file: reading it fails in a way Claudio doesn't expect
    (tmp_path / ".tdcg" / "phase").unlink()
    (tmp_path / ".tdcg" / "phase").mkdir()
    result = run_hook(HOOK_MODULE, tmp_path, build_bash_event("git status"), temp_folder)
    assert result.returncode == 0
    assert "Claudio hit a bug" in json.loads(result.stdout)["systemMessage"]


# speed
def test_hook_does_not_load_jsonschema():
    assert "jsonschema" not in find_modules_loaded_by(HOOK_MODULE)
