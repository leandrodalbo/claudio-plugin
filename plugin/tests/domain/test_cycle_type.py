import pytest

from tdcg.core.errors import PhaseNotInRouteError
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.phase import Phase
from tdcg.domain.test_result import TestResult
from tests.support.constants import (
    ALL_CYCLE_TYPES,
    ALL_PHASES,
    FULL_ROUTE,
    PHASE_NOT_IN_ROUTE_BY_TYPE,
    PHASES_WITH_NO_TEST_RUN,
    PHASES_WITH_PASSING_TESTS,
    PHASES_WITHOUT_RED,
    ROUTE_WITHOUT_RED,
    TYPES_WITH_RED,
    TYPES_WITHOUT_RED,
)


@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
def test_each_type_is_read_from_its_word(word):
    assert CycleType(word).value == word


@pytest.mark.parametrize("word", TYPES_WITH_RED)
def test_types_with_red_have_the_full_route(word):
    assert [phase.value for phase in CycleType(word).route] == FULL_ROUTE


@pytest.mark.parametrize("word", TYPES_WITHOUT_RED)
def test_types_without_red_have_the_route_without_red(word):
    assert [phase.value for phase in CycleType(word).route] == ROUTE_WITHOUT_RED


# steps: PLAN, then the route
@pytest.mark.parametrize("word", TYPES_WITH_RED)
def test_types_with_red_walk_every_phase(word):
    assert [phase.value for phase in CycleType(word).steps] == ALL_PHASES


@pytest.mark.parametrize("word", TYPES_WITHOUT_RED)
def test_types_without_red_walk_every_phase_but_red(word):
    assert [phase.value for phase in CycleType(word).steps] == PHASES_WITHOUT_RED


# ensure_has_step
@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
@pytest.mark.parametrize("phase", PHASES_WITHOUT_RED)
def test_every_phase_but_red_is_a_step_of_every_type(word, phase):
    CycleType(word).ensure_has_step(Phase(phase))


@pytest.mark.parametrize("word", TYPES_WITH_RED)
def test_red_is_a_step_of_types_with_red(word):
    CycleType(word).ensure_has_step(Phase.RED)


@pytest.mark.parametrize("word", TYPES_WITHOUT_RED)
def test_red_is_not_a_step_of_types_without_red(word):
    with pytest.raises(PhaseNotInRouteError) as error:
        CycleType(word).ensure_has_step(Phase.RED)
    assert str(error.value) == PHASE_NOT_IN_ROUTE_BY_TYPE[word]


# expect_when_leaving
def test_leaving_red_in_a_behaviour_cycle_expects_failing_tests():
    assert CycleType.BEHAVIOUR.expect_when_leaving(Phase.RED) == TestResult.FAIL


def test_leaving_red_in_a_coverage_cycle_expects_passing_tests():
    assert CycleType.COVERAGE.expect_when_leaving(Phase.RED) == TestResult.PASS


@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
@pytest.mark.parametrize("phase", PHASES_WITH_PASSING_TESTS)
def test_leaving_green_or_refactor_expects_passing_tests(word, phase):
    assert CycleType(word).expect_when_leaving(Phase(phase)) == TestResult.PASS


@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
@pytest.mark.parametrize("phase", PHASES_WITH_NO_TEST_RUN)
def test_leaving_any_other_phase_runs_no_tests(word, phase):
    assert CycleType(word).expect_when_leaving(Phase(phase)) is None


@pytest.mark.parametrize("word", TYPES_WITHOUT_RED)
def test_leaving_red_in_a_type_without_red_is_an_error(word):
    """No silent None: the phase machine raises the same error for a phase off the route."""
    with pytest.raises(PhaseNotInRouteError) as error:
        CycleType(word).expect_when_leaving(Phase.RED)
    assert str(error.value) == PHASE_NOT_IN_ROUTE_BY_TYPE[word]
