"""The files that make the folder a Claude Code plugin, read as Claude Code reads them."""

import json

from tests.support.constants import ENCODING
from tests.support.hook_processes import PLUGIN_DIR

MANIFEST_FILE = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
HOOKS_FILE = PLUGIN_DIR / "hooks" / "hooks.json"
COMMANDS_DIR = PLUGIN_DIR / "commands"
PLAN_SCHEMA_SOURCE = PLUGIN_DIR / "tdcg" / "schema" / "plan.schema.json"


def load_manifest():
    return json.loads(MANIFEST_FILE.read_text(encoding=ENCODING))


def load_plan_schema_source():
    return PLAN_SCHEMA_SOURCE.read_text(encoding=ENCODING)


def find_command_files():
    return sorted(path.name for path in COMMANDS_DIR.iterdir())


def load_hooks_file():
    return json.loads(HOOKS_FILE.read_text(encoding=ENCODING))
