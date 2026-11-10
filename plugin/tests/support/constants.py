TDCG_DIR = ".tdcg"
PHASE_FILE = "phase"
OFF_IN_PHASE_FILE = "off_in_phase"
PLAN_FILE = "plan.json"
CONFIG_FILE = "config.json"
DONE_DIR = "done"
ENCODING = "utf-8"
SNAPSHOT_DIR = "claudio"
JSON_INDENT = 2

ALL_PHASES = ["PLAN", "SPECIFY", "RED", "PROMPT", "GREEN", "REVIEW", "REFACTOR", "COMMIT"]

GIT_READ_COMMANDS = ["status", "diff", "log", "show", "blame", "ls-files"]
GIT_WRITE_COMMANDS = [
    "commit", "push", "pull", "fetch", "reset", "checkout", "switch", "restore", "branch",
    "stash", "merge", "rebase", "revert", "cherry-pick", "add", "rm", "mv", "tag", "config",
    "init", "clone", "clean", "am", "apply", "worktree", "notes", "gc", "update-ref",
]

# The route of each cycle type, written out in full
PHASES_WITHOUT_RED = ["PLAN", "SPECIFY", "PROMPT", "GREEN", "REVIEW", "REFACTOR", "COMMIT"]
FULL_ROUTE = ["SPECIFY", "RED", "PROMPT", "GREEN", "REVIEW", "REFACTOR", "COMMIT"]
ROUTE_WITHOUT_RED = ["SPECIFY", "PROMPT", "GREEN", "REVIEW", "REFACTOR", "COMMIT"]
TYPES_WITH_RED = ["behaviour", "coverage"]
TYPES_WITHOUT_RED = ["refactor", "documentation", "setup", "spike"]
ALL_CYCLE_TYPES = ["behaviour", "coverage", "refactor", "documentation", "setup", "spike"]

# What the tests must do when leaving a phase, the same for every cycle type (RED depends on it)
PHASES_WITH_PASSING_TESTS = ["GREEN", "REFACTOR"]
PHASES_WITH_NO_TEST_RUN = ["PLAN", "SPECIFY", "PROMPT", "REVIEW", "COMMIT"]

# What /claudio:next says when the test command's result doesn't fit the phase, written out in full
TESTS_SHOULD_HAVE_FAILED = (
    "RED: the tests pass, but RED needs a failing test. Write a test that fails first, "
    "then /claudio:next."
)
COVERAGE_TESTS_SHOULD_HAVE_PASSED = (
    "RED (coverage): the tests fail. Coverage tests are for code that already works: "
    "they must pass."
)
TESTS_SHOULD_HAVE_PASSED_BY_PHASE = {
    "GREEN": "GREEN: the tests fail. Make them pass, then /claudio:next.",
    "REFACTOR": "REFACTOR: the tests fail. Make them pass, then /claudio:next.",
}
PHASE_NOT_IN_ROUTE_BY_TYPE = {
    "refactor": "A refactor cycle has no RED. To change the cycle's type, go back to PLAN.",
    "documentation": (
        "A documentation cycle has no RED. To change the cycle's type, go back to PLAN."
    ),
    "setup": "A setup cycle has no RED. To change the cycle's type, go back to PLAN.",
    "spike": "A spike cycle has no RED. To change the cycle's type, go back to PLAN.",
}

# The line Claude is told on every message. {rules} = that phase's file in the skill.
WHERE_WE_ARE_IN_PLAN = (
    "Claudio: phase PLAN. Only .tdcg/plan.json and .tdcg/config.json may change. "
    "Rules for this phase: {rules}"
)
WHERE_WE_ARE_IN_CYCLE = (
    'Claudio: phase {phase}, cycle {key} "{what}" ({type}). Files: {files}. '
    "Rules for this phase: {rules}"
)
WHERE_WE_ARE_PROBLEM = "Claudio: {problem}"
WHERE_WE_ARE_OFF = "Claudio: phase {phase}. The rules are off until the next phase."
# The sample plan's current cycle, as the line shows it
SAMPLE_CYCLE_KEY = "2"
SAMPLE_CYCLE_WHAT = "next"
SAMPLE_CYCLE_FILES = "tdcg/state/*.py, tests/state/test_phase_file.py"
NO_CYCLE_LEFT_PROBLEM = (
    "Every cycle in the plan is done. Finish the plan with /claudio:next, "
    "or go back to PLAN to add a cycle."
)
UNKNOWN_PHASE_PROBLEM = (
    "Unknown phase '{word}' in {path}. Fix the file or delete it to start at PLAN."
)
BROKEN_PLAN_START = "Claudio: Can't read the plan at"
# The warning when this hook hits a bug: the rules stay on
CLAUDE_NOT_TOLD_START = "Claudio hit a bug (KeyError:"
CLAUDE_NOT_TOLD = "Claude was not told the phase; the rules still work."
BROKEN_PLAN_WHAT_TO_DO = "Go back to PLAN and regenerate the plan."

# The claudio skill: every file besides SKILL.md, written out in full
SKILL_FILES = [
    "working-together.md",
    "phases/plan.md",
    "phases/specify.md",
    "phases/red.md",
    "phases/prompt.md",
    "phases/green.md",
    "phases/review.md",
    "phases/refactor.md",
    "phases/commit.md",
    "craft/tdd-bdd-xp.md",
    "craft/clean-code.md",
    "craft/clean-architecture.md",
    "craft/solid.md",
    "craft/simplicity.md",
    "craft/design-patterns.md",
    "craft/tests.md",
    "craft/safety.md",
    "knowledge/efficiency.md",
    "knowledge/system-design.md",
    "knowledge/production.md",
    "knowledge/data-and-networks.md",
    "knowledge/runtime.md",
]
SKILL_NAME = "claudio"
SKILL_MAX_LINES = 500
SKILL_MAX_DESCRIPTION = 1536
PHASE_FILE_SECTIONS = ["Goal", "What may change", "Checklist"]
# Nothing lost: each must be a heading in its craft file
DESIGN_PATTERNS = [
    "Factory Method", "Abstract Factory", "Builder", "Prototype", "Singleton",
    "Adapter", "Bridge", "Composite", "Decorator", "Facade", "Flyweight", "Proxy",
    "Strategy", "State", "Observer", "Command", "Template Method", "Chain of Responsibility",
    "Iterator", "Mediator", "Memento", "Visitor",
    "Repository", "Dependency Injection", "Value Object", "Null Object",
]
SOLID_PRINCIPLES = [
    "Single responsibility", "Open/closed", "Liskov substitution", "Interface segregation",
    "Dependency inversion",
]
SIMPLICITY_PRINCIPLES = ["KISS", "DRY", "YAGNI", "Don't reinvent the wheel"]
TDD_BDD_XP_PRACTICES = ["TDD", "BDD", "eXtreme Programming"]

# What the /claudio commands answer, written out in full
PLAN_SCHEMA_FILE = "plan.schema.json"
DONE_PLAN_FILE = "done/phase-machine.json"
CYCLE_ANSWER = "Claudio: {phase}, cycle {key} ({type})."
PLAN_ANSWER = "Claudio: PLAN."
PLAN_FINISHED_ANSWER = "Claudio: the plan is done. Phase PLAN."
MOVE_NOTE = "Claudio moved the phase just now. Any older Claudio line in this message is out of date."
MOVE_COMMAND_FILES = ["back.md", "next.md"]
SET_UP_ANSWER = (
    "Claudio: set up here. Phase PLAN. "
    "Now tell Claude your plan: what to build, your test command and your test files."
)
SKIP_NOTE = "{phase} skipped, {date}"
TDCG_INSTRUCTIONS = (
    "/claudio:init: set up Claudio in this project\n"
    "/claudio:next: move to the next phase\n"
    "/claudio:next --skipTo <PHASE>: jump ahead, skipping phases\n"
    "/claudio:back <PHASE>: go back to an earlier phase\n"
    "/claudio:status: where we are, and this list"
)
ALREADY_SET_UP = "Claudio is already set up here."
NOT_SET_UP = "Claudio is not set up here. Start with /claudio:init."
UNKNOWN_INSTRUCTION = "Unknown instruction '/claudio:{words}'. These work:\n" + TDCG_INSTRUCTIONS
NOT_EARLIER_SPECIFY_TO_GREEN = (
    "Can't go back from SPECIFY to GREEN: GREEN is not an earlier phase."
)
NOT_LATER_GREEN_TO_RED = "Can't skip from GREEN to RED: RED is not a later phase."
CANT_SKIP_RED = (
    "Can't skip RED: it must happen in every behaviour cycle. "
    "Only REVIEW and REFACTOR can be skipped."
)
# The warning when a command hits a bug: it still stays away from Claude
TDCG_BUG_START = "Claudio hit a bug (KeyError:"
TDCG_BUG_END = "The phase did not change."
# The warning when the event itself can't be read
TDCG_LINE_NOT_READ = "Claudio could not read this message."

INSTRUCTIONS_THAT_NEED_A_PROJECT = [["status"], ["next"], ["back", "PLAN"], ["nonsense"]]
WRONG_INSTRUCTIONS = [
    ["nonsense"],
    ["init", "extra"],
    ["status", "extra"],
    ["next", "extra"],
    ["next", "--skipTo"],
    ["next", "--skipTo", "NOPE"],
    ["next", "--other", "REVIEW"],
    ["back"],
    ["back", "NOPE"],
    ["back", "RED", "extra"],
]
# Phase left, phase reached, on the sample plan's behaviour cycle
MOVES_THAT_RUN_NO_TESTS = [
    ("PLAN", "SPECIFY"),
    ("SPECIFY", "RED"),
    ("PROMPT", "GREEN"),
    ("REVIEW", "REFACTOR"),
]
MOVES_THAT_NEED_PASSING_TESTS = [("GREEN", "REVIEW"), ("REFACTOR", "COMMIT")]

# How Claude Code starts the plugin: hooks/hooks.json, written out in full
_RUN_MODULE = 'cd "${CLAUDE_PLUGIN_ROOT}" && python3 -m '
_RUN_WHERE_WE_ARE = {"type": "command", "command": _RUN_MODULE + "tdcg.hooks.where_we_are_hook"}
_RUN_VENV_SETUP = {"type": "command", "command": _RUN_MODULE + "tdcg.setup.venv_setup"}
# The command hook needs jsonschema: set up the venv first, then run the hook with its Python
_RUN_COMMAND_HOOK = (
    'cd "${CLAUDE_PLUGIN_ROOT}" && python3 -m tdcg.setup.venv_setup && '
    '"${CLAUDE_PLUGIN_DATA}/venv/bin/python3" -m tdcg.hooks.tdcg_command_hook'
)
_RUN_SHELL_AFTER = {"type": "command", "command": _RUN_MODULE + "tdcg.hooks.shell_after_hook"}
EXPECTED_HOOKS_FILE = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Edit|Write|NotebookEdit",
                "hooks": [{"type": "command", "command": _RUN_MODULE + "tdcg.hooks.edit_hook"}],
            },
            {
                "matcher": "Bash",
                "hooks": [
                    {"type": "command", "command": _RUN_MODULE + "tdcg.hooks.shell_before_hook"}
                ],
            },
        ],
        "PostToolUse": [{"matcher": "Bash", "hooks": [_RUN_SHELL_AFTER]}],
        "PostToolUseFailure": [{"matcher": "Bash", "hooks": [_RUN_SHELL_AFTER]}],
        "UserPromptSubmit": [{"hooks": [_RUN_WHERE_WE_ARE]}],
        "UserPromptExpansion": [
            {
                "matcher": "^claudio:(init|next|back|status)$",
                "hooks": [
                    {
                        "type": "command",
                        "command": _RUN_COMMAND_HOOK,
                        "onFailure": "block",
                    }
                ],
            }
        ],
        "SessionStart": [{"hooks": [_RUN_WHERE_WE_ARE, _RUN_VENV_SETUP]}],
    }
}
HOOK_MODULES = [
    "tdcg.hooks.edit_hook",
    "tdcg.hooks.shell_before_hook",
    "tdcg.hooks.shell_after_hook",
    "tdcg.hooks.where_we_are_hook",
    "tdcg.hooks.tdcg_command_hook",
    "tdcg.setup.venv_setup",
]

# How people install the plugin: plugin.json and the repo's marketplace, written out in full
_REPO_URL = "https://github.com/leandrodalbo/claudio-plugin"
_AUTHOR = {"name": "Leandro Dal Bo", "url": "https://github.com/leandrodalbo"}
_DESCRIPTION = "Guard rails for AI-assisted development: TDCG cycles, enforced."
EXPECTED_MANIFEST = {
    "name": "claudio",
    "version": "0.1.0",
    "description": _DESCRIPTION,
    "author": _AUTHOR,
    "license": "Apache-2.0",
    "homepage": _REPO_URL,
    "repository": _REPO_URL,
    "keywords": ["tdd", "tdcg", "xp", "guard-rails", "hooks"],
}
EXPECTED_MARKETPLACE = {
    "name": "claudio-plugin",
    "owner": _AUTHOR,
    # validate --strict refuses a marketplace with no description
    "description": "Claudio's own marketplace: guard rails for AI-assisted development.",
    "plugins": [{"name": "claudio", "source": "./plugin", "description": _DESCRIPTION}],
}
# Every library, pinned: a fresh venv with jsonschema 4.26.0 (pip freeze, 2026-11-10)
EXPECTED_REQUIREMENTS = [
    "attrs==26.1.0",
    "jsonschema==4.26.0",
    "jsonschema-specifications==2025.9.1",
    "referencing==0.37.0",
    "rpds-py==2026.9.1",
]

# The plugin's own venv (5.1)
PLUGIN_DATA_VARIABLE = "CLAUDE_PLUGIN_DATA"
VENV_DIR = "venv"
VENV_PYTHON = "venv/bin/python3"
DONE_MARK = "requirements.txt"
OLD_REQUIREMENTS = "jsonschema==4.0.0\n"
OLD_VENV_FILE = "venv/left-from-before.txt"
VENV_SETUP_FAILED = (
    "Claudio couldn't install its Python libraries ({step}: {error}). Guard rails still work; "
    "/claudio: commands don't. Fix: check your internet; on Debian/Ubuntu: "
    "sudo apt install python3-venv. Then try any /claudio: command again."
)
MAKING_THE_VENV = "making the venv"
INSTALLING_THE_LIBRARIES = "installing the libraries"
FINDING_THE_DATA_FOLDER = "finding the plugin's data folder"
DATA_FOLDER_NOT_SET = "CLAUDE_PLUGIN_DATA is not set"
SAMPLE_PIP_ERROR = "ERROR: No matching distribution found for jsonschema==4.26.0"
# python3 -m venv's own words when the folder is under a file
VENV_UNDER_A_FILE_ERROR = "Error: [Errno 20] Not a directory: '{path}'"
SAMPLE_HOOK_EVENT = '{"hook_event_name": "UserPromptExpansion"}'
COMMAND_FILES = ["back.md", "init.md", "next.md", "status.md"]

# The free list (3.8)
FREE_FILES_FIELD = "claude_free_writing_files"
FREE_FILES = ["README.md", "notes/**"]
FREE_FILE = "README.md"
FREE_FILE_IN_A_FOLDER = "notes/deep/down/idea.md"
PATTERN_NOT_IN_A_LIST = "notes/**"
BAD_PATTERN_LISTS = [PATTERN_NOT_IN_A_LIST, ["notes/**", 7], None]
