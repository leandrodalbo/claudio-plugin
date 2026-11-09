from pathlib import Path

from tdcg.core import messages
from tdcg.domain.file_stamp import Snapshot
from tdcg.domain.hook_answer import HookAnswer
from tdcg.domain.hook_decision import HookDecision
from tdcg.guards.shell_guard import (
    ensure_changed_files_allowed,
    ensure_tdcg_folder_kept,
    find_changed_files,
)
from tdcg.hooks.hook_glue import (
    ALLOWED,
    answer_claude_code,
    decide_by_rule_ignoring_off_switch,
    find_shell_call_id,
)
from tdcg.state.project_snapshot import take_snapshot
from tdcg.state.shell_snapshot_file import load_snapshot, remove_snapshot


def decide_after_shell_command(event: dict, project: Path) -> HookAnswer:
    """After a Bash command: the files it changed must follow the edit rules, or Claude stops.
    No snapshot from before means Claudio was off, or the command was blocked: nothing to check."""
    call_id = find_shell_call_id(event)
    if call_id is None:
        return ALLOWED
    before = load_snapshot(call_id)
    if before is None:
        return ALLOWED
    remove_snapshot(call_id)
    return _decide_changes_since(before, project)


def main() -> None:
    """Claude Code runs this after each Bash command, failed or not."""
    answer_claude_code(decide_after_shell_command, messages.COMMAND_CHANGES_NOT_CHECKED)


def _decide_changes_since(before: Snapshot, project: Path) -> HookAnswer:
    """A snapshot means Claudio was on before the command, so the rules run even if .tdcg/ is gone
    or the off switch is set now: the command itself may have done that."""
    return decide_by_rule_ignoring_off_switch(
        project, lambda: _ensure_changes_since_allowed(before, project), HookDecision.STOP
    )


def _ensure_changes_since_allowed(before: Snapshot, project: Path) -> None:
    ensure_tdcg_folder_kept(project)
    changed = find_changed_files(before, take_snapshot(project))
    ensure_changed_files_allowed(project, changed)


if __name__ == "__main__":
    main()
