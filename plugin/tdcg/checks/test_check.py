"""Runs the user's test command when a phase moves forward and checks the result fits the phase."""

import subprocess
from pathlib import Path

from tdcg.core.errors import (
    CoverageTestsShouldHavePassedError,
    TdcgError,
    TestsShouldHaveFailedError,
    TestsShouldHavePassedError,
)
from tdcg.domain.cycle_type import CycleType
from tdcg.domain.phase import Phase
from tdcg.domain.test_result import TestResult
from tdcg.state.config_file import read_config


def ensure_tests_as_expected(project: Path, phase: Phase, cycle_type: CycleType) -> None:
    """Called by /claudio:next before it moves on from `phase` (next or skip), only when the user
    types it: Claude never triggers it. Returns quietly when the phase runs no tests (the config
    isn't even read) or when the result fits; raises with what to do when it doesn't."""
    expected = cycle_type.expect_when_leaving(phase)
    if expected is None:
        return
    result = _run_test_command(project, read_config(project).test_command)
    if result is not expected:
        raise _build_mismatch_error(phase, expected)


def _run_test_command(project: Path, command: str) -> TestResult:
    """Through the shell, in the project folder: the user's own text, the same as typing it, so
    `&&` and scripts work. The output is dropped (the user runs the command for the details) and
    nothing waits for typing. No time limit: a hanging command is the user's to stop."""
    finished = subprocess.run(
        command,
        shell=True,
        cwd=project,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return TestResult.from_exit_code(finished.returncode)


def _build_mismatch_error(phase: Phase, expected: TestResult) -> TdcgError:
    """Only behaviour RED expects FAIL. Expecting PASS in RED means a coverage cycle."""
    if expected is TestResult.FAIL:
        return TestsShouldHaveFailedError()
    if phase is Phase.RED:
        return CoverageTestsShouldHavePassedError()
    return TestsShouldHavePassedError(phase.value)
