from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import PATH_FIELD_BY_EDIT_TOOL, TOOL_INPUT, TOOL_NAME
from tdcg.domain.hook_answer import HookAnswer
from tdcg.guards.edit_guard import ensure_edit_allowed
from tdcg.hooks.hook_glue import ALLOWED, answer_claude_code, decide_by_rule


def decide_before_edit(event: dict, project: Path) -> HookAnswer:
    """Edits only: anything else, or an edit with no path, is not this hook's business."""
    file = _find_edited_file(event)
    if file is None:
        return ALLOWED
    return decide_by_rule(project, lambda: ensure_edit_allowed(project, file))


def main() -> None:
    """Claude Code runs this before each Edit, Write or NotebookEdit."""
    answer_claude_code(decide_before_edit, messages.EDIT_NOT_CHECKED)


def _find_edited_file(event: dict) -> Path | None:
    """The file the tool is about to change, or None when the tool is not an edit or has no path."""
    field = PATH_FIELD_BY_EDIT_TOOL.get(event.get(TOOL_NAME))
    tool_input = event.get(TOOL_INPUT)
    if field is None or not isinstance(tool_input, dict):
        return None
    path = tool_input.get(field)
    if not path:
        return None
    return Path(path)


if __name__ == "__main__":
    main()
