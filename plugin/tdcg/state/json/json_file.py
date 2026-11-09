import json
from collections.abc import Callable
from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import ENCODING
from tdcg.core.errors import RepeatedFieldError

InvalidFileError = Callable[[list[str], Path], Exception]


def load_json(path: Path, invalid_error: InvalidFileError) -> object:
    """Bad UTF-8 or bad JSON raises invalid_error; a repeated field raises RepeatedFieldError."""
    text = _load_text(path, invalid_error)
    try:
        return json.loads(
            text, object_pairs_hook=lambda pairs: _build_dict_rejecting_repeated_fields(pairs, path)
        )
    except json.JSONDecodeError as error:
        problem = messages.BAD_JSON.format(line=error.lineno, column=error.colno, reason=error.msg)
        raise invalid_error([problem], path) from error


def load_json_object(path: Path, invalid_error: InvalidFileError) -> dict:
    """As load_json; anything but a JSON object also raises invalid_error."""
    data = load_json(path, invalid_error)
    if not isinstance(data, dict):
        raise invalid_error([messages.NOT_A_JSON_OBJECT], path)
    return data


def _load_text(path: Path, invalid_error: InvalidFileError) -> str:
    try:
        return path.read_text(encoding=ENCODING)
    except UnicodeDecodeError as error:
        problem = messages.NOT_UTF8.format(reason=error.reason)
        raise invalid_error([problem], path) from error


def _build_dict_rejecting_repeated_fields(pairs: list[tuple[str, object]], path: Path) -> dict:
    seen = set()
    for field, _ in pairs:
        if field in seen:
            raise RepeatedFieldError(field, path)
        seen.add(field)
    return dict(pairs)
