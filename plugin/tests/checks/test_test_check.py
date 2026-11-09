import pytest

from tdcg.checks.test_check import ensure_tests_as_expected
from tdcg.core.errors import (
    CoverageTestsShouldHavePassedError,
    NoConfigError,
    TestsShouldHaveFailedError,
    TestsShouldHavePassedError,
)
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.phase import Phase
from tests.support.constants import (
    ALL_CYCLE_TYPES,
    CONFIG_FILE,
    COVERAGE_TESTS_SHOULD_HAVE_PASSED,
    PHASES_WITH_NO_TEST_RUN,
    PHASES_WITH_PASSING_TESTS,
    TESTS_SHOULD_HAVE_FAILED,
    TESTS_SHOULD_HAVE_PASSED_BY_PHASE,
)
from tests.support.sample_commands import (
    FAILING,
    FAILING_AFTER_PASSING,
    FAILING_WITH_CODE_3,
    LEAVES_A_MARKER,
    LOUD_FAILING,
    MARKER,
    NOT_FOUND,
    PASSES_IF_MARKER_IS_HERE,
    PASSING,
)
from tests.support.sample_configs import build_config_with_test_command
from tests.support.tdcg_files import write_tdcg_json


# phases that run nothing
@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
@pytest.mark.parametrize("phase", PHASES_WITH_NO_TEST_RUN)
def test_leaving_a_phase_without_tests_runs_nothing(tmp_path, word, phase):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(LEAVES_A_MARKER))
    ensure_tests_as_expected(tmp_path, Phase(phase), CycleType(word))
    assert not (tmp_path / MARKER).exists()


@pytest.mark.parametrize("phase", PHASES_WITH_NO_TEST_RUN)
def test_leaving_a_phase_without_tests_needs_no_config(tmp_path, phase):
    ensure_tests_as_expected(tmp_path, Phase(phase), CycleType.BEHAVIOUR)


# RED
@pytest.mark.parametrize("command", [FAILING, FAILING_WITH_CODE_3, NOT_FOUND])
def test_behaviour_red_with_failing_tests_is_fine(tmp_path, command):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(command))
    ensure_tests_as_expected(tmp_path, Phase.RED, CycleType.BEHAVIOUR)


def test_behaviour_red_with_passing_tests_should_have_failed(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(PASSING))
    with pytest.raises(TestsShouldHaveFailedError) as error:
        ensure_tests_as_expected(tmp_path, Phase.RED, CycleType.BEHAVIOUR)
    assert str(error.value) == TESTS_SHOULD_HAVE_FAILED


def test_coverage_red_with_passing_tests_is_fine(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(PASSING))
    ensure_tests_as_expected(tmp_path, Phase.RED, CycleType.COVERAGE)


def test_coverage_red_with_failing_tests_should_have_passed(tmp_path):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(FAILING))
    with pytest.raises(CoverageTestsShouldHavePassedError) as error:
        ensure_tests_as_expected(tmp_path, Phase.RED, CycleType.COVERAGE)
    assert str(error.value) == COVERAGE_TESTS_SHOULD_HAVE_PASSED


# GREEN and REFACTOR
@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
@pytest.mark.parametrize("phase", PHASES_WITH_PASSING_TESTS)
def test_green_or_refactor_with_passing_tests_is_fine(tmp_path, word, phase):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(PASSING))
    ensure_tests_as_expected(tmp_path, Phase(phase), CycleType(word))


@pytest.mark.parametrize("word", ALL_CYCLE_TYPES)
@pytest.mark.parametrize("phase", PHASES_WITH_PASSING_TESTS)
@pytest.mark.parametrize("command", [FAILING, FAILING_WITH_CODE_3, NOT_FOUND])
def test_green_or_refactor_with_failing_tests_should_have_passed(tmp_path, word, phase, command):
    """The full text also proves the message names no command and no exit code."""
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(command))
    with pytest.raises(TestsShouldHavePassedError) as error:
        ensure_tests_as_expected(tmp_path, Phase(phase), CycleType(word))
    assert str(error.value) == TESTS_SHOULD_HAVE_PASSED_BY_PHASE[phase]


# how the command runs
def test_the_command_runs_through_the_shell(tmp_path):
    """`&&` works as typed: the last part fails, so the whole command fails."""
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(FAILING_AFTER_PASSING))
    with pytest.raises(TestsShouldHavePassedError):
        ensure_tests_as_expected(tmp_path, Phase.GREEN, CycleType.BEHAVIOUR)


def test_the_command_runs_in_the_project_folder(tmp_path):
    (tmp_path / MARKER).touch()
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(PASSES_IF_MARKER_IS_HERE))
    ensure_tests_as_expected(tmp_path, Phase.GREEN, CycleType.BEHAVIOUR)


def test_the_command_output_is_not_shown(tmp_path, capfd):
    write_tdcg_json(tmp_path, CONFIG_FILE, build_config_with_test_command(LOUD_FAILING))
    with pytest.raises(TestsShouldHavePassedError) as error:
        ensure_tests_as_expected(tmp_path, Phase.GREEN, CycleType.BEHAVIOUR)
    shown = capfd.readouterr()
    assert shown.out == ""
    assert shown.err == ""
    assert str(error.value) == TESTS_SHOULD_HAVE_PASSED_BY_PHASE["GREEN"]


def test_a_phase_with_tests_needs_the_config(tmp_path):
    with pytest.raises(NoConfigError):
        ensure_tests_as_expected(tmp_path, Phase.GREEN, CycleType.BEHAVIOUR)
