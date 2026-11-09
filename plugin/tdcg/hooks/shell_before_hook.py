from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import (
    BASH_TOOL,
    COMMAND_FIELD,
    RUN_IN_BACKGROUND_FIELD,
    TOOL_INPUT,
    TOOL_NAME,
)
from tdcg.core.errors import NotAGitRepoError
from tdcg.domain.hook_answer import HookAnswer
from tdcg.guards.git_guard import ensure_git_allowed
from tdcg.hooks.hook_glue import ALLOWED, answer_claude_code, decide_by_rule, find_shell_call_id
from tdcg.state.project_snapshot import take_snapshot
from tdcg.state.shell_snapshot_file import write_snapshot


def decide_git_in_command(event: dict, project: Path) -> HookAnswer:
    """The git rule on the command text. Any other tool, or a shell call with no command text, is
    not this hook's business."""
    command = _find_command(event)
    if command is None:
        return ALLOWED
    return decide_by_rule(project, lambda: ensure_git_allowed(command))


def save_snapshot_before_command(event: dict, project: Path) -> HookAnswer:
    """Saves which files are changed right now, for the shell guard to compare after the command.
    Left alone: background commands (dev servers, watchers, long runs) and projects without git."""
    call_id = find_shell_call_id(event)
    if call_id is None or _is_background_command(event):
        return ALLOWED
    return decide_by_rule(project, lambda: _save_snapshot_if_git_repo(call_id, project))


def decide_before_shell_command(event: dict, project: Path) -> HookAnswer:
    """The git rule first; only an allowed command gets a snapshot."""
    answer = decide_git_in_command(event, project)
    if answer != ALLOWED:
        return answer
    return save_snapshot_before_command(event, project)


def main() -> None:
    """Claude Code runs this before each Bash command."""
    answer_claude_code(decide_before_shell_command, messages.COMMAND_NOT_CHECKED)


def _find_command(event: dict) -> str | None:
    """The shell command about to run, or None when the tool is not Bash or has no command text."""
    tool_input = event.get(TOOL_INPUT)
    if event.get(TOOL_NAME) != BASH_TOOL or not isinstance(tool_input, dict):
        return None
    command = tool_input.get(COMMAND_FIELD)
    if not isinstance(command, str):
        return None
    return command


def _is_background_command(event: dict) -> bool:
    tool_input = event.get(TOOL_INPUT)
    return isinstance(tool_input, dict) and tool_input.get(RUN_IN_BACKGROUND_FIELD) is True


def _save_snapshot_if_git_repo(call_id: str, project: Path) -> None:
    """Without git nothing tracks file changes, so there is nothing to compare: no snapshot."""
    try:
        write_snapshot(call_id, take_snapshot(project))
    except NotAGitRepoError:
        return


if __name__ == "__main__":
    main()
