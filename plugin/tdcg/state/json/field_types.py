"""Type checks for the few fields the guards use, so the quick reads don't need jsonschema.
Python can't check "a list of text" by itself (`isinstance(value, list[str])` raises)."""

import json

from tdcg.core import messages


def is_list_of_text(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def describe_wrong_type(field: str, expected: str, value: object) -> str:
    """The value as JSON, as the user wrote it (null, not None)."""
    return messages.WRONG_TYPE.format(field=field, expected=expected, value=json.dumps(value))
