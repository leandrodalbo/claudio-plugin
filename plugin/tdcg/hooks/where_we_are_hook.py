from pathlib import Path

from tdcg.context.where_we_are import build_where_we_are
from tdcg.core import messages
from tdcg.domain.hook_answer import HookAnswer
from tdcg.domain.hook_decision import HookDecision
from tdcg.hooks.hook_glue import ALLOWED, answer_claude_code


def decide_where_we_are(event: dict, project: Path) -> HookAnswer:
    """Never blocks. A bug is caught by the glue (answer_claude_code): it only warns, and the rules
    stay on, since the guards don't need this line."""
    line = build_where_we_are(project)
    if line is None:
        return ALLOWED
    return HookAnswer(HookDecision.ADD_CONTEXT, line)


def main() -> None:
    """Claude Code runs this on each message the user sends (UserPromptSubmit) and when a session
    starts or resumes (SessionStart): a resumed session replays old message context."""
    answer_claude_code(decide_where_we_are, messages.CLAUDE_NOT_TOLD)


if __name__ == "__main__":
    main()
