TDCG_DIR = ".tdcg"
PHASE_FILE = "phase"
OFF_IN_PHASE_FILE = "off_in_phase"
PLAN_FILE = "plan.json"
CONFIG_FILE = "config.json"
DONE_DIR = "done"
SCHEMA_DIR = "schema"
PLAN_SCHEMA_FILE = "plan.schema.json"
CONFIG_SCHEMA_FILE = "config.schema.json"
JSON_EXTENSION = ".json"
JSON_INDENT = 2
ENCODING = "utf-8"
NEW_LINE = "\n"
DESCRIPTION = "description"
SCHEMA_FIELD = "$schema"
RULES_EXPLAINED_IN_WORDS = {"type", "pattern", "minLength", "minItems", "enum"}

TITLE = "title"
STATUS = "status"
GOAL = "goal"
CYCLES = "cycles"
KEY = "key"
DONE = "done"
FILES = "files"
NOTES = "notes"
TEST_FILES = "test_files"
CLAUDE_FREE_WRITING_FILES = "claude_free_writing_files"

TITLE_SPACE = " "
FILE_NAME_DASH = "-"

TOOL_NAME = "tool_name"
TOOL_INPUT = "tool_input"
PATH_FIELD_BY_EDIT_TOOL = {"Edit": "file_path", "Write": "file_path", "NotebookEdit": "notebook_path"}
BASH_TOOL = "Bash"
COMMAND_FIELD = "command"
PROJECT_DIR_VARIABLE = "CLAUDE_PROJECT_DIR"
SYSTEM_MESSAGE = "systemMessage"
BLOCK_EXIT_CODE = 2

# git.exe: Windows git, which WSL can run too. Compared in lower case: macOS ignores letter case.
GIT_NAMES = ("git", "git.exe")
GIT_READ_COMMANDS = ("status", "diff", "log", "show", "blame", "ls-files")
GIT_OPTIONS_WITH_VALUE = {
    "-C", "-c", "--git-dir", "--work-tree", "--namespace", "--attr-source", "--config-env",
}
# git with these and no subcommand only prints and stops.
GIT_VERSION_AND_HELP_OPTIONS = ("-v", "--version", "-h", "--help")
GIT_OUTPUT_OPTION = "--output"
OPTION_START = "-"
OPTION_VALUE_SIGN = "="
# Characters the shell reads as operators between commands (`;`, `&&`, `|`, `$( )`, `{ }`, `<<`).
SHELL_OPERATOR_CHARS = "();<>|&`{}"
# No comment characters: Python's shlex would end a word at `#` (`--format=#%h; git commit`),
# where the shell does not.
NO_COMMENT_CHARS = ""
# Inside one word, list marks split it again, so `['git', 'commit']` gives git and commit.
WORD_PIECE = r"[^\[\],]+"
# The rough split, for text the shell rules can't read (an open quote, like `echo don't`):
# where one command ends and the next starts,
COMMAND_BREAKS = r"[;&|\n(){}`]"
# the quotes and backslashes the shell drops ("g"it and g\it both run git),
QUOTES_AND_BACKSLASHES = r"['\"\\]"
# and one word: a run of anything except spaces, brackets, commas and < >.
WORD = r"[^\s\[\],<>]+"

# Shell guard (3.4): a snapshot of the changed files before each shell command, compared after it.
# Followed by "-<user>": on Linux the temp folder is shared, and another user's folder can't be
# written.
SNAPSHOT_DIR = "claudio"
TOOL_USE_ID = "tool_use_id"
RUN_IN_BACKGROUND_FIELD = "run_in_background"
# A stop message lists this many reasons at most, then counts the rest.
MAX_REASONS_SHOWN = 20
CONTINUE_FIELD = "continue"
# Telling Claude where we are (3.6): added to each message and at session start.
HOOK_EVENT_NAME = "hook_event_name"
HOOK_SPECIFIC_OUTPUT_FIELD = "hookSpecificOutput"
HOOK_EVENT_NAME_FIELD = "hookEventName"
ADDITIONAL_CONTEXT_FIELD = "additionalContext"
# The claudio skill: the knowledge Claude works with, in the plugin next to tdcg/.
SKILLS_DIR = "skills"
CLAUDIO_SKILL = "claudio"
PHASES_DIR = "phases"
MARKDOWN_EXTENSION = ".md"
LIST_SEPARATOR = ", "
# The plugin's own venv (5.1): in the folder Claude Code keeps for the plugin, built from the
# plugin's requirements.txt; the done mark next to the venv holds the Python version
# (major.minor) that built it, then the requirements it was built from.
PLUGIN_DATA_VARIABLE = "CLAUDE_PLUGIN_DATA"
REQUIREMENTS_FILE = "requirements.txt"
DONE_MARK_FILE = "venv-done.txt"
DONE_MARK_PYTHON_LINE = "python {major}.{minor}\n"
VENV_DIR = "venv"
VENV_PYTHON = ("bin", "python3")
MAKE_VENV = ("-m", "venv")
PIP_INSTALL = ("-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r")
# The plugin's commands (3.7): Claude Code names them "claudio:next", with the words in the args.
PLUGIN_COMMAND_PREFIX = "claudio:"
COMMAND_NAME_FIELD = "command_name"
COMMAND_ARGS_FIELD = "command_args"
INIT_WORD = "init"
NEXT_WORD = "next"
BACK_WORD = "back"
STATUS_WORD = "status"
SKIP_TO_OPTION = "--skipTo"
WORD_SEPARATOR = " "
DECISION_FIELD = "decision"
DECISION_BLOCK = "block"
REASON_FIELD = "reason"
STOP_REASON_FIELD = "stopReason"
# Files that differ from git's index or are new and not ignored, each name ending with NUL.
# Paths count from the folder git runs in, so a project inside a bigger repo works too.
GIT_LIST_CHANGED_FILES = (
    "git", "ls-files", "-z", "--modified", "--deleted", "--others", "--exclude-standard",
)
NUL = "\0"
