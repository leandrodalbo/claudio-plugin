import pytest

from tdcg.core.errors import (
    GitNoSubcommandError,
    GitOutputBlockedError,
    GitWriteBlockedError,
    TdcgError,
)
from tdcg.guards.git_guard import ensure_git_allowed
from tests.support.constants import GIT_READ_COMMANDS, GIT_WRITE_COMMANDS


# read commands are allowed
@pytest.mark.parametrize("subcommand", GIT_READ_COMMANDS)
def test_read_command_is_allowed(subcommand):
    ensure_git_allowed(f"git {subcommand}")


@pytest.mark.parametrize(
    "command",
    [
        "git log --oneline -5",
        "git diff HEAD~1 -- tdcg/",
        "git show HEAD:README.md",
        "git blame -L 1,10 tdcg/core/errors.py",
        "git ls-files --others --exclude-standard",
        "git -C ../other status",
        "git --no-pager log",
        "git -c color.ui=never diff",
        "/usr/bin/git status",
        "git status && git diff",
        "git diff --stat | head -20",
    ],
)
def test_read_command_with_options_is_allowed(command):
    ensure_git_allowed(command)


@pytest.mark.parametrize("command", ["git --version", "git -v", "git --help", "git -h"])
def test_git_version_and_help_are_allowed(command):
    ensure_git_allowed(command)


# git with no subcommand could get one when it runs (from xargs)
@pytest.mark.parametrize(
    "command",
    [
        "git",
        "git -C ../other",
        "echo commit | xargs git",
        "printf push | xargs git --no-pager",
    ],
)
def test_git_without_a_subcommand_is_blocked(command):
    with pytest.raises(GitNoSubcommandError):
        ensure_git_allowed(command)


def test_no_subcommand_message_says_what_to_do():
    with pytest.raises(GitNoSubcommandError) as error:
        ensure_git_allowed("echo commit | xargs git")
    assert str(error.value) == (
        "git with no subcommand is blocked: it could get one when it runs (e.g. from xargs). "
        "Name the subcommand, e.g. git status."
    )


# global options that take a value
def test_attr_source_value_does_not_hide_the_subcommand():
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed("git --attr-source status commit")


@pytest.mark.parametrize(
    "command", ["git --attr-source HEAD log", "git --config-env x.y=Z status"]
)
def test_global_option_value_before_a_read_command_is_allowed(command):
    ensure_git_allowed(command)


# git under another name: git.exe (Windows git from WSL), any letter case (macOS)
@pytest.mark.parametrize(
    "command",
    [
        "git.exe commit",
        "GIT commit",
        "Git push",
        "'/mnt/c/Program Files/Git/bin/git.exe' push",
    ],
)
def test_git_under_another_name_is_blocked(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


@pytest.mark.parametrize("command", ["git.exe status", "GIT log", "ls git.exe.notes"])
def test_git_under_another_name_reading_is_allowed(command):
    ensure_git_allowed(command)


# commands that are not git are not our business
@pytest.mark.parametrize(
    "command",
    [
        "ls -la",
        "python3 -m pytest",
        "cat .gitignore",
        "ls ~/git/project",
        "ls git-notes",
        "grep -rn 'git log' docs",
        "",
    ],
)
def test_command_without_git_writes_is_allowed(command):
    ensure_git_allowed(command)


# every other git command is blocked
@pytest.mark.parametrize("subcommand", GIT_WRITE_COMMANDS)
def test_write_command_is_blocked(subcommand):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(f"git {subcommand}")


@pytest.mark.parametrize(
    "command",
    [
        "git commit -m 'add guard'",
        "git push origin main",
        "git reset --hard HEAD~1",
    ],
)
def test_write_command_with_arguments_is_blocked(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


# options before the subcommand don't hide it
@pytest.mark.parametrize(
    "command",
    [
        "git -C ../other commit",
        "git --no-pager push",
        "git -c user.name=x commit",
        "git --git-dir=.git reset",
        "git --work-tree . --git-dir .git checkout main",
        "/usr/bin/git commit",
        "GIT_DIR=.git git commit",
    ],
)
def test_options_before_the_subcommand_do_not_hide_it(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


# every git call in the command is checked
@pytest.mark.parametrize(
    "command",
    [
        "git status && git commit",
        "git status; git push",
        "ls || git reset --hard",
        "git log | git am",
        "git status & git stash",
        "git status\ngit commit",
        "(git commit)",
        "{ git commit; }",
    ],
)
def test_every_git_call_is_checked(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


# git run through another command
@pytest.mark.parametrize(
    "command",
    [
        "bash -c 'git commit'",
        'sh -c "git push"',
        "eval 'git reset --hard'",
        "echo $(git stash)",
        "echo `git commit`",
        'echo "$(git checkout main)"',
        "env git commit",
        "command git commit",
        "exec git commit",
        "sudo git commit",
        "nohup git push",
        "time git commit",
        "xargs git add",
        "find . -name '*.py' -exec git add {} ;",
        "echo git commit | bash",
        "bash <<EOF\ngit commit\nEOF",
        "python3 -c \"import subprocess; subprocess.run(['git', 'commit'])\"",
    ],
)
def test_git_run_through_another_command_is_blocked(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


# quotes and backslashes inside a word don't hide it: the shell drops them
@pytest.mark.parametrize(
    "command",
    [
        '"g"it commit',
        "'gi't commit",
        "g\\it commit",
        'git "com"mit',
        "git co\\mmit",
        "/usr/bin/'git' push",
    ],
)
def test_quotes_and_backslashes_inside_a_word_do_not_hide_it(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


@pytest.mark.parametrize("command", ['"g"it status', "g\\it log", "git \"di\"ff"])
def test_read_command_with_quotes_inside_a_word_is_allowed(command):
    ensure_git_allowed(command)


# a quoted option value is one word, as the shell sees it
@pytest.mark.parametrize(
    "command",
    [
        'git -c "user.name=1 status" commit -m x',
        "git -c 'a.b=1 log' push",
        'git -C "x status" commit',
    ],
)
def test_read_command_name_inside_a_quoted_value_does_not_hide_the_subcommand(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


@pytest.mark.parametrize(
    "command",
    [
        'git -C "my dir" status',
        "git -C 'my dir' diff",
        'git -c "user.name=A B" log',
    ],
)
def test_quoted_value_with_a_space_is_allowed_before_a_read_command(command):
    ensure_git_allowed(command)


# `#` only starts a comment at the start of a word, as in the shell
@pytest.mark.parametrize(
    "command",
    [
        "git log --format=#%h; git commit",
        "git log --pretty=a#b && git push",
    ],
)
def test_hash_inside_a_word_does_not_hide_the_rest(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


def test_git_write_in_a_comment_is_blocked_too():
    """Harmless to block: Claude can leave the comment out."""
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed("git status # git commit")


# an empty quoted word is a word, not a break between commands
@pytest.mark.parametrize("command", ['git -C "" commit', "git -C '' push", 'git "" -C x commit'])
def test_empty_quoted_word_does_not_cut_the_command(command):
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed(command)


def test_empty_quoted_value_before_a_read_command_is_allowed():
    ensure_git_allowed('git -C "" status')


# text the shell can't split (an open quote) is still checked
def test_open_quote_does_not_hide_a_write_command():
    with pytest.raises(GitWriteBlockedError):
        ensure_git_allowed("echo don't && git commit")


def test_open_quote_before_a_read_command_is_allowed():
    ensure_git_allowed("echo don't && git status")


# --output writes a file, even on a read command
@pytest.mark.parametrize(
    "command",
    [
        "git diff --output=changes.patch",
        "git log --output changes.txt",
        "git show --output=x HEAD",
        "git status && git diff --output=changes.patch",
    ],
)
def test_output_option_is_blocked(command):
    with pytest.raises(GitOutputBlockedError):
        ensure_git_allowed(command)


# messages
def test_write_block_message_names_the_command_and_what_to_do():
    with pytest.raises(GitWriteBlockedError) as error:
        ensure_git_allowed("git commit -m 'x'")
    assert str(error.value) == (
        "git commit is blocked: Claudio keeps git read-only "
        "(status, diff, log, show, blame, ls-files). Run it yourself."
    )


def test_write_block_message_names_the_blocked_call_not_the_first_one():
    with pytest.raises(GitWriteBlockedError) as error:
        ensure_git_allowed("git status && git push")
    assert str(error.value).startswith("git push is blocked")


def test_output_block_message_says_what_to_do():
    with pytest.raises(GitOutputBlockedError) as error:
        ensure_git_allowed("git diff --output=changes.patch")
    assert str(error.value) == (
        "git diff --output is blocked: it writes a file, and Claudio keeps git read-only. "
        "Run it without --output."
    )


@pytest.mark.parametrize(
    "error", [GitWriteBlockedError, GitOutputBlockedError, GitNoSubcommandError]
)
def test_git_errors_are_claudio_errors(error):
    assert issubclass(error, TdcgError)
