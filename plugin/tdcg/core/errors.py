"""Every error Claudio raises on purpose. Each fills in its own message from messages.py."""

from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import MAX_REASONS_SHOWN


class TdcgError(Exception):
    """Base for every error Claudio raises on purpose. Anything else is a bug."""


def _list_problems(problems: list[str]) -> str:
    lines = []
    for problem in problems:
        lines.append(messages.PROBLEM_LINE.format(problem=problem))
    return "\n".join(lines)


class UnknownPhaseError(TdcgError, ValueError):
    def __init__(self, word: str, path: Path):
        super().__init__(messages.UNKNOWN_PHASE.format(word=word, path=path))


class NotEarlierPhaseError(TdcgError, ValueError):
    def __init__(self, current: str, target: str):
        super().__init__(messages.NOT_EARLIER_PHASE.format(current=current, target=target))


class NotLaterPhaseError(TdcgError, ValueError):
    def __init__(self, current: str, target: str):
        super().__init__(messages.NOT_LATER_PHASE.format(current=current, target=target))


class PhaseNotInRouteError(TdcgError, ValueError):
    def __init__(self, phase: str, cycle_type: str):
        super().__init__(messages.PHASE_NOT_IN_ROUTE.format(phase=phase, cycle_type=cycle_type))


class PhaseNotSkippableError(TdcgError, ValueError):
    def __init__(self, phase: str, cycle_type: str):
        super().__init__(messages.PHASE_NOT_SKIPPABLE.format(phase=phase, cycle_type=cycle_type))


class NoPlanError(TdcgError, FileNotFoundError):
    def __init__(self, path: Path):
        super().__init__(messages.NO_PLAN.format(path=path))


class InvalidPlanError(TdcgError, ValueError):
    def __init__(self, problems: list[str], path: Path):
        super().__init__(messages.INVALID_PLAN.format(path=path, problems=_list_problems(problems)))


class BrokenPlanError(TdcgError, ValueError):
    def __init__(self, problems: list[str], path: Path):
        super().__init__(messages.BROKEN_PLAN.format(path=path, problems=_list_problems(problems)))


class NoCycleLeftError(TdcgError, ValueError):
    def __init__(self):
        super().__init__(messages.NO_CYCLE_LEFT)


class OutsideProjectError(TdcgError, PermissionError):
    def __init__(self, file: Path):
        super().__init__(messages.OUTSIDE_PROJECT.format(file=file))


class TdcgFolderLockedError(TdcgError, PermissionError):
    def __init__(self, file: Path):
        super().__init__(messages.TDCG_FOLDER_LOCKED.format(file=file))


class PhaseBlocksEditError(TdcgError, PermissionError):
    def __init__(self, phase: str, file: Path):
        super().__init__(messages.PHASE_BLOCKS_EDIT.format(phase=phase, file=file))


class NotATestFileError(TdcgError, PermissionError):
    def __init__(self, file: Path):
        super().__init__(messages.NOT_A_TEST_FILE.format(file=file))


class LockedTestFileError(TdcgError, PermissionError):
    def __init__(self, file: Path, phase: str):
        super().__init__(messages.LOCKED_TEST_FILE.format(file=file, phase=phase))


class FileNotInCycleError(TdcgError, PermissionError):
    def __init__(self, file: Path, key: str):
        super().__init__(messages.FILE_NOT_IN_CYCLE.format(file=file, key=key))


class GitWriteBlockedError(TdcgError, PermissionError):
    def __init__(self, subcommand: str, read_commands: tuple[str, ...]):
        super().__init__(
            messages.GIT_WRITE_BLOCKED.format(
                subcommand=subcommand, read_commands=", ".join(read_commands)
            )
        )


class GitOutputBlockedError(TdcgError, PermissionError):
    def __init__(self, subcommand: str, option: str):
        super().__init__(messages.GIT_OUTPUT_BLOCKED.format(subcommand=subcommand, option=option))


class GitNoSubcommandError(TdcgError, PermissionError):
    def __init__(self):
        super().__init__(messages.GIT_NO_SUBCOMMAND)


class NoConfigError(TdcgError, FileNotFoundError):
    def __init__(self, path: Path):
        super().__init__(messages.NO_CONFIG.format(path=path))


class InvalidConfigError(TdcgError, ValueError):
    def __init__(self, problems: list[str], path: Path):
        super().__init__(
            messages.INVALID_CONFIG.format(path=path, problems=_list_problems(problems))
        )


class BrokenConfigError(TdcgError, ValueError):
    def __init__(self, problems: list[str], path: Path):
        super().__init__(
            messages.BROKEN_CONFIG.format(path=path, problems=_list_problems(problems))
        )


class RepeatedFieldError(TdcgError, ValueError):
    def __init__(self, field: str, path: Path):
        super().__init__(messages.REPEATED_FIELD.format(field=field, path=path))


class DuplicateCycleError(TdcgError, ValueError):
    def __init__(self, key: str, path: Path):
        super().__init__(messages.DUPLICATE_CYCLE.format(key=key, path=path))


class CycleNotFoundError(TdcgError, ValueError):
    def __init__(self, key: str, path: Path):
        super().__init__(messages.CYCLE_NOT_FOUND.format(key=key, path=path))


class CycleAlreadyDoneError(TdcgError, ValueError):
    def __init__(self, key: str):
        super().__init__(messages.CYCLE_ALREADY_DONE.format(key=key))


class DonePlanExistsError(TdcgError, FileExistsError):
    def __init__(self, path: Path):
        super().__init__(messages.DONE_PLAN_EXISTS.format(path=path))


class NotAGitRepoError(TdcgError, ValueError):
    def __init__(self, project: Path):
        super().__init__(messages.NOT_A_GIT_REPO.format(project=project))


class ShellChangesBlockedError(TdcgError, PermissionError):
    """Shows the first MAX_REASONS_SHOWN reasons and counts the rest: no wall of text."""

    def __init__(self, reasons: list[str]):
        listed = _list_problems(reasons[:MAX_REASONS_SHOWN])
        hidden = len(reasons) - MAX_REASONS_SHOWN
        if hidden > 0:
            listed += "\n" + messages.MORE_PROBLEMS_LINE.format(hidden=hidden)
        super().__init__(messages.SHELL_CHANGES_BLOCKED.format(problems=listed))


class TdcgFolderRemovedError(TdcgError, PermissionError):
    def __init__(self):
        super().__init__(messages.TDCG_FOLDER_REMOVED)



class AlreadySetUpError(TdcgError):
    def __init__(self):
        super().__init__(messages.ALREADY_SET_UP)


class NotSetUpError(TdcgError):
    def __init__(self):
        super().__init__(messages.NOT_SET_UP)


class UnknownInstructionError(TdcgError):
    def __init__(self, words: str):
        super().__init__(messages.UNKNOWN_INSTRUCTION.format(words=words))


class TestsShouldHaveFailedError(TdcgError):
    __test__ = False  # the name starts with "Test": tells pytest this is not a test class

    def __init__(self):
        super().__init__(messages.TESTS_SHOULD_HAVE_FAILED)


class TestsShouldHavePassedError(TdcgError):
    __test__ = False  # the name starts with "Test": tells pytest this is not a test class

    def __init__(self, phase: str):
        super().__init__(messages.TESTS_SHOULD_HAVE_PASSED.format(phase=phase))


class CoverageTestsShouldHavePassedError(TdcgError):
    def __init__(self):
        super().__init__(messages.COVERAGE_TESTS_SHOULD_HAVE_PASSED)
