from dataclasses import dataclass

from tdcg.domain.hook_decision import HookDecision


@dataclass(frozen=True)
class HookAnswer:
    """BLOCK: message is the reason Claude sees.
    WARN: the tool goes ahead, message is shown to the user.
    STOP: after a tool ran, Claude stops; message is shown to the user and stays in the chat.
    ADD_CONTEXT: message is added for Claude to read with the user's message.
    BLOCK_COMMAND: the command stops before Claude; message is shown to the user."""

    decision: HookDecision
    message: str
