import json

from tdcg.hooks import tdcg_command_hook
from tests.support.constants import (
    CYCLE_ANSWER,
    MOVE_NOTE,
    NOT_EARLIER_SPECIFY_TO_GREEN,
    NOT_SET_UP,
    OFF_IN_PHASE_FILE,
    PHASE_FILE,
    PLAN_ANSWER,
    PLAN_FINISHED_ANSWER,
    SAMPLE_CYCLE_KEY,
    SET_UP_ANSWER,
    TDCG_BUG_END,
    TDCG_BUG_START,
    TDCG_INSTRUCTIONS,
    TDCG_LINE_NOT_READ,
)
from tests.support.hook_events import (
    build_command_block,
    build_command_event,
    build_command_event_without_name,
    read_added_context,
)
from tests.support.hook_processes import make_crash, run_hook, run_hook_main_here
from tests.support.sample_configs import build_valid_config
from tests.support.sample_plans import build_plan_with_one_cycle_left
from tests.support.sample_projects import write_project_in
from tests.support.tdcg_files import (
    has_tdcg_path,
    load_tdcg_text,
    write_tdcg_state,
    write_tdcg_text,
)

HOOK_MODULE = "tdcg.hooks.tdcg_command_hook"
RED_ANSWER = CYCLE_ANSWER.format(phase="RED", key=SAMPLE_CYCLE_KEY, type="behaviour")


# a move that works hands over to Claude, who starts the phase
def test_next_moves_and_tells_claude(tmp_path, temp_folder):
    write_project_in(tmp_path, "SPECIFY")
    event = build_command_event("claudio:next", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert result.returncode == 0
    context = read_added_context(result.stdout)
    assert context.startswith(MOVE_NOTE)
    assert RED_ANSWER in context
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "RED"


def test_claude_is_told_the_new_phase_and_its_rules(tmp_path, temp_folder):
    write_project_in(tmp_path, "SPECIFY")
    event = build_command_event("claudio:next", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    context = read_added_context(result.stdout)
    assert 'phase RED, cycle 2 "next"' in context
    assert "phases/red.md" in context


def test_the_handover_names_the_event_it_answers(tmp_path, temp_folder):
    write_project_in(tmp_path, "SPECIFY")
    event = build_command_event("claudio:next", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptExpansion"


def test_going_back_tells_claude_too(tmp_path, temp_folder):
    write_project_in(tmp_path, "GREEN")
    event = build_command_event("claudio:back", "RED")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert RED_ANSWER in read_added_context(result.stdout)


def test_the_last_move_says_the_plan_is_done(tmp_path, temp_folder):
    write_tdcg_state(tmp_path, "COMMIT", build_plan_with_one_cycle_left(), build_valid_config())
    event = build_command_event("claudio:next", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert PLAN_FINISHED_ANSWER in read_added_context(result.stdout)


# a refused move and the commands that only report stay away from Claude
def test_a_refused_move_is_blocked_and_stays_put(tmp_path, temp_folder):
    write_tdcg_text(tmp_path, PHASE_FILE, "SPECIFY")
    event = build_command_event("claudio:next", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert json.loads(result.stdout)["decision"] == "block"
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


def test_the_arguments_reach_the_command(tmp_path, temp_folder):
    write_project_in(tmp_path, "GREEN")
    event = build_command_event("claudio:back", "RED")
    run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "RED"


def test_an_error_is_the_answer(tmp_path, temp_folder):
    write_project_in(tmp_path, "SPECIFY")
    event = build_command_event("claudio:back", "GREEN")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert json.loads(result.stdout) == build_command_block(NOT_EARLIER_SPECIFY_TO_GREEN)
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


def test_status_with_no_arguments_answers(tmp_path, temp_folder):
    write_project_in(tmp_path, "PLAN")
    event = build_command_event("claudio:status", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    expected = build_command_block(f"{PLAN_ANSWER}\n{TDCG_INSTRUCTIONS}")
    assert json.loads(result.stdout) == expected


# no .tdcg/ yet
def test_without_tdcg_folder_init_sets_up(tmp_path, temp_folder):
    event = build_command_event("claudio:init", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert json.loads(result.stdout) == build_command_block(SET_UP_ANSWER)
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"


def test_without_tdcg_folder_next_says_so(tmp_path, temp_folder):
    event = build_command_event("claudio:next", "")
    result = run_hook(HOOK_MODULE, tmp_path, event, temp_folder)
    assert json.loads(result.stdout) == build_command_block(NOT_SET_UP)


# a bug
def test_a_bug_warns_and_leaves_the_phase(tmp_path, monkeypatch, capsys):
    write_project_in(tmp_path, "SPECIFY")
    make_crash(monkeypatch, tdcg_command_hook, "run_tdcg_command")
    event = build_command_event("claudio:next", "")
    answer = run_hook_main_here(tdcg_command_hook, event, tmp_path, monkeypatch, capsys)
    assert answer["decision"] == "block"
    assert answer["reason"].startswith(TDCG_BUG_START)
    assert answer["reason"].endswith(TDCG_BUG_END)
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


def test_a_bug_does_not_turn_the_rules_off(tmp_path, monkeypatch, capsys):
    """The guards are fine; only this command failed."""
    write_project_in(tmp_path, "SPECIFY")
    make_crash(monkeypatch, tdcg_command_hook, "run_tdcg_command")
    event = build_command_event("claudio:next", "")
    run_hook_main_here(tdcg_command_hook, event, tmp_path, monkeypatch, capsys)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


def test_an_event_that_can_not_be_read_warns_and_changes_nothing(tmp_path, temp_folder):
    write_project_in(tmp_path, "SPECIFY")
    result = run_hook(HOOK_MODULE, tmp_path, build_command_event_without_name(), temp_folder)
    assert result.returncode == 0
    warning = json.loads(result.stdout)["systemMessage"]
    assert warning.startswith(TDCG_BUG_START)
    assert warning.endswith(TDCG_LINE_NOT_READ)
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"
