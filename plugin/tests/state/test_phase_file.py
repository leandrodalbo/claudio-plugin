import pytest

from tdcg.core.errors import (
    NotEarlierPhaseError,
    NotLaterPhaseError,
    PhaseNotInRouteError,
    PhaseNotSkippableError,
    UnknownPhaseError,
)
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.phase import Phase
from tdcg.state.phase_file import move_back_to, move_to_next_phase, read_phase, skip_to
from tests.support.constants import (
    ALL_CYCLE_TYPES,
    ALL_PHASES,
    OFF_IN_PHASE_FILE,
    PHASE_FILE,
    PHASES_WITHOUT_RED,
    TYPES_WITH_RED,
    TYPES_WITHOUT_RED,
)
from tests.support.tdcg_files import has_tdcg_path, load_tdcg_text, write_tdcg_text

BEHAVIOUR = CycleType("behaviour")


# read_phase
def test_missing_file_means_plan(tmp_path):
    assert read_phase(tmp_path) == Phase.PLAN


@pytest.mark.parametrize("word", ALL_PHASES)
def test_reads_each_phase(tmp_path, word):
    write_tdcg_text(tmp_path, PHASE_FILE, word)
    assert read_phase(tmp_path).value == word


def test_ignores_spaces_and_new_line(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "  GREEN\n")
    assert read_phase(tmp_path) == Phase.GREEN


def test_unknown_word_is_an_error(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "BANANA")
    with pytest.raises(UnknownPhaseError, match="BANANA"):
        read_phase(tmp_path)


# move_to_next_phase
@pytest.mark.parametrize("cycle_type", TYPES_WITH_RED)
@pytest.mark.parametrize("current, expected", list(zip(ALL_PHASES, ALL_PHASES[1:])))
def test_next_follows_the_full_route(tmp_path, cycle_type, current, expected):
    write_tdcg_text(tmp_path, PHASE_FILE, current)
    assert move_to_next_phase(tmp_path, CycleType(cycle_type)).value == expected
    assert load_tdcg_text(tmp_path, PHASE_FILE) == expected


@pytest.mark.parametrize("cycle_type", TYPES_WITHOUT_RED)
@pytest.mark.parametrize(
    "current, expected", list(zip(PHASES_WITHOUT_RED, PHASES_WITHOUT_RED[1:]))
)
def test_next_follows_the_route_without_red(tmp_path, cycle_type, current, expected):
    write_tdcg_text(tmp_path, PHASE_FILE, current)
    assert move_to_next_phase(tmp_path, CycleType(cycle_type)).value == expected
    assert load_tdcg_text(tmp_path, PHASE_FILE) == expected


@pytest.mark.parametrize("cycle_type", ALL_CYCLE_TYPES)
def test_next_from_commit_goes_to_specify(tmp_path, cycle_type):
    write_tdcg_text(tmp_path, PHASE_FILE, "COMMIT")
    assert move_to_next_phase(tmp_path, CycleType(cycle_type)) == Phase.SPECIFY
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


def test_next_without_file_creates_it_at_specify(tmp_path):
    assert move_to_next_phase(tmp_path, BEHAVIOUR) == Phase.SPECIFY
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


@pytest.mark.parametrize("cycle_type", TYPES_WITHOUT_RED)
def test_next_from_a_phase_not_on_the_route_is_an_error(tmp_path, cycle_type):
    """Can't happen through the tool (the plan only changes in PLAN), but must not crash."""
    write_tdcg_text(tmp_path, PHASE_FILE, "RED")
    with pytest.raises(PhaseNotInRouteError, match=cycle_type):
        move_to_next_phase(tmp_path, CycleType(cycle_type))
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "RED"


# move_back_to
def test_back_goes_to_an_earlier_phase(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    assert move_back_to(tmp_path, Phase.RED, BEHAVIOUR) == Phase.RED
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "RED"


@pytest.mark.parametrize("cycle_type", ALL_CYCLE_TYPES)
def test_back_to_plan_works_for_every_type(tmp_path, cycle_type):
    write_tdcg_text(tmp_path, PHASE_FILE, "COMMIT")
    assert move_back_to(tmp_path, Phase.PLAN, CycleType(cycle_type)) == Phase.PLAN
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "PLAN"


@pytest.mark.parametrize("target", [Phase.GREEN, Phase.REVIEW])
def test_back_to_same_or_later_phase_is_an_error(tmp_path, target):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    with pytest.raises(NotEarlierPhaseError):
        move_back_to(tmp_path, target, BEHAVIOUR)
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "GREEN"


@pytest.mark.parametrize("cycle_type", TYPES_WITHOUT_RED)
def test_back_to_a_phase_not_on_the_route_is_an_error(tmp_path, cycle_type):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    with pytest.raises(PhaseNotInRouteError, match=cycle_type):
        move_back_to(tmp_path, Phase.RED, CycleType(cycle_type))
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "GREEN"


# skip_to
@pytest.mark.parametrize("cycle_type", ALL_CYCLE_TYPES)
@pytest.mark.parametrize(
    "current, target, skipped",
    [
        ("GREEN", Phase.COMMIT, [Phase.REVIEW, Phase.REFACTOR]),
        ("GREEN", Phase.REFACTOR, [Phase.REVIEW]),
        ("REVIEW", Phase.COMMIT, [Phase.REFACTOR]),
    ],
)
def test_skip_jumps_to_the_target_and_says_what_was_skipped(
    tmp_path, cycle_type, current, target, skipped
):
    write_tdcg_text(tmp_path, PHASE_FILE, current)
    assert skip_to(tmp_path, target, CycleType(cycle_type)) == skipped
    assert load_tdcg_text(tmp_path, PHASE_FILE) == target.value


def test_skip_to_the_next_phase_skips_nothing(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "REFACTOR")
    assert skip_to(tmp_path, Phase.COMMIT, BEHAVIOUR) == []
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "COMMIT"


@pytest.mark.parametrize(
    "cycle_type, current, target, not_skippable",
    [
        ("behaviour", "SPECIFY", Phase.PROMPT, "RED"),
        ("coverage", "SPECIFY", Phase.PROMPT, "RED"),
        ("behaviour", "PLAN", Phase.RED, "SPECIFY"),
        ("behaviour", "RED", Phase.GREEN, "PROMPT"),
        ("refactor", "PROMPT", Phase.REVIEW, "GREEN"),
        ("refactor", "SPECIFY", Phase.GREEN, "PROMPT"),
    ],
)
def test_skipping_a_phase_that_must_happen_is_an_error(
    tmp_path, cycle_type, current, target, not_skippable
):
    write_tdcg_text(tmp_path, PHASE_FILE, current)
    with pytest.raises(PhaseNotSkippableError, match=not_skippable):
        skip_to(tmp_path, target, CycleType(cycle_type))
    assert load_tdcg_text(tmp_path, PHASE_FILE) == current


@pytest.mark.parametrize(
    "current, target",
    [
        ("REVIEW", Phase.REVIEW),
        ("REVIEW", Phase.GREEN),
        ("REVIEW", Phase.PLAN),
        ("COMMIT", Phase.SPECIFY),
    ],
)
def test_skip_to_the_same_or_an_earlier_phase_is_an_error(tmp_path, current, target):
    write_tdcg_text(tmp_path, PHASE_FILE, current)
    with pytest.raises(NotLaterPhaseError):
        skip_to(tmp_path, target, BEHAVIOUR)
    assert load_tdcg_text(tmp_path, PHASE_FILE) == current


@pytest.mark.parametrize("cycle_type", TYPES_WITHOUT_RED)
def test_skip_to_a_phase_not_on_the_route_is_an_error(tmp_path, cycle_type):
    write_tdcg_text(tmp_path, PHASE_FILE, "SPECIFY")
    with pytest.raises(PhaseNotInRouteError, match=cycle_type):
        skip_to(tmp_path, Phase.RED, CycleType(cycle_type))
    assert load_tdcg_text(tmp_path, PHASE_FILE) == "SPECIFY"


# Claudio turned off after a bug comes back on when the phase moves
def test_next_turns_claudio_back_on(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    move_to_next_phase(tmp_path, BEHAVIOUR)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


def test_back_turns_claudio_back_on(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    move_back_to(tmp_path, Phase.RED, BEHAVIOUR)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


def test_skip_turns_claudio_back_on(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    skip_to(tmp_path, Phase.COMMIT, BEHAVIOUR)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


def test_back_to_a_later_phase_keeps_claudio_off(tmp_path):
    write_tdcg_text(tmp_path, PHASE_FILE, "GREEN")
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    with pytest.raises(NotEarlierPhaseError):
        move_back_to(tmp_path, Phase.REVIEW, BEHAVIOUR)
    assert has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)
