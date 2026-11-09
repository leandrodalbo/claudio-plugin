import re
import shlex
from itertools import groupby
from pathlib import PurePosixPath

from tdcg.core.constants import (
    COMMAND_BREAKS,
    GIT_NAMES,
    GIT_OPTIONS_WITH_VALUE,
    GIT_OUTPUT_OPTION,
    GIT_READ_COMMANDS,
    GIT_VERSION_AND_HELP_OPTIONS,
    NO_COMMENT_CHARS,
    OPTION_START,
    OPTION_VALUE_SIGN,
    QUOTES_AND_BACKSLASHES,
    SHELL_OPERATOR_CHARS,
    WORD,
    WORD_PIECE,
)
from tdcg.core.errors import GitNoSubcommandError, GitOutputBlockedError, GitWriteBlockedError


def ensure_git_allowed(command: str) -> None:
    """Returns when every git call in the command only reads; raises naming the first that writes.
    Quoted text is checked as a command too, so git hidden in `bash -c '…'` or `"$( )"` is found."""
    for words in _split_into_commands(command):
        pieces = _split_at_list_marks(words)
        _ensure_every_git_call_only_reads(pieces)
        _ensure_quoted_text_only_reads(words)


# Splitting the text into commands and words

def _split_into_commands(command: str) -> list[list[str]]:
    """Each command's words, as the shell reads them. Text the shell rules can't read (an open
    quote, like `echo don't`) gets the rough split instead."""
    try:
        words = _split_like_the_shell(command)
    except ValueError:
        return _split_roughly(command)
    return _group_by_command(words)


def _split_like_the_shell(command: str) -> list[str]:
    """Quotes and backslashes are dropped ("g"it → git), but a quoted value stays one word.
    `#` is read as a plain character, so a git call in a comment is checked too."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=SHELL_OPERATOR_CHARS)
    lexer.whitespace_split = True
    lexer.commenters = NO_COMMENT_CHARS
    return list(lexer)


def _group_by_command(words: list[str]) -> list[list[str]]:
    """The runs of words between operators: each run is one command."""
    commands = []
    for is_operator, run in groupby(words, key=_is_operator):
        if not is_operator:
            commands.append(list(run))
    return commands


def _split_roughly(command: str) -> list[list[str]]:
    commands = []
    for part in re.split(COMMAND_BREAKS, command):
        plain_part = re.sub(QUOTES_AND_BACKSLASHES, "", part)
        commands.append(re.findall(WORD, plain_part))
    return commands


def _split_at_list_marks(words: list[str]) -> list[str]:
    """`['git', 'commit']` gives git and commit. An empty word stays as it is: in
    `git -C "" commit` it is -C's value, so `commit` is not."""
    pieces = []
    for word in words:
        pieces.extend(re.findall(WORD_PIECE, word) or [word])
    return pieces


# The rules: each helper returns quietly or raises

def _ensure_quoted_text_only_reads(words: list[str]) -> None:
    """A word with a space in it was quoted text, maybe a command of its own: check it too."""
    for word in words:
        if any(char.isspace() for char in word):
            ensure_git_allowed(word)


def _ensure_every_git_call_only_reads(words: list[str]) -> None:
    for position, word in enumerate(words):
        if _is_git(word):
            arguments = words[position + 1:]
            _ensure_git_call_only_reads(arguments)


def _ensure_git_call_only_reads(arguments: list[str]) -> None:
    subcommand, options = _split_off_subcommand(arguments)
    if subcommand is None:
        _ensure_only_version_or_help(arguments)
        return
    _ensure_read_command(subcommand)
    _ensure_no_output_option(subcommand, options)


def _ensure_only_version_or_help(options: list[str]) -> None:
    """git with no subcommand could get one when it runs (`echo commit | xargs git`), unless it
    only prints its version or help and stops."""
    if not any(option in GIT_VERSION_AND_HELP_OPTIONS for option in options):
        raise GitNoSubcommandError()


def _ensure_read_command(subcommand: str) -> None:
    if subcommand not in GIT_READ_COMMANDS:
        raise GitWriteBlockedError(subcommand, GIT_READ_COMMANDS)


def _ensure_no_output_option(subcommand: str, options: list[str]) -> None:
    """`--output` makes even a read command write a file."""
    if any(_is_output_option(option) for option in options):
        raise GitOutputBlockedError(subcommand, GIT_OUTPUT_OPTION)


# Finding things in the words

def _split_off_subcommand(arguments: list[str]) -> tuple[str | None, list[str]]:
    """The first word after git that is not an option or an option's value, and the words after
    it. No subcommand: (None, [])."""
    words = iter(arguments)
    for word in words:
        if not word.startswith(OPTION_START):
            return word, list(words)
        if word in GIT_OPTIONS_WITH_VALUE:
            next(words, None)  # `-C ../other`: skip the option's value too
    return None, []


# Naming each condition

def _is_operator(word: str) -> bool:
    """`;`, `&&`, `|`, `(` and the like: made only of operator characters. An empty quoted word
    (`git -C "" commit`) is a word, not an operator."""
    if not word:
        return False
    return not word.strip(SHELL_OPERATOR_CHARS)


def _is_git(word: str) -> bool:
    """`git`, git by its full path (`/usr/bin/git`), or Windows `git.exe`, in any letter case."""
    program = PurePosixPath(word).name.lower()
    return program in GIT_NAMES


def _is_output_option(word: str) -> bool:
    """`--output file` or `--output=file`."""
    return word == GIT_OUTPUT_OPTION or word.startswith(GIT_OUTPUT_OPTION + OPTION_VALUE_SIGN)
