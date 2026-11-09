from enum import Enum


class TestResult(Enum):
    """What the user's test command gave. Only the exit code counts, whatever the command runs."""

    __test__ = False  # the name starts with "Test": tells pytest this is not a test class

    PASS = "PASS"
    FAIL = "FAIL"

    @classmethod
    def from_exit_code(cls, code: int) -> "TestResult":
        """0 = PASS. Anything else is FAIL: a crash or a command not found counts too."""
        return cls.PASS if code == 0 else cls.FAIL
