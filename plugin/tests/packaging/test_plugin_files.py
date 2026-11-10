"""The files Claude Code reads to install the plugin: they exist and point to real modules."""

import importlib.util

import pytest

from tests.support.constants import (
    COMMAND_FILES,
    EXPECTED_HOOKS_FILE,
    EXPECTED_MANIFEST,
    EXPECTED_MARKETPLACE,
    EXPECTED_REQUIREMENTS,
    HOOK_MODULES,
    MOVE_COMMAND_FILES,
)
from tests.support.hook_processes import PLUGIN_DIR
from tests.support.plugin_files import (
    COMMANDS_DIR,
    REPO_DIR,
    find_command_files,
    load_hooks_file,
    load_manifest,
    load_marketplace,
    load_plugin_requirements,
)
from tests.support.skill_files import load_frontmatter


# plugin.json
def test_the_manifest_has_every_field_people_and_validate_strict_need():
    assert load_manifest() == EXPECTED_MANIFEST


# .claude-plugin/marketplace.json at the repo root
def test_the_marketplace_lists_the_plugin_once():
    assert load_marketplace() == EXPECTED_MARKETPLACE


def test_the_marketplace_entry_has_the_plugins_own_name():
    assert [plugin["name"] for plugin in load_marketplace()["plugins"]] == [load_manifest()["name"]]


def test_the_marketplace_entry_points_to_the_plugin_folder():
    source = load_marketplace()["plugins"][0]["source"]
    assert (REPO_DIR / source).resolve() == PLUGIN_DIR.resolve()


# requirements.txt
def test_every_library_is_pinned():
    assert load_plugin_requirements().splitlines() == EXPECTED_REQUIREMENTS


# hooks.json
def test_every_hook_is_registered_on_its_event():
    assert load_hooks_file() == EXPECTED_HOOKS_FILE


@pytest.mark.parametrize("module", HOOK_MODULES)
def test_each_registered_hook_is_a_real_module(module):
    assert importlib.util.find_spec(module) is not None


# commands/
def test_there_is_one_file_per_instruction():
    assert find_command_files() == COMMAND_FILES


@pytest.mark.parametrize("name", COMMAND_FILES)
def test_claude_can_not_call_the_command(name):
    assert load_frontmatter(COMMANDS_DIR / name)["disable-model-invocation"] == "true"


@pytest.mark.parametrize("name", COMMAND_FILES)
def test_the_command_has_a_description_for_the_menu(name):
    assert load_frontmatter(COMMANDS_DIR / name)["description"]


@pytest.mark.parametrize("name", MOVE_COMMAND_FILES)
def test_a_move_tells_claude_to_start_the_new_phase(name):
    assert "start that phase" in (COMMANDS_DIR / name).read_text(encoding="utf-8")
