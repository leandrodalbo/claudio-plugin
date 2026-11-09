"""Full check of the config, run by /claudio:next and /claudio:back. Loads jsonschema, so the
guards and the where-we-are hook never import this."""

from pathlib import Path

from tdcg.core.constants import CONFIG_SCHEMA_FILE
from tdcg.core.errors import InvalidConfigError, NoConfigError
from tdcg.state.config_file import build_config_path
from tdcg.state.json.json_file import load_json
from tdcg.state.json.schema_check import ensure_matches_schema, load_schema_validator

_VALIDATOR = load_schema_validator(CONFIG_SCHEMA_FILE)


def ensure_config_valid(project: Path) -> None:
    path = build_config_path(project)
    if not path.exists():
        raise NoConfigError(path)
    data = load_json(path, InvalidConfigError)
    ensure_matches_schema(data, _VALIDATOR, path, InvalidConfigError)
