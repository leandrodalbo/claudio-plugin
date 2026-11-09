import json
from pathlib import Path

import pytest
from jsonschema.validators import validator_for

import tdcg
from tdcg.core.errors import InvalidConfigError, NoConfigError, RepeatedFieldError
from tdcg.state.config_check import ensure_config_valid
from tests.support.constants import BAD_PATTERN_LISTS, CONFIG_FILE, FREE_FILES, FREE_FILES_FIELD
from tests.support.sample_configs import (
    build_config_with_field_set_to,
    build_config_with_free_files,
    build_config_with_schema_link,
    build_config_without_field,
    build_valid_config,
)
from tests.support.tdcg_files import write_tdcg_bytes, write_tdcg_json, write_tdcg_text

SCHEMA = Path(tdcg.__file__).parent / "schema" / "config.schema.json"


# the schema
def test_schema_is_a_valid_json_schema():
    schema = json.loads(SCHEMA.read_text())
    validator_for(schema).check_schema(schema)


# ensure_config_valid
def test_valid_config_passes(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_valid_config())
    ensure_config_valid(tmp_path)


def test_editor_schema_line_is_allowed(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_schema_link())
    ensure_config_valid(tmp_path)


def test_no_config_file_is_an_error(tmp_path):
    with pytest.raises(NoConfigError, match="test_command and test_files"):
        ensure_config_valid(tmp_path)


@pytest.mark.parametrize(
    "config",
    [
        # missing or unknown fields
        build_config_without_field("test_command"),
        build_config_without_field("test_files"),
        build_config_with_field_set_to("max_source_files", 3),
        # wrong types
        build_config_with_field_set_to("test_command", ["python3", "-m", "pytest"]),
        build_config_with_field_set_to("test_files", "tests/**"),
        build_config_with_field_set_to("test_files", ["tests/**", 7]),
        # empty
        build_config_with_field_set_to("test_command", ""),
        build_config_with_field_set_to("test_command", "   "),
        build_config_with_field_set_to("test_files", []),
        build_config_with_field_set_to("test_files", [""]),
    ],
)
def test_config_breaking_the_schema_is_an_error(tmp_path, config):
    write_tdcg_json(tmp_path, CONFIG_FILE, config)
    with pytest.raises(InvalidConfigError):
        ensure_config_valid(tmp_path)


def test_config_that_is_not_an_object_says_what_it_must_be(tmp_path):
    write_tdcg_text(tmp_path, CONFIG_FILE, '["python3 -m pytest"]')
    with pytest.raises(InvalidConfigError, match="An object with test_command and test_files"):
        ensure_config_valid(tmp_path)


def test_spaces_only_test_command_is_explained_in_words(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_field_set_to("test_command", "   "))
    with pytest.raises(InvalidConfigError, match="Not empty or only spaces"):
        ensure_config_valid(tmp_path)


def test_empty_test_files_is_explained_in_words(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_field_set_to("test_files", []))
    with pytest.raises(InvalidConfigError, match="at least one file pattern"):
        ensure_config_valid(tmp_path)


def test_config_that_is_not_utf8_is_an_error(tmp_path):
    write_tdcg_bytes(tmp_path, CONFIG_FILE, b'{"test_command": "caf\xe9"}')
    with pytest.raises(InvalidConfigError, match="not UTF-8"):
        ensure_config_valid(tmp_path)


def test_error_says_where_the_problem_is(tmp_path):
    config = build_config_with_field_set_to("test_files", ["tests/**", 7])
    write_tdcg_json(tmp_path, CONFIG_FILE, config)
    with pytest.raises(InvalidConfigError, match=r"test_files\[1\]"):
        ensure_config_valid(tmp_path)


def test_error_explains_the_rule_in_words(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_field_set_to("test_command", ""))
    with pytest.raises(InvalidConfigError, match="Not empty"):
        ensure_config_valid(tmp_path)


def test_error_lists_every_problem(tmp_path):
    config = build_config_with_field_set_to("test_command", "")
    config["test_files"] = "tests/**"
    write_tdcg_json(tmp_path, CONFIG_FILE, config)
    with pytest.raises(InvalidConfigError) as error:
        ensure_config_valid(tmp_path)
    assert "$.test_command" in str(error.value)
    assert "$.test_files" in str(error.value)


def test_bad_json_error_says_the_line(tmp_path):
    write_tdcg_text(tmp_path, CONFIG_FILE, '{\n  "test_command": "pytest",\n}')
    with pytest.raises(InvalidConfigError, match="line 2"):
        ensure_config_valid(tmp_path)


def test_repeated_field_is_an_error(tmp_path):
    text = json.dumps(build_valid_config()).replace(
        '"test_files"', '"test_command": "other", "test_files"', 1
    )
    write_tdcg_text(tmp_path, CONFIG_FILE, text)
    with pytest.raises(RepeatedFieldError):
        ensure_config_valid(tmp_path)


# the free list
def test_a_config_with_a_free_list_passes(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_free_files(FREE_FILES))
    ensure_config_valid(tmp_path)


@pytest.mark.parametrize("value", BAD_PATTERN_LISTS)
def test_a_bad_free_list_is_invalid(tmp_path, value):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_free_files(value))
    with pytest.raises(InvalidConfigError, match=FREE_FILES_FIELD):
        ensure_config_valid(tmp_path)
