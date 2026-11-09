import json
from pathlib import Path

import pytest
from jsonschema.validators import validator_for

import tdcg
from tdcg.core.errors import DuplicateCycleError, InvalidPlanError, NoPlanError, RepeatedFieldError
from tdcg.state.plan_check import ensure_plan_valid
from tests.support.constants import ALL_CYCLE_TYPES, PLAN_FILE
from tests.support.sample_plans import (
    build_plan_with_cycle_field_set_to,
    build_plan_with_field_set_to,
    build_plan_with_schema_link,
    build_plan_without_cycle_field,
    build_plan_without_field,
    build_valid_plan,
)
from tests.support.tdcg_files import write_tdcg_bytes, write_tdcg_json, write_tdcg_text

SCHEMA = Path(tdcg.__file__).parent / "schema" / "plan.schema.json"


# the schema
def test_schema_is_a_valid_json_schema():
    schema = json.loads(SCHEMA.read_text())
    validator_for(schema).check_schema(schema)


# ensure_plan_valid
def test_valid_plan_passes(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    ensure_plan_valid(tmp_path)


@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
def test_each_cycle_type_passes(tmp_path, word):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", "type", word))
    ensure_plan_valid(tmp_path)


def test_schema_link_is_allowed(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_schema_link())
    ensure_plan_valid(tmp_path)


def test_no_plan_file_is_an_error(tmp_path):
    with pytest.raises(NoPlanError):
        ensure_plan_valid(tmp_path)


@pytest.mark.parametrize("text", ['{"title": "Phase machine",', "[]", '"just text"'])
def test_not_a_json_object_is_an_error(tmp_path, text):
    write_tdcg_text(tmp_path, PLAN_FILE, text)
    with pytest.raises(InvalidPlanError):
        ensure_plan_valid(tmp_path)


@pytest.mark.parametrize(
    "plan",
    [
        # missing or unknown plan fields
        build_plan_without_field("title"),
        build_plan_without_field("status"),
        build_plan_without_field("goal"),
        build_plan_without_field("cycles"),
        build_plan_with_field_set_to("owner", "me"),
        # missing or unknown cycle fields
        build_plan_without_cycle_field("2", "key"),
        build_plan_without_cycle_field("2", "what"),
        build_plan_without_cycle_field("2", "done"),
        build_plan_without_cycle_field("2", "notes"),
        build_plan_without_cycle_field("2", "files"),
        build_plan_with_cycle_field_set_to("2", "owner", "me"),
        # wrong types
        build_plan_with_field_set_to("title", 5),
        build_plan_with_field_set_to("status", None),
        build_plan_with_field_set_to("goal", ["a"]),
        build_plan_with_field_set_to("cycles", {}),
        build_plan_with_field_set_to("cycles", ["next"]),
        build_plan_with_cycle_field_set_to("2", "key", 2),
        build_plan_with_cycle_field_set_to("2", "what", None),
        build_plan_with_cycle_field_set_to("2", "done", "yes"),
        build_plan_with_cycle_field_set_to("2", "notes", "a note"),
        build_plan_with_cycle_field_set_to("2", "notes", [1]),
        build_plan_with_cycle_field_set_to("2", "files", "tdcg/core/errors.py"),
        build_plan_with_cycle_field_set_to("2", "files", [1]),
        # no files, or an empty one
        build_plan_with_cycle_field_set_to("2", "files", []),
        build_plan_with_cycle_field_set_to("2", "files", [""]),
        # odd titles
        build_plan_with_field_set_to("title", "read/write"),
        build_plan_with_field_set_to("title", "Phase_machine"),
        build_plan_with_field_set_to("title", "Phase machine "),
        build_plan_with_field_set_to("title", " Phase machine"),
        build_plan_with_field_set_to("title", "Phase  machine"),
        build_plan_with_field_set_to("title", ""),
        build_plan_with_field_set_to("title", "Phase machine\n"),
        # empty text
        build_plan_with_field_set_to("goal", ""),
        build_plan_with_cycle_field_set_to("2", "what", ""),
        # unknown status
        build_plan_with_field_set_to("status", "Active"),
        build_plan_with_field_set_to("status", "finished"),
        # unknown cycle type
        build_plan_with_cycle_field_set_to("2", "type", "banana"),
        build_plan_with_cycle_field_set_to("2", "type", "Refactor"),
        build_plan_with_cycle_field_set_to("2", "type", 5),
        # no cycles
        build_plan_with_field_set_to("cycles", []),
        # badly written keys
        build_plan_with_cycle_field_set_to("2", "key", "a"),
        build_plan_with_cycle_field_set_to("2", "key", "4A"),
        build_plan_with_cycle_field_set_to("2", "key", "4bb"),
        build_plan_with_cycle_field_set_to("2", "key", "04"),
        build_plan_with_cycle_field_set_to("2", "key", "0"),
        build_plan_with_cycle_field_set_to("2", "key", ""),
        build_plan_with_cycle_field_set_to("2", "key", " 4"),
        build_plan_with_cycle_field_set_to("2", "key", "4."),
        build_plan_with_cycle_field_set_to("2", "key", "4\n"),
    ],
)
def test_plan_that_breaks_the_schema_is_an_error(tmp_path, plan):
    write_tdcg_json(tmp_path, PLAN_FILE, plan)
    with pytest.raises(InvalidPlanError):
        ensure_plan_valid(tmp_path)


def test_error_says_where_the_problem_is(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", "key", "4A"))
    with pytest.raises(InvalidPlanError, match=r"cycles\[1\]\.key"):
        ensure_plan_valid(tmp_path)


def test_error_explains_the_rule_in_words(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", "key", "4A"))
    with pytest.raises(InvalidPlanError) as error:
        ensure_plan_valid(tmp_path)
    assert "A number from 1, optionally with one lowercase letter" in str(error.value)
    assert "[1-9]" not in str(error.value)


def test_error_lists_every_problem(tmp_path):
    plan = build_plan_with_field_set_to("title", "read/write")
    plan["status"] = "finished"
    write_tdcg_json(tmp_path, PLAN_FILE, plan)
    with pytest.raises(InvalidPlanError) as error:
        ensure_plan_valid(tmp_path)
    assert "$.title" in str(error.value)
    assert "$.status" in str(error.value)


def test_bad_json_error_says_the_line(tmp_path):
    write_tdcg_text(tmp_path, PLAN_FILE, '{\n  "title": "Phase machine",\n}')
    with pytest.raises(InvalidPlanError, match="line 2"):
        ensure_plan_valid(tmp_path)


def test_plan_that_is_not_an_object_says_what_it_must_be(tmp_path):
    write_tdcg_text(tmp_path, PLAN_FILE, '["Phase machine"]')
    with pytest.raises(InvalidPlanError, match="An object with title, status, goal and cycles"):
        ensure_plan_valid(tmp_path)


def test_empty_cycles_is_explained_in_words(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_field_set_to("cycles", []))
    with pytest.raises(InvalidPlanError, match="at least one cycle"):
        ensure_plan_valid(tmp_path)


def test_empty_cycle_files_is_explained_in_words(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", "files", []))
    with pytest.raises(InvalidPlanError, match="at least one file pattern"):
        ensure_plan_valid(tmp_path)


def test_plan_that_is_not_utf8_is_an_error(tmp_path):
    write_tdcg_bytes(tmp_path, PLAN_FILE, b'{"title": "caf\xe9"}')
    with pytest.raises(InvalidPlanError, match="not UTF-8"):
        ensure_plan_valid(tmp_path)


def test_repeated_plan_field_is_an_error(tmp_path):
    text = json.dumps(build_valid_plan()).replace('"status"', '"title": "Other", "status"', 1)
    write_tdcg_text(tmp_path, PLAN_FILE, text)
    with pytest.raises(RepeatedFieldError):
        ensure_plan_valid(tmp_path)


def test_repeated_cycle_key_is_an_error(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("3", "key", "2b"))
    with pytest.raises(DuplicateCycleError):
        ensure_plan_valid(tmp_path)
