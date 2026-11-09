"""Commands any POSIX shell runs. The test check only reads the exit code, so these stand in for
a project's tests."""

PASSING = "true"
FAILING = "false"
FAILING_WITH_CODE_3 = "exit 3"
NOT_FOUND = "no-such-command-claudio"
FAILING_AFTER_PASSING = "true && false"
LOUD_FAILING = "echo hello-from-the-tests; echo oops-on-stderr >&2; false"
MARKER = "ran"
LEAVES_A_MARKER = f"touch {MARKER}"
PASSES_IF_MARKER_IS_HERE = f"test -f {MARKER}"
