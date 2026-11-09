from enum import Enum


class HookDecision(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn"
    # After a tool ran (it can't be blocked any more): Claude stops and the user decides.
    STOP = "stop"
    # Before Claude answers: text added for Claude to read (it never blocks).
    ADD_CONTEXT = "add_context"
    # A plugin command that stops before Claude: the user reads the answer.
    BLOCK_COMMAND = "block_command"
