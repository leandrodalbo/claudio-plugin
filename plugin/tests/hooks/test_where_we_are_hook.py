import json

from tdcg.hooks import where_we_are_hook
from tests.support.constants import (
    CLAUDE_NOT_TOLD,
    CLAUDE_NOT_TOLD_START,
    OFF_IN_PHASE_FILE,
    SAMPLE_CYCLE_FILES,
    SAMPLE_CYCLE_KEY,
    SAMPLE_CYCLE_WHAT,
    WHERE_WE_ARE_IN_CYCLE,
)
from tests.support.hook_events import build_prompt_event, build_session_start_event
from tests.support.hook_processes import (
    find_modules_loaded_by,
    make_crash,
    run_hook,
    run_hook_main_here,
)
from tests.support.sample_projects import write_project_in
from tests.support.skill_files import build_phase_rules_path
from tests.support.tdcg_files import has_tdcg_path

HOOK_MODULE = "tdcg.hooks.where_we_are_hook"
GREEN_LINE = WHERE_WE_ARE_IN_CYCLE.format(
    phase="GREEN",
    key=SAMPLE_CYCLE_KEY,
    what=SAMPLE_CYCLE_WHAT,
    type="behaviour",
    files=SAMPLE_CYCLE_FILES,
    rules=build_phase_rules_path("GREEN"),
)


# what Claude Code gets
def test_each_message_gets_the_line_as_context(tmp_path, temp_folder):
    write_project_in(tmp_path, "GREEN")
    result = run_hook(HOOK_MODULE, tmp_path, build_prompt_event("go on"), temp_folder)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": GREEN_LINE}
    }


def test_a_session_start_gets_the_line_too(tmp_path, temp_folder):
    """A resumed session replays old message context; session start tells the fresh phase."""
    write_project_in(tmp_path, "GREEN")
    result = run_hook(HOOK_MODULE, tmp_path, build_session_start_event("resume"), temp_folder)
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": GREEN_LINE}
    }


def test_claudio_off_adds_nothing(tmp_path, temp_folder):
    result = run_hook(HOOK_MODULE, tmp_path, build_prompt_event("go on"), temp_folder)
    assert result.returncode == 0
    assert result.stdout == ""


# a bug never stops the user
def test_a_bug_warns_and_leaves_the_rules_on(tmp_path, monkeypatch, capsys):
    """Only telling Claude failed: the guards still work, so Claudio is not turned off."""
    write_project_in(tmp_path, "GREEN")
    make_crash(monkeypatch, where_we_are_hook, "build_where_we_are")
    event = build_prompt_event("go on")
    answer = run_hook_main_here(where_we_are_hook, event, tmp_path, monkeypatch, capsys)
    assert answer["systemMessage"].startswith(CLAUDE_NOT_TOLD_START)
    assert answer["systemMessage"].endswith(CLAUDE_NOT_TOLD)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


def test_hook_does_not_load_jsonschema():
    """It runs on every message, so it must start fast."""
    assert "jsonschema" not in find_modules_loaded_by(HOOK_MODULE)
