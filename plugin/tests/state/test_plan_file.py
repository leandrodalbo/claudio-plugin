import json

import pytest

from tdcg.core.errors import (
    BrokenPlanError,
    CycleAlreadyDoneError,
    CycleNotFoundError,
    DonePlanExistsError,
    NoCycleLeftError,
    NoPlanError,
    RepeatedFieldError,
)
from tdcg.domain.cycle import Cycle
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.plan_status import PlanStatus
from tdcg.state.plan_file import (
    add_cycle_note,
    complete_plan,
    find_next_cycle,
    finish_cycle,
    is_plan_done,
    read_plan,
)
from tests.support.constants import (
    ALL_CYCLE_TYPES,
    DONE_DIR,
    DONE_PLAN_FILE,
    NO_CYCLE_LEFT_PROBLEM,
    PLAN_FILE,
)
from tests.support.sample_plans import (
    build_plan_with_all_cycles_done,
    build_plan_with_cycle_field_set_to,
    build_plan_with_field_set_to,
    build_plan_with_schema_link,
    build_plan_without_cycle_field,
    build_plan_without_field,
    build_valid_plan,
)
from tests.support.tdcg_files import (
    has_tdcg_path,
    load_tdcg_json,
    load_tdcg_text,
    write_tdcg_bytes,
    write_tdcg_json,
    write_tdcg_text,
)


# read_plan
def test_no_plan_file_means_no_plan(tmp_path):
    assert read_plan(tmp_path) is None


def test_reads_title_status_and_goal(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    plan = read_plan(tmp_path)
    assert plan.title == "Phase machine"
    assert plan.status == PlanStatus.ACTIVE
    assert plan.goal == "Know the current phase."


def test_reads_cycles(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    assert read_plan(tmp_path).cycles == [
        Cycle(
            key="1",
            what="Read the phase",
            done=True,
            notes=[],
            files=["tdcg/state/phase_file.py"],
        ),
        Cycle(
            key="2",
            what="next",
            done=False,
            notes=["COMMIT wraps to SPECIFY"],
            files=["tdcg/state/*.py", "tests/state/test_phase_file.py"],
        ),
        Cycle(
            key="2b",
            what="next creates the folder",
            done=False,
            notes=[],
            files=["tdcg/state/phase_file.py"],
        ),
        Cycle(key="3", what="back", done=False, notes=[], files=["tdcg/**"]),
    ]


@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
def test_reads_the_cycle_type(tmp_path, word):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", "type", word))
    assert read_plan(tmp_path).cycles[1].type.value == word


def test_cycle_without_type_is_a_behaviour_cycle(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    assert read_plan(tmp_path).cycles[1].type == CycleType.BEHAVIOUR


def test_schema_link_is_allowed(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_schema_link())
    assert read_plan(tmp_path).title == "Phase machine"


def test_rules_only_the_full_check_knows_are_not_checked(tmp_path):
    """The quick read leaves the schema rules to ensure_plan_valid, run by /claudio:next."""
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", "key", "4A"))
    assert read_plan(tmp_path).cycles[1].key == "4A"


# a broken plan
@pytest.mark.parametrize("text", ['{"title": "Phase machine",', "[]", '"just text"'])
def test_not_a_json_object_is_broken(tmp_path, text):
    write_tdcg_text(tmp_path, PLAN_FILE, text)
    with pytest.raises(BrokenPlanError):
        read_plan(tmp_path)


@pytest.mark.parametrize(
    "plan, field",
    [
        (build_plan_without_field("title"), "title"),
        (build_plan_without_field("status"), "status"),
        (build_plan_without_field("goal"), "goal"),
        (build_plan_without_field("cycles"), "cycles"),
        (build_plan_without_cycle_field("2", "key"), "key"),
        (build_plan_without_cycle_field("2", "what"), "what"),
        (build_plan_without_cycle_field("2", "done"), "done"),
        (build_plan_without_cycle_field("2", "notes"), "notes"),
        (build_plan_without_cycle_field("2", "files"), "files"),
        (build_plan_with_cycle_field_set_to("2", "owner", "me"), "owner"),
    ],
)
def test_missing_or_unknown_field_is_broken_and_named(tmp_path, plan, field):
    write_tdcg_json(tmp_path, PLAN_FILE, plan)
    with pytest.raises(BrokenPlanError, match=field):
        read_plan(tmp_path)


def test_unknown_status_is_broken(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_field_set_to("status", "finished"))
    with pytest.raises(BrokenPlanError, match="finished"):
        read_plan(tmp_path)


def test_unknown_cycle_type_is_broken(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", "type", "banana"))
    with pytest.raises(BrokenPlanError, match="banana"):
        read_plan(tmp_path)


@pytest.mark.parametrize(
    "field, value",
    [
        ("files", "src/*"),
        ("files", ["src/*", 1]),
        ("files", None),
        ("done", "no"),
        ("done", 0),
        ("done", None),
    ],
)
def test_wrong_type_in_a_field_the_guards_use_is_broken_and_named(tmp_path, field, value):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_cycle_field_set_to("2", field, value))
    with pytest.raises(BrokenPlanError, match=field):
        read_plan(tmp_path)


def test_broken_plan_says_to_regenerate_it_in_plan(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_without_cycle_field("2", "files"))
    with pytest.raises(BrokenPlanError) as error:
        read_plan(tmp_path)
    assert "Go back to PLAN and regenerate the plan" in str(error.value)
    assert "/claudio:next" in str(error.value)


def test_bad_json_says_the_line(tmp_path):
    write_tdcg_text(tmp_path, PLAN_FILE, '{\n  "title": "Phase machine",\n}')
    with pytest.raises(BrokenPlanError, match="line 2"):
        read_plan(tmp_path)


def test_plan_that_is_not_utf8_is_broken(tmp_path):
    write_tdcg_bytes(tmp_path, PLAN_FILE, b'{"title": "caf\xe9"}')
    with pytest.raises(BrokenPlanError, match="not UTF-8"):
        read_plan(tmp_path)


def test_repeated_plan_field_is_an_error(tmp_path):
    text = json.dumps(build_valid_plan()).replace('"status"', '"title": "Other", "status"', 1)
    write_tdcg_text(tmp_path, PLAN_FILE, text)
    with pytest.raises(RepeatedFieldError):
        read_plan(tmp_path)


def test_repeated_cycle_field_is_an_error(tmp_path):
    text = json.dumps(build_valid_plan()).replace('"what"', '"key": "9", "what"', 1)
    write_tdcg_text(tmp_path, PLAN_FILE, text)
    with pytest.raises(RepeatedFieldError):
        read_plan(tmp_path)


# find_next_cycle
def test_next_cycle_without_plan_is_an_error(tmp_path):
    with pytest.raises(NoPlanError):
        find_next_cycle(tmp_path)


def test_next_cycle_is_the_first_one_not_done(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    assert find_next_cycle(tmp_path) == Cycle(
        key="2",
        what="next",
        done=False,
        notes=["COMMIT wraps to SPECIFY"],
        files=["tdcg/state/*.py", "tests/state/test_phase_file.py"],
    )


def test_no_next_cycle_when_all_are_done_is_an_error(tmp_path):
    """The helper that owns the rule throws for it: callers don't test for None."""
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_all_cycles_done())
    with pytest.raises(NoCycleLeftError) as error:
        find_next_cycle(tmp_path)
    assert str(error.value) == NO_CYCLE_LEFT_PROBLEM


def test_next_cycle_of_a_broken_plan_is_an_error(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_without_cycle_field("2", "files"))
    with pytest.raises(BrokenPlanError, match="files"):
        find_next_cycle(tmp_path)


# is_plan_done
def test_a_plan_with_a_cycle_left_is_not_done(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    assert not is_plan_done(tmp_path)


def test_a_plan_with_every_cycle_done_is_done(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_all_cycles_done())
    assert is_plan_done(tmp_path)


def test_is_plan_done_without_plan_is_an_error(tmp_path):
    with pytest.raises(NoPlanError):
        is_plan_done(tmp_path)


def test_is_plan_done_on_a_broken_plan_is_an_error(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_without_cycle_field("2", "files"))
    with pytest.raises(BrokenPlanError, match="files"):
        is_plan_done(tmp_path)


# finish_cycle
def test_finish_without_plan_is_an_error(tmp_path):
    with pytest.raises(NoPlanError):
        finish_cycle(tmp_path, "2")


@pytest.mark.parametrize("key", ["2", "2b", "3"])
def test_finish_marks_only_that_cycle_done(tmp_path, key):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    finish_cycle(tmp_path, key)
    expected = build_plan_with_cycle_field_set_to(key, "done", True)
    assert load_tdcg_json(tmp_path, PLAN_FILE) == expected


def test_finish_keeps_the_schema_link(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_with_schema_link())
    finish_cycle(tmp_path, "2")
    assert load_tdcg_json(tmp_path, PLAN_FILE)["$schema"] == "./plan.schema.json"


def test_finish_keeps_special_characters_readable(tmp_path):
    plan = build_plan_with_cycle_field_set_to("2", "notes", ["a — b", "café"])
    write_tdcg_json(tmp_path, PLAN_FILE, plan)
    finish_cycle(tmp_path, "2")
    saved = load_tdcg_text(tmp_path, PLAN_FILE)
    assert "a — b" in saved
    assert "café" in saved


def test_finish_unknown_cycle_is_an_error(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    before = load_tdcg_text(tmp_path, PLAN_FILE)
    with pytest.raises(CycleNotFoundError):
        finish_cycle(tmp_path, "9")
    assert load_tdcg_text(tmp_path, PLAN_FILE) == before


def test_finish_a_done_cycle_is_an_error(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    before = load_tdcg_text(tmp_path, PLAN_FILE)
    with pytest.raises(CycleAlreadyDoneError):
        finish_cycle(tmp_path, "1")
    assert load_tdcg_text(tmp_path, PLAN_FILE) == before


def test_finish_on_a_broken_plan_changes_nothing(tmp_path):
    write_tdcg_text(tmp_path, PLAN_FILE, '{"title": "Phase machine",')
    with pytest.raises(BrokenPlanError):
        finish_cycle(tmp_path, "1")
    assert load_tdcg_text(tmp_path, PLAN_FILE) == '{"title": "Phase machine",'


# add_cycle_note
def test_note_without_plan_is_an_error(tmp_path):
    with pytest.raises(NoPlanError):
        add_cycle_note(tmp_path, "2", "REVIEW skipped, 2026-11-06")


@pytest.mark.parametrize("key", ["2b", "3"])
def test_note_is_added_only_to_that_cycle(tmp_path, key):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    add_cycle_note(tmp_path, key, "REVIEW skipped, 2026-11-06")
    expected = build_plan_with_cycle_field_set_to(key, "notes", ["REVIEW skipped, 2026-11-06"])
    assert load_tdcg_json(tmp_path, PLAN_FILE) == expected


def test_note_goes_after_the_notes_already_there(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    add_cycle_note(tmp_path, "2", "REVIEW skipped, 2026-11-06")
    notes = ["COMMIT wraps to SPECIFY", "REVIEW skipped, 2026-11-06"]
    assert load_tdcg_json(tmp_path, PLAN_FILE) == build_plan_with_cycle_field_set_to(
        "2", "notes", notes
    )


def test_note_to_unknown_cycle_is_an_error(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    before = load_tdcg_text(tmp_path, PLAN_FILE)
    with pytest.raises(CycleNotFoundError):
        add_cycle_note(tmp_path, "9", "REVIEW skipped, 2026-11-06")
    assert load_tdcg_text(tmp_path, PLAN_FILE) == before


def test_note_on_a_broken_plan_changes_nothing(tmp_path):
    write_tdcg_text(tmp_path, PLAN_FILE, '{"title": "Phase machine",')
    with pytest.raises(BrokenPlanError):
        add_cycle_note(tmp_path, "2", "REVIEW skipped, 2026-11-06")
    assert load_tdcg_text(tmp_path, PLAN_FILE) == '{"title": "Phase machine",'


# complete_plan
def test_complete_without_plan_is_an_error(tmp_path):
    with pytest.raises(NoPlanError):
        complete_plan(tmp_path)


def test_complete_marks_all_cycles_done_and_moves_plan(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    complete_plan(tmp_path)
    expected = build_plan_with_all_cycles_done()
    expected["status"] = "done"
    assert not has_tdcg_path(tmp_path, PLAN_FILE)
    assert load_tdcg_json(tmp_path, DONE_PLAN_FILE) == expected


def test_complete_keeps_an_old_done_plan(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    before = load_tdcg_text(tmp_path, PLAN_FILE)
    write_tdcg_text(tmp_path, DONE_PLAN_FILE, "old plan")
    with pytest.raises(DonePlanExistsError):
        complete_plan(tmp_path)
    assert load_tdcg_text(tmp_path, DONE_PLAN_FILE) == "old plan"
    assert load_tdcg_text(tmp_path, PLAN_FILE) == before


def test_complete_on_a_broken_plan_changes_nothing(tmp_path):
    write_tdcg_json(tmp_path, PLAN_FILE, build_plan_without_field("title"))
    before = load_tdcg_text(tmp_path, PLAN_FILE)
    with pytest.raises(BrokenPlanError):
        complete_plan(tmp_path)
    assert load_tdcg_text(tmp_path, PLAN_FILE) == before
    assert not has_tdcg_path(tmp_path, DONE_DIR)
