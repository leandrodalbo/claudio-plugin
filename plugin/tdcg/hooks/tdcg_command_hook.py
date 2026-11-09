from pathlib import Path

from tdcg.commands.tdcg_command import run_tdcg_command
from tdcg.context.where_we_are import build_where_we_are
from tdcg.core import messages
from tdcg.core.constants import (
    BACK_WORD,
    COMMAND_ARGS_FIELD,
    COMMAND_NAME_FIELD,
    NEXT_WORD,
    PLUGIN_COMMAND_PREFIX,
)
from tdcg.core.errors import TdcgError
from tdcg.domain.hook_answer import HookAnswer
from tdcg.domain.hook_decision import HookDecision
from tdcg.hooks.hook_glue import answer_claude_code, build_bug_warning

_MOVES = frozenset({NEXT_WORD, BACK_WORD})


def decide_command(event: dict, project: Path) -> HookAnswer:
    """Claude Code runs this only for the plugin's own commands (the matcher in hooks.json)."""
    instruction = event[COMMAND_NAME_FIELD].removeprefix(PLUGIN_COMMAND_PREFIX)
    return _answer_command(project, [instruction, *event[COMMAND_ARGS_FIELD].split()])


def _answer_command(project: Path, words: list[str]) -> HookAnswer:
    """A refusal or a bug blocks the command: let through, Claude would start a phase that never
    began. A bug is only this command failing, so the rules stay on."""
    try:
        return _run_command(project, words)
    except TdcgError as error:
        return HookAnswer(HookDecision.BLOCK_COMMAND, str(error))
    except Exception as error:
        warning = build_bug_warning(error, messages.PHASE_NOT_CHANGED)
        return HookAnswer(HookDecision.BLOCK_COMMAND, warning.message)


def _run_command(project: Path, words: list[str]) -> HookAnswer:
    """A move that worked goes on to Claude, who starts the phase. The other commands only report,
    so the user reads the answer and Claude is never asked."""
    answer = run_tdcg_command(project, words)
    if words[0] not in _MOVES:
        return HookAnswer(HookDecision.BLOCK_COMMAND, answer)
    context = messages.MOVE_CONTEXT.format(answer=answer, where=build_where_we_are(project))
    return HookAnswer(HookDecision.ADD_CONTEXT, context)


def main() -> None:
    """Claude Code runs this when the user types a plugin command (UserPromptExpansion), with the
    event as JSON on stdin. The answer goes back as printed JSON."""
    answer_claude_code(decide_command, messages.TDCG_LINE_NOT_READ)


if __name__ == "__main__":
    main()
