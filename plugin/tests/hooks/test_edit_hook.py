import json

import pytest

from tdcg.core.errors import (
    BrokenConfigError,
    BrokenPlanError,
    FileNotInCycleError,
    InvalidConfigError,
    InvalidPlanError,
    LockedTestFileError,
    NoConfigError,
    NoCycleLeftError,
    NoPlanError,
    NotATestFileError,
    NotEarlierPhaseError,
    PhaseBlocksEditError,
    RepeatedFieldError,
    TdcgError,
    TdcgFolderLockedError,
    UnknownPhaseError,
)
from tdcg.domain.hook_answer import HookAnswer, HookDecision
from tdcg.hooks import edit_hook
from tdcg.hooks.edit_hook import decide_before_edit
from tests.support.constants import OFF_IN_PHASE_FILE, PHASE_FILE, PLAN_FILE
from tests.support.hook_events import (
    build_bash_event,
    build_edit_event,
    build_event_without_input,
    build_notebook_event,
)
from tests.support.hook_processes import (
    build_environment_for,
    build_environment_without_project,
    find_modules_loaded_by,
    run_hook,
    run_hook_process,
)
from tests.support.sample_plans import build_valid_plan
from tests.support.sample_projects import write_project_in
from tests.support.tdcg_files import has_tdcg_path, load_tdcg_text, write_tdcg_text

HOOK_MODULE = "tdcg.hooks.edit_hook"

# The sample plan's current cycle "2" has "tdcg/state/*.py"; "tdcg/core/errors.py" is not in it.
SOURCE_IN_CYCLE = "tdcg/state/phase_file.py"
SOURCE_NOT_IN_CYCLE = "tdcg/core/errors.py"

ALLOWED = HookAnswer(HookDecision.ALLOW, "")


def make_ensure_edit_allowed_crash(monkeypatch):
    def crash(project, file):
        raise KeyError("something Claudio did not expect")

    monkeypatch.setattr(edit_hook, "ensure_edit_allowed", crash)


# one shared base for Claudio's own errors
@pytest.mark.parametrize(
    "error",
    [
        UnknownPhaseError,
        NotEarlierPhaseError,
        NoPlanError,
        InvalidPlanError,
        BrokenPlanError,
        RepeatedFieldError,
        NoCycleLeftError,
        NoConfigError,
        InvalidConfigError,
        BrokenConfigError,
        TdcgFolderLockedError,
        PhaseBlocksEditError,
        NotATestFileError,
        LockedTestFileError,
        FileNotInCycleError,
    ],
)
def test_claudio_errors_share_one_base(error):
    assert issubclass(error, TdcgError)


# Claudio off
def test_project_without_tdcg_folder_allows_everything(tmp_path):
    event = build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE)
    assert decide_before_edit(event, tmp_path) == ALLOWED


# which events are checked
@pytest.mark.parametrize("tool_name", ["Edit", "Write"])
def test_edit_and_write_are_checked(tmp_path, tool_name):
    write_project_in(tmp_path, "GREEN")
    event = build_edit_event(tool_name, tmp_path / SOURCE_NOT_IN_CYCLE)
    answer = decide_before_edit(event, tmp_path)
    assert answer.decision is HookDecision.BLOCK


def test_notebook_edit_is_checked(tmp_path):
    write_project_in(tmp_path, "GREEN")
    answer = decide_before_edit(build_notebook_event(tmp_path / "notes.ipynb"), tmp_path)
    assert answer.decision is HookDecision.BLOCK


def test_allowed_edit_is_allowed(tmp_path):
    write_project_in(tmp_path, "GREEN")
    event = build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE)
    assert decide_before_edit(event, tmp_path) == ALLOWED


def test_other_tools_are_allowed(tmp_path):
    write_project_in(tmp_path, "SPECIFY")
    assert decide_before_edit(build_bash_event("ls"), tmp_path) == ALLOWED


@pytest.mark.parametrize("tool_name", ["Edit", "Write", "NotebookEdit"])
def test_event_without_a_path_is_allowed(tmp_path, tool_name):
    write_project_in(tmp_path, "SPECIFY")
    assert decide_before_edit(build_event_without_input(tool_name), tmp_path) == ALLOWED


@pytest.mark.parametrize("tool_input", [None, "text", ["a"]])
def test_tool_input_that_is_not_an_object_is_allowed(tmp_path, tool_input):
    write_project_in(tmp_path, "SPECIFY")
    event = {**build_event_without_input("Edit"), "tool_input": tool_input}
    assert decide_before_edit(event, tmp_path) == ALLOWED


# blocked by a rule
def test_block_reason_is_the_rule_message(tmp_path):
    write_project_in(tmp_path, "GREEN")
    answer = decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_NOT_IN_CYCLE), tmp_path)
    assert answer == HookAnswer(
        HookDecision.BLOCK, f"{SOURCE_NOT_IN_CYCLE} is not in cycle 2's files. Go back to PLAN to add it."
    )


def test_bad_plan_blocks_with_its_message(tmp_path):
    write_project_in(tmp_path, "GREEN")
    write_tdcg_text(tmp_path, PLAN_FILE, "{")
    answer = decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE), tmp_path)
    assert answer.decision is HookDecision.BLOCK
    assert "Go back to PLAN and regenerate the plan" in answer.message


# speed
def test_hook_does_not_load_jsonschema():
    assert "jsonschema" not in find_modules_loaded_by(HOOK_MODULE)


# a bug in Claudio
def test_bug_warns_and_allows(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_edit_allowed_crash(monkeypatch)
    answer = decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE), tmp_path)
    assert answer.decision is HookDecision.WARN
    assert "Claudio hit a bug" in answer.message
    assert "something Claudio did not expect" in answer.message
    assert "off until the next phase" in answer.message


def test_bug_turns_claudio_off_for_this_phase(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_edit_allowed_crash(monkeypatch)
    decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE), tmp_path)
    assert load_tdcg_text(tmp_path, OFF_IN_PHASE_FILE) == "GREEN"


def test_after_a_bug_edits_in_the_same_phase_are_allowed_without_checks(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_edit_allowed_crash(monkeypatch)
    decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE), tmp_path)
    monkeypatch.undo()
    answer = decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_NOT_IN_CYCLE), tmp_path)
    assert answer == ALLOWED


def test_claudio_is_back_on_in_the_next_phase(tmp_path, monkeypatch):
    write_project_in(tmp_path, "GREEN")
    make_ensure_edit_allowed_crash(monkeypatch)
    decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE), tmp_path)
    monkeypatch.undo()
    write_tdcg_text(tmp_path, PHASE_FILE, "REFACTOR")
    answer = decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_NOT_IN_CYCLE), tmp_path)
    assert answer.decision is HookDecision.BLOCK


def test_rule_blocks_do_not_turn_claudio_off(tmp_path):
    write_project_in(tmp_path, "GREEN")
    decide_before_edit(build_edit_event("Edit", tmp_path / SOURCE_NOT_IN_CYCLE), tmp_path)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


# main: what Claude Code sees
def test_main_without_project_dir_warns_and_allows(tmp_path, temp_folder):
    environment = build_environment_without_project(temp_folder)
    event = build_edit_event("Edit", tmp_path / "a.py")
    result = run_hook_process(HOOK_MODULE, json.dumps(event), environment)
    assert result.returncode == 0
    assert "Claudio hit a bug" in json.loads(result.stdout)["systemMessage"]


def test_main_with_bad_input_warns_and_allows(tmp_path, temp_folder):
    environment = build_environment_for(tmp_path, temp_folder)
    result = run_hook_process(HOOK_MODULE, "not json", environment)
    assert result.returncode == 0
    assert "Claudio hit a bug" in json.loads(result.stdout)["systemMessage"]


def test_main_allows_with_exit_0_and_no_output(tmp_path, temp_folder):
    write_project_in(tmp_path, "GREEN")
    event = build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE)
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_main_blocks_with_exit_2_and_the_reason_on_stderr(tmp_path, temp_folder):
    write_project_in(tmp_path, "GREEN")
    event = build_edit_event("Edit", tmp_path / SOURCE_NOT_IN_CYCLE)
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert result.returncode == 2
    assert "is not in cycle 2's files" in result.stderr


def test_main_warns_with_exit_0_and_a_system_message(tmp_path, temp_folder):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    write_tdcg_text(tmp_path, PLAN_FILE, json.dumps(build_valid_plan()))
    # a config that is a folder, not a file: reading it fails in a way Claudio doesn't expect
    (tmp_path / ".tdcg" / "config.json").mkdir()
    event = build_edit_event("Edit", tmp_path / SOURCE_IN_CYCLE)
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert result.returncode == 0
    assert "Claudio hit a bug" in json.loads(result.stdout)["systemMessage"]
