"""What every Claudio hook does the same way: Claudio on or off, rule blocks, bugs, and the answer
to Claude Code. Each hook only finds its target in the event and names its rule."""

import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from types import MappingProxyType

from tdcg.core import messages
from tdcg.core.constants import (
    BASH_TOOL,
    ADDITIONAL_CONTEXT_FIELD,
    BLOCK_EXIT_CODE,
    CONTINUE_FIELD,
    DECISION_BLOCK,
    DECISION_FIELD,
    HOOK_EVENT_NAME,
    HOOK_EVENT_NAME_FIELD,
    HOOK_SPECIFIC_OUTPUT_FIELD,
    PROJECT_DIR_VARIABLE,
    REASON_FIELD,
    STOP_REASON_FIELD,
    SYSTEM_MESSAGE,
    TOOL_NAME,
    TOOL_USE_ID,
)
from tdcg.core.errors import TdcgError
from tdcg.domain.hook_answer import HookAnswer
from tdcg.domain.hook_decision import HookDecision
from tdcg.state.claudio_switch import is_claudio_on, is_off_in, turn_off_in
from tdcg.state.phase_file import read_phase

ALLOWED = HookAnswer(HookDecision.ALLOW, "")


def decide_by_rule(project: Path, ensure_rule: Callable[[], None]) -> HookAnswer:
    """Runs the rule (returns quietly or raises) and turns the result into an answer: allow, block
    with the rule's reason, or warn and turn Claudio off for this phase on a bug."""
    if not is_claudio_on(project) or _is_off_after_bug(project):
        return ALLOWED
    return decide_by_rule_ignoring_off_switch(project, ensure_rule, HookDecision.BLOCK)


def decide_by_rule_ignoring_off_switch(
    project: Path, ensure_rule: Callable[[], None], refusal: HookDecision
) -> HookAnswer:
    """decide_by_rule without asking whether Claudio is on: for a hook that already knows it was."""
    try:
        ensure_rule()
    except TdcgError as error:
        return HookAnswer(refusal, str(error))
    except Exception as error:
        return _turn_off_after_bug(project, error)
    return ALLOWED


def find_shell_call_id(event: dict) -> str | None:
    """Claude Code's id for this Bash call, the same before and after it runs.
    None for other tools."""
    call_id = event.get(TOOL_USE_ID)
    if event.get(TOOL_NAME) != BASH_TOOL or not isinstance(call_id, str):
        return None
    return call_id


def answer_claude_code(decide: Callable[[dict, Path], HookAnswer], not_checked: str) -> None:
    """A hook's main: Claude Code sends the event as JSON on stdin, the answer goes back as the exit
    code or printed JSON. Any bug left, even reading the input, warns with `not_checked` and lets
    the tool run."""
    try:
        _answer_event(decide)
    except Exception as error:
        _send_warning(build_bug_warning(error, not_checked))


def _answer_event(decide: Callable[[dict, Path], HookAnswer]) -> None:
    """Allow sends nothing back: exit 0, no output. Added context also names the event it answers;
    every other answer needs only itself."""
    event = json.load(sys.stdin)
    project = Path(os.environ[PROJECT_DIR_VARIABLE])
    answer = decide(event, project)
    if answer.decision is HookDecision.ALLOW:
        return
    if answer.decision is HookDecision.ADD_CONTEXT:
        _send_context(answer, event.get(HOOK_EVENT_NAME))
        return
    _SENDERS[answer.decision](answer)


def build_bug_warning(error: Exception, what_now: str) -> HookAnswer:
    warning = messages.BUG_WARNING.format(kind=type(error).__name__, error=error, what_now=what_now)
    return HookAnswer(HookDecision.WARN, warning)


def _is_off_after_bug(project: Path) -> bool:
    """After a bug the rules are off until the next phase."""
    return is_off_in(project, read_phase(project))


def _turn_off_after_bug(project: Path, error: Exception) -> HookAnswer:
    turn_off_in(project, read_phase(project))
    return build_bug_warning(error, messages.RULES_OFF_UNTIL_NEXT_PHASE)


# How each answer goes back to Claude Code.
def _send_block(answer: HookAnswer) -> None:
    """The reason on stderr, exit 2: the tool doesn't run and Claude reads why."""
    print(answer.message, file=sys.stderr)
    sys.exit(BLOCK_EXIT_CODE)


def _send_warning(answer: HookAnswer) -> None:
    """A system message the user sees; the tool still runs."""
    print(json.dumps({SYSTEM_MESSAGE: answer.message}))


def _send_stop(answer: HookAnswer) -> None:
    """Claude stops; the reason is shown to the user and stays in the chat."""
    print(json.dumps({CONTINUE_FIELD: False, STOP_REASON_FIELD: answer.message}))


def _send_command_block(answer: HookAnswer) -> None:
    """The command stops before Claude and the user reads the answer."""
    print(json.dumps({DECISION_FIELD: DECISION_BLOCK, REASON_FIELD: answer.message}))


def _send_context(answer: HookAnswer, event_name: str | None) -> None:
    """The text goes to Claude with the event it answers (a message or a session start)."""
    context = {HOOK_EVENT_NAME_FIELD: event_name, ADDITIONAL_CONTEXT_FIELD: answer.message}
    print(json.dumps({HOOK_SPECIFIC_OUTPUT_FIELD: context}))


# The answers that need only themselves; allow and added context are handled before the lookup.
_SENDERS = MappingProxyType(
    {
        HookDecision.BLOCK: _send_block,
        HookDecision.WARN: _send_warning,
        HookDecision.STOP: _send_stop,
        HookDecision.BLOCK_COMMAND: _send_command_block,
    }
)
