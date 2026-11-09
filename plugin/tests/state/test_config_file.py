import json

import pytest

from tdcg.core.errors import BrokenConfigError, NoConfigError, RepeatedFieldError
from tdcg.domain.config import Config
from tdcg.state.config_file import read_config, read_free_files
from tests.support.constants import BAD_PATTERN_LISTS, CONFIG_FILE, FREE_FILES, FREE_FILES_FIELD
from tests.support.sample_configs import (
    build_config_with_field_set_to,
    build_config_with_free_files,
    build_config_with_schema_link,
    build_config_without_field,
    build_valid_config,
)
from tests.support.tdcg_files import write_tdcg_bytes, write_tdcg_json, write_tdcg_text


# read_config
def test_reads_test_command_and_test_files(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_valid_config())
    assert read_config(tmp_path) == Config(
        test_command="python3 -m pytest", test_files=["tests/**", "src/test/**"]
    )


def test_editor_schema_line_is_allowed(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_schema_link())
    assert read_config(tmp_path).test_command == "python3 -m pytest"


def test_reads_utf8(tmp_path):
    config = build_config_with_field_set_to("test_files", ["tests/café/**"])
    write_tdcg_json(tmp_path, CONFIG_FILE, config)
    assert read_config(tmp_path).test_files == ["tests/café/**"]


def test_no_config_file_is_an_error(tmp_path):
    with pytest.raises(NoConfigError, match="test_command and test_files"):
        read_config(tmp_path)


def test_rules_only_the_full_check_knows_are_not_checked(tmp_path):
    """The quick read leaves the schema rules to ensure_config_valid, run by /claudio:next."""
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_field_set_to("test_command", ""))
    assert read_config(tmp_path).test_command == ""


# a broken config
@pytest.mark.parametrize("text", ['{"test_command": "pytest",', "[]", '"just text"'])
def test_not_a_json_object_is_broken(tmp_path, text):
    write_tdcg_text(tmp_path, CONFIG_FILE, text)
    with pytest.raises(BrokenConfigError):
        read_config(tmp_path)


@pytest.mark.parametrize(
    "config, field",
    [
        (build_config_without_field("test_command"), "test_command"),
        (build_config_without_field("test_files"), "test_files"),
        (build_config_with_field_set_to("max_source_files", 3), "max_source_files"),
    ],
)
def test_missing_or_unknown_field_is_broken_and_named(tmp_path, config, field):
    write_tdcg_json(tmp_path, CONFIG_FILE, config)
    with pytest.raises(BrokenConfigError, match=field):
        read_config(tmp_path)


@pytest.mark.parametrize("field", ["test_files", FREE_FILES_FIELD])
@pytest.mark.parametrize("value", BAD_PATTERN_LISTS)
def test_patterns_not_a_list_of_text_are_broken_and_named(tmp_path, field, value):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_field_set_to(field, value))
    with pytest.raises(BrokenConfigError, match=field):
        read_config(tmp_path)


def test_broken_config_says_to_regenerate_it_in_plan(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_without_field("test_files"))
    with pytest.raises(BrokenConfigError) as error:
        read_config(tmp_path)
    assert "Go back to PLAN and regenerate it" in str(error.value)
    assert "/claudio:next" in str(error.value)


def test_bad_json_says_the_line(tmp_path):
    write_tdcg_text(tmp_path, CONFIG_FILE, '{\n  "test_command": "pytest",\n}')
    with pytest.raises(BrokenConfigError, match="line 2"):
        read_config(tmp_path)


def test_config_that_is_not_utf8_is_broken(tmp_path):
    write_tdcg_bytes(tmp_path, CONFIG_FILE, b'{"test_command": "caf\xe9"}')
    with pytest.raises(BrokenConfigError, match="not UTF-8"):
        read_config(tmp_path)


def test_repeated_field_is_an_error(tmp_path):
    text = json.dumps(build_valid_config()).replace(
        '"test_files"', '"test_command": "other", "test_files"', 1
    )
    write_tdcg_text(tmp_path, CONFIG_FILE, text)
    with pytest.raises(RepeatedFieldError):
        read_config(tmp_path)


# the free list
def test_the_free_list_is_read(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_free_files(FREE_FILES))
    assert read_free_files(tmp_path) == FREE_FILES


def test_a_config_without_the_list_has_nothing_free(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_valid_config())
    assert read_free_files(tmp_path) == []


def test_no_config_has_nothing_free(tmp_path):
    """Just after /claudio:init: the config is written later, in PLAN."""
    assert read_free_files(tmp_path) == []
