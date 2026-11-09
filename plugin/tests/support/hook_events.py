import json

CALL_ID = "toolu_01"


def build_edit_event(tool_name, file):
    """A PreToolUse event as Claude Code sends it for Edit and Write."""
    return _build_event(tool_name, {"file_path": str(file), "old_string": "a", "new_string": "b"})


def build_notebook_event(file):
    return _build_event("NotebookEdit", {"notebook_path": str(file), "new_source": "x = 1"})


def build_bash_event(command):
    return _build_event("Bash", {"command": command})


def build_event_without_input(tool_name):
    return _build_event(tool_name, {})


def build_after_bash_event(command, event_name="PostToolUse"):
    """What Claude Code sends after a Bash command: PostToolUse, or PostToolUseFailure when it failed."""
    event = _build_event("Bash", {"command": command}, event_name)
    event["tool_response"] = {"stdout": "", "stderr": "", "interrupted": False}
    return event


def build_event_without_call_id(tool_name, tool_input):
    event = _build_event(tool_name, tool_input)
    del event["tool_use_id"]
    return event


def _build_event(tool_name, tool_input, event_name="PreToolUse"):
    return {
        "session_id": "abc123",
        "cwd": "/somewhere",
        "hook_event_name": event_name,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": CALL_ID,
    }


def build_prompt_event(prompt):
    """What Claude Code sends when the user sends a message (UserPromptSubmit)."""
    return {
        "session_id": "abc123",
        "cwd": "/somewhere",
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
    }


def build_command_event(name, arguments):
    """What Claude Code sends when the user types one of the plugin's commands."""
    return {
        "session_id": "abc123",
        "cwd": "/somewhere",
        "hook_event_name": "UserPromptExpansion",
        "expansion_type": "slash_command",
        "command_name": name,
        "command_args": arguments,
        "command_source": "plugin",
        "prompt": f"/{name} {arguments}",
    }


def build_command_event_without_name():
    event = build_command_event("claudio:next", "")
    del event["command_name"]
    return event


def build_session_start_event(source):
    """What Claude Code sends when a session starts; source is startup, resume, clear or compact."""
    return {
        "session_id": "abc123",
        "cwd": "/somewhere",
        "hook_event_name": "SessionStart",
        "source": source,
    }


def build_command_block(reason):
    """What a hook prints to stop a command: the user reads the reason, Claude never sees it."""
    return {"decision": "block", "reason": reason}


def read_added_context(stdout):
    """What a hook adds for Claude. Fails on any other answer, a block included."""
    return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]
