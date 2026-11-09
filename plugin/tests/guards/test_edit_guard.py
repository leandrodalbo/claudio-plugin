from pathlib import Path

import pytest

from tdcg.core.errors import (
    BrokenConfigError,
    FileNotInCycleError,
    LockedTestFileError,
    NoConfigError,
    NoCycleLeftError,
    NoPlanError,
    NotATestFileError,
    OutsideProjectError,
    PhaseBlocksEditError,
    TdcgFolderLockedError,
)
from tdcg.guards.edit_guard import ensure_edit_allowed
from tests.support.constants import (
    ALL_PHASES,
    CONFIG_FILE,
    FREE_FILE,
    FREE_FILE_IN_A_FOLDER,
    FREE_FILES,
    FREE_FILES_FIELD,
    PATTERN_NOT_IN_A_LIST,
    PHASE_FILE,
    PLAN_FILE,
)
from tests.support.hook_processes import PLUGIN_DIR
from tests.support.sample_configs import build_config_with_free_files, build_valid_config
from tests.support.sample_plans import build_plan_with_all_cycles_done, build_valid_plan
from tests.support.sample_projects import write_project_in
from tests.support.skill_files import SKILL_DIR
from tests.support.tdcg_files import write_tdcg_json, write_tdcg_state, write_tdcg_text

# The sample plan's current cycle is "2", with files "tdcg/state/*.py" and
# "tests/state/test_phase_file.py". The sample config's test files are "tests/**" and "src/test/**".
SOURCE_IN_CYCLE = "tdcg/state/phase_file.py"
TEST_IN_CYCLE = "tests/state/test_phase_file.py"
SOURCE_NOT_IN_CYCLE = "tdcg/core/errors.py"
TEST_NOT_IN_CYCLE = "tests/state/test_plan_file.py"

NO_EDIT_PHASES = ["SPECIFY", "PROMPT", "REVIEW", "COMMIT"]
SOURCE_PHASES = ["GREEN", "REFACTOR"]


# files outside the project
@pytest.mark.parametrize("phase", ALL_PHASES)
def test_file_outside_the_project_is_blocked(tmp_path, phase):
    project = tmp_path / "project"
    write_project_in(project, phase)
    with pytest.raises(OutsideProjectError):
        ensure_edit_allowed(project, tmp_path / "notes.md")


# the claudio skill: the user's own copy of the knowledge, outside the project
@pytest.mark.parametrize("phase", ALL_PHASES)
def test_a_skill_file_may_change_in_any_phase(tmp_path, phase):
    write_project_in(tmp_path, phase)
    ensure_edit_allowed(tmp_path, SKILL_DIR / "craft" / "clean-code.md")


@pytest.mark.parametrize(
    "plugin_file",
    [
        PLUGIN_DIR / "tdcg" / "guards" / "edit_guard.py",
        PLUGIN_DIR / "skills" / "another-skill" / "SKILL.md",
        SKILL_DIR / ".." / ".." / "tdcg" / "guards" / "edit_guard.py",
    ],
)
def test_the_rest_of_the_plugin_stays_locked(tmp_path, plugin_file):
    """Claude may improve the knowledge, never switch off the guard rails."""
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(OutsideProjectError):
        ensure_edit_allowed(tmp_path, plugin_file)


# how paths are read
def test_relative_path_counts_from_the_project(tmp_path, monkeypatch):
    write_project_in(tmp_path / "project", "GREEN")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotInCycleError):
        ensure_edit_allowed(tmp_path / "project", Path(SOURCE_NOT_IN_CYCLE))


def test_the_project_folder_itself_follows_the_phase_rules(tmp_path):
    write_project_in(tmp_path, "GREEN")
    with pytest.raises(FileNotInCycleError):
        ensure_edit_allowed(tmp_path, tmp_path)


# .tdcg/
@pytest.mark.parametrize("phase", ALL_PHASES)
def test_phase_file_is_locked(tmp_path, phase):
    write_project_in(tmp_path, phase)
    with pytest.raises(TdcgFolderLockedError):
        ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / "phase")


def test_config_can_be_written_in_plan(tmp_path):
    write_project_in(tmp_path, "PLAN")
    ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / "config.json")


@pytest.mark.parametrize("phase", ALL_PHASES[1:])
def test_config_is_locked_outside_plan(tmp_path, phase):
    write_project_in(tmp_path, phase)
    with pytest.raises(TdcgFolderLockedError):
        ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / "config.json")


def test_plan_is_locked_outside_plan(tmp_path):
    write_project_in(tmp_path, "RED")
    with pytest.raises(TdcgFolderLockedError):
        ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / "plan.json")


# PLAN
def test_plan_can_be_written_in_plan(tmp_path):
    write_project_in(tmp_path, "PLAN")
    ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / "plan.json")


def test_plan_can_be_written_before_anything_exists(tmp_path):
    ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / "plan.json")


def test_plan_can_be_written_without_a_config(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "PLAN")
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / "plan.json")


def test_other_files_are_blocked_in_plan(tmp_path):
    write_project_in(tmp_path, "PLAN")
    with pytest.raises(PhaseBlocksEditError, match="PLAN"):
        ensure_edit_allowed(tmp_path, tmp_path / SOURCE_IN_CYCLE)


# phases with no edits
@pytest.mark.parametrize("phase", NO_EDIT_PHASES)
@pytest.mark.parametrize("file", [SOURCE_IN_CYCLE, TEST_IN_CYCLE])
def test_no_edits_in_phases_that_only_read(tmp_path, phase, file):
    write_project_in(tmp_path, phase)
    with pytest.raises(PhaseBlocksEditError, match=phase):
        ensure_edit_allowed(tmp_path, tmp_path / file)


# RED
def test_test_file_in_cycle_is_allowed_in_red(tmp_path):
    write_project_in(tmp_path, "RED")
    ensure_edit_allowed(tmp_path, tmp_path / TEST_IN_CYCLE)


def test_source_file_is_blocked_in_red(tmp_path):
    write_project_in(tmp_path, "RED")
    with pytest.raises(NotATestFileError):
        ensure_edit_allowed(tmp_path, tmp_path / SOURCE_IN_CYCLE)


def test_test_file_not_in_cycle_is_blocked_in_red(tmp_path):
    write_project_in(tmp_path, "RED")
    with pytest.raises(FileNotInCycleError, match=f"{TEST_NOT_IN_CYCLE} is not in cycle 2's files"):
        ensure_edit_allowed(tmp_path, tmp_path / TEST_NOT_IN_CYCLE)


# GREEN and REFACTOR
@pytest.mark.parametrize("phase", SOURCE_PHASES)
def test_source_file_in_cycle_is_allowed(tmp_path, phase):
    write_project_in(tmp_path, phase)
    ensure_edit_allowed(tmp_path, tmp_path / SOURCE_IN_CYCLE)


@pytest.mark.parametrize("phase", SOURCE_PHASES)
def test_test_file_is_locked(tmp_path, phase):
    write_project_in(tmp_path, phase)
    with pytest.raises(LockedTestFileError, match="Go back to RED"):
        ensure_edit_allowed(tmp_path, tmp_path / TEST_IN_CYCLE)


@pytest.mark.parametrize("phase", SOURCE_PHASES)
def test_source_file_not_in_cycle_is_blocked(tmp_path, phase):
    write_project_in(tmp_path, phase)
    with pytest.raises(FileNotInCycleError, match="Go back to PLAN to add it"):
        ensure_edit_allowed(tmp_path, tmp_path / SOURCE_NOT_IN_CYCLE)


# missing plan, cycle or config
@pytest.mark.parametrize("phase", ["RED", "GREEN", "REFACTOR"])
def test_no_plan_blocks_edits(tmp_path, phase):
    write_tdcg_text(tmp_path, PHASE_FILE, phase)
    with pytest.raises(NoPlanError):
        ensure_edit_allowed(tmp_path, tmp_path / SOURCE_IN_CYCLE)


def test_no_cycle_left_blocks_edits(tmp_path):
    write_tdcg_state(tmp_path, "GREEN", build_plan_with_all_cycles_done(), build_valid_config())
    with pytest.raises(NoCycleLeftError):
        ensure_edit_allowed(tmp_path, tmp_path / SOURCE_IN_CYCLE)


def test_no_config_blocks_edits(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    write_tdcg_json(tmp_path, PLAN_FILE, build_valid_plan())
    with pytest.raises(NoConfigError):
        ensure_edit_allowed(tmp_path, tmp_path / SOURCE_IN_CYCLE)


# the free list: the user's own choice, so it beats the phase and the cycle
@pytest.mark.parametrize("phase", ALL_PHASES)
def test_a_listed_file_may_change_in_any_phase(tmp_path, phase):
    write_tdcg_state(tmp_path, phase, build_valid_plan(), build_config_with_free_files(FREE_FILES))
    ensure_edit_allowed(tmp_path, tmp_path / FREE_FILE)


def test_a_folder_pattern_covers_files_at_any_depth(tmp_path):
    config = build_config_with_free_files(FREE_FILES)
    write_tdcg_state(tmp_path, "SPECIFY", build_valid_plan(), config)
    ensure_edit_allowed(tmp_path, tmp_path / FREE_FILE_IN_A_FOLDER)


def test_the_list_needs_no_plan(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_free_files(FREE_FILES))
    ensure_edit_allowed(tmp_path, tmp_path / FREE_FILE)


def test_the_list_works_when_every_cycle_is_done(tmp_path):
    config = build_config_with_free_files(FREE_FILES)
    write_tdcg_state(tmp_path, "GREEN", build_plan_with_all_cycles_done(), config)
    ensure_edit_allowed(tmp_path, tmp_path / FREE_FILE)


@pytest.mark.parametrize("phase", SOURCE_PHASES)
def test_the_list_wins_over_locked_tests(tmp_path, phase):
    config = build_config_with_free_files(["tests/**"])
    write_tdcg_state(tmp_path, phase, build_valid_plan(), config)
    ensure_edit_allowed(tmp_path, tmp_path / TEST_IN_CYCLE)


# still locked, whatever the list says
@pytest.mark.parametrize("name", [PHASE_FILE, PLAN_FILE, CONFIG_FILE, "done/old-plan.json"])
def test_the_tdcg_folder_stays_locked_even_if_listed(tmp_path, name):
    config = build_config_with_free_files(["**"])
    write_tdcg_state(tmp_path, "GREEN", build_valid_plan(), config)
    with pytest.raises(TdcgFolderLockedError):
        ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / name)


def test_a_file_outside_the_project_stays_locked_even_if_listed(tmp_path):
    project = tmp_path / "project"
    write_tdcg_state(project, "GREEN", build_valid_plan(), build_config_with_free_files(["**"]))
    with pytest.raises(OutsideProjectError):
        ensure_edit_allowed(project, tmp_path / "notes.md")


# everything else follows today's rules
def test_a_file_not_listed_follows_the_cycle(tmp_path):
    config = build_config_with_free_files(FREE_FILES)
    write_tdcg_state(tmp_path, "GREEN", build_valid_plan(), config)
    with pytest.raises(FileNotInCycleError):
        ensure_edit_allowed(tmp_path, tmp_path / SOURCE_NOT_IN_CYCLE)


def test_a_folder_name_alone_covers_nothing(tmp_path):
    config = build_config_with_free_files(["notes"])
    write_tdcg_state(tmp_path, "SPECIFY", build_valid_plan(), config)
    with pytest.raises(PhaseBlocksEditError):
        ensure_edit_allowed(tmp_path, tmp_path / FREE_FILE_IN_A_FOLDER)


# no config, or a broken one
def test_without_a_config_nothing_is_free_and_the_phase_answers(tmp_path):
    """Just after /claudio:init there is no config: a "no config" error would only confuse."""
    write_tdcg_text(tmp_path, PHASE_FILE, "PLAN")
    with pytest.raises(PhaseBlocksEditError):
        ensure_edit_allowed(tmp_path, tmp_path / FREE_FILE)


def test_a_broken_free_list_says_so(tmp_path):
    config = build_config_with_free_files(PATTERN_NOT_IN_A_LIST)
    write_tdcg_state(tmp_path, "SPECIFY", build_valid_plan(), config)
    with pytest.raises(BrokenConfigError, match=FREE_FILES_FIELD):
        ensure_edit_allowed(tmp_path, tmp_path / FREE_FILE)


def test_a_broken_config_can_still_be_fixed_in_plan(tmp_path):
    config = build_config_with_free_files(PATTERN_NOT_IN_A_LIST)
    write_tdcg_state(tmp_path, "PLAN", build_valid_plan(), config)
    ensure_edit_allowed(tmp_path, tmp_path / ".tdcg" / CONFIG_FILE)
