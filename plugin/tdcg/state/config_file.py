"""Quick read of the config for the hooks: plain json, no schema. Full check: config_check.py."""

from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import (
    CLAUDE_FREE_WRITING_FILES,
    CONFIG_FILE,
    SCHEMA_FIELD,
    TDCG_DIR,
    TEST_FILES,
)
from tdcg.core.errors import BrokenConfigError, NoConfigError
from tdcg.domain.config import Config
from tdcg.state.json.field_types import describe_wrong_type, is_list_of_text
from tdcg.state.json.json_file import load_json_object


def read_config(project: Path) -> Config:
    path = build_config_path(project)
    if not path.exists():
        raise NoConfigError(path)
    return _build_config(load_json_object(path, BrokenConfigError), path)


def read_free_files(project: Path) -> list[str]:
    """The patterns of the files Claude may change in any phase. No config means nothing is free:
    just after /claudio:init the config is still to be written."""
    try:
        return read_config(project).claude_free_writing_files
    except NoConfigError:
        return []


def build_config_path(project: Path) -> Path:
    return project / TDCG_DIR / CONFIG_FILE


def _build_config(data: dict, path: Path) -> Config:
    """`$schema` only points editors to the schema; it is not a setting. A missing or unknown
    field is named by the dataclass's own TypeError."""
    data.pop(SCHEMA_FIELD, None)
    try:
        config = Config(**data)
    except TypeError as error:
        raise BrokenConfigError([str(error)], path) from error
    _ensure_list_of_text(TEST_FILES, config.test_files, path)
    _ensure_list_of_text(CLAUDE_FREE_WRITING_FILES, config.claude_free_writing_files, path)
    return config


def _ensure_list_of_text(field: str, value: object, path: Path) -> None:
    """Text in place of a list would be read letter by letter, and "*" matches every file."""
    if not is_list_of_text(value):
        problem = describe_wrong_type(field, messages.LIST_OF_TEXT, value)
        raise BrokenConfigError([problem], path)
