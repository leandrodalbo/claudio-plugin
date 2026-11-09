"""Every text Claudio shows to people, in one place. Fixed values live in constants.py.
Templates use str.format: `{name}` is filled in by the error or hook that sends the message."""

# shared pieces
USER_DECIDES = "Tell the user; don't undo it, the user decides."
CLAUDE_CAN_HELP = "Claude can help. /claudio:next shows every problem."
PROBLEM_LINE = "- {problem}"
MORE_PROBLEMS_LINE = "- …and {hidden} more."

# phase
UNKNOWN_PHASE = "Unknown phase '{word}' in {path}. Fix the file or delete it to start at PLAN."
NOT_EARLIER_PHASE = "Can't go back from {current} to {target}: {target} is not an earlier phase."
NOT_LATER_PHASE = "Can't skip from {current} to {target}: {target} is not a later phase."
PHASE_NOT_IN_ROUTE = (
    "A {cycle_type} cycle has no {phase}. To change the cycle's type, go back to PLAN."
)
PHASE_NOT_SKIPPABLE = (
    "Can't skip {phase}: it must happen in every {cycle_type} cycle. "
    "Only REVIEW and REFACTOR can be skipped."
)

# plan
NO_PLAN = "No plan at {path}. Write one in the PLAN phase first."
INVALID_PLAN = "Bad plan at {path}:\n{problems}\nSee plan.schema.json."
BROKEN_PLAN = (
    "Can't read the plan at {path}:\n{problems}\n"
    "Go back to PLAN and regenerate the plan. " + CLAUDE_CAN_HELP
)
NO_CYCLE_LEFT = (
    "Every cycle in the plan is done. Finish the plan with /claudio:next, "
    "or go back to PLAN to add a cycle."
)
DUPLICATE_CYCLE = "Cycle {key} appears more than once in {path}. Each key must be unique."
CYCLE_NOT_FOUND = "No cycle {key} in the plan at {path}."
CYCLE_ALREADY_DONE = "Cycle {key} is already done."
DONE_PLAN_EXISTS = "A completed plan already exists at {path}. Rename one of the plans first."

# config
NO_CONFIG = "No config at {path}. Create it with test_command and test_files."
INVALID_CONFIG = "Bad config at {path}:\n{problems}\nSee config.schema.json."
BROKEN_CONFIG = (
    "Can't read the config at {path}:\n{problems}\n"
    "Go back to PLAN and regenerate it. " + CLAUDE_CAN_HELP
)

# reading JSON files
NOT_UTF8 = "the file is not UTF-8 text ({reason})"
BAD_JSON = "line {line}, column {column}: {reason}"
NOT_A_JSON_OBJECT = "the file must be a JSON object, starting with {"
REPEATED_FIELD = "Field '{field}' appears more than once in {path}."
MISSING_FIELD = "missing field {field}"
WRONG_TYPE = "{field} must be {expected}, not {value}"
CYCLE_PROBLEM = "cycle {key}: {problem}"
LIST_OF_TEXT = "a list of text"
TRUE_OR_FALSE = "true or false"
SCHEMA_RULE_IN_WORDS = "{where}: {value} is not valid. {rule}"
SCHEMA_PROBLEM = "{where}: {problem}"

# edits
# the only files Claude may write in PLAN, said the same way in every message
PLAN_FILES = ".tdcg/plan.json and .tdcg/config.json"

OUTSIDE_PROJECT = (
    "{file} is outside the project. Claude may only change project files, "
    "so please make this change yourself."
)
TDCG_FOLDER_LOCKED = (
    "{file} is in .tdcg/, which only the user changes. "
    "Claude may only write " + PLAN_FILES + ", in PLAN."
)
PHASE_BLOCKS_EDIT = (
    "{phase} doesn't allow editing {file}. PLAN only allows " + PLAN_FILES + "; "
    "SPECIFY, PROMPT, REVIEW and COMMIT allow no edits. Move on with /claudio:next."
)
NOT_A_TEST_FILE = (
    "RED only allows test files, and {file} is not one (see test_files in .tdcg/config.json)."
)
LOCKED_TEST_FILE = (
    "Tests are locked in {phase}, and {file} is a test file. Go back to RED to change a test."
)
FILE_NOT_IN_CYCLE = "{file} is not in cycle {key}'s files. Go back to PLAN to add it."

# git
GIT_WRITE_BLOCKED = (
    "git {subcommand} is blocked: Claudio keeps git read-only ({read_commands}). Run it yourself."
)
GIT_OUTPUT_BLOCKED = (
    "git {subcommand} {option} is blocked: it writes a file, and Claudio keeps git read-only. "
    "Run it without {option}."
)
GIT_NO_SUBCOMMAND = (
    "git with no subcommand is blocked: it could get one when it runs (e.g. from xargs). "
    "Name the subcommand, e.g. git status."
)
NOT_A_GIT_REPO = "{project} is not a git repo (or git can't read it)."

# shell
SHELL_CHANGES_BLOCKED = (
    "The shell changed files the rules don't allow:\n{problems}\n" + USER_DECIDES
)
TDCG_FOLDER_REMOVED = "The shell removed .tdcg/, which turns Claudio off. " + USER_DECIDES

# hooks
BUG_WARNING = "Claudio hit a bug ({kind}: {error}). {what_now}"
RULES_OFF_UNTIL_NEXT_PHASE = "The rules are off until the next phase."
EDIT_NOT_CHECKED = "This edit was not checked."
COMMAND_NOT_CHECKED = "This command was not checked."
COMMAND_CHANGES_NOT_CHECKED = "The files this command changed were not checked."
CLAUDE_NOT_TOLD = "Claude was not told the phase; the rules still work."

# where we are (told to Claude before every message)
WHERE_WE_ARE_IN_PLAN = (
    "Claudio: phase PLAN. Only " + PLAN_FILES + " may change. "
    "Rules for this phase: {rules}"
)
WHERE_WE_ARE_IN_CYCLE = (
    'Claudio: phase {phase}, cycle {key} "{what}" ({type}). Files: {files}. '
    "Rules for this phase: {rules}"
)
WHERE_WE_ARE_PROBLEM = "Claudio: {problem}"
WHERE_WE_ARE_OFF = "Claudio: phase {phase}. " + RULES_OFF_UNTIL_NEXT_PHASE

# the /claudio commands (answers for the user)
CYCLE_ANSWER = "Claudio: {phase}, cycle {key} ({type})."
PLAN_ANSWER = "Claudio: PLAN."
PLAN_FINISHED_ANSWER = "Claudio: the plan is done. Phase PLAN."
SET_UP_ANSWER = (
    "Claudio: set up here. Phase PLAN. "
    "Now tell Claude your plan: what to build, your test command and your test files."
)
SKIP_NOTE = "{phase} skipped, {date}"
# A move that worked, for Claude: the line added to the message before the move is out of date.
MOVE_CONTEXT = (
    "Claudio moved the phase just now. Any older Claudio line in this message is out of date.\n"
    "{answer}\n{where}"
)
INSTRUCTIONS = (
    "/claudio:init: set up Claudio in this project\n"
    "/claudio:next: move to the next phase\n"
    "/claudio:next --skipTo <PHASE>: jump ahead, skipping phases\n"
    "/claudio:back <PHASE>: go back to an earlier phase\n"
    "/claudio:status: where we are, and this list"
)
WHERE_WE_ARE_AND_INSTRUCTIONS = "{where}\n" + INSTRUCTIONS
ALREADY_SET_UP = "Claudio is already set up here."
NOT_SET_UP = "Claudio is not set up here. Start with /claudio:init."
UNKNOWN_INSTRUCTION = "Unknown instruction '/claudio:{words}'. These work:\n" + INSTRUCTIONS
PHASE_NOT_CHANGED = "The phase did not change."
TDCG_LINE_NOT_READ = "Claudio could not read this message."

# tests
TESTS_SHOULD_HAVE_FAILED = (
    "RED: the tests pass, but RED needs a failing test. Write a test that fails first, "
    "then /claudio:next."
)
COVERAGE_TESTS_SHOULD_HAVE_PASSED = (
    "RED (coverage): the tests fail. Coverage tests are for code that already works: "
    "they must pass."
)
TESTS_SHOULD_HAVE_PASSED = "{phase}: the tests fail. Make them pass, then /claudio:next."
