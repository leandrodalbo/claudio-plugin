"""Full check of the plan, run by /claudio:next and /claudio:back. Loads jsonschema, so the
guards and the where-we-are hook never import this."""

from collections import Counter
from pathlib import Path

from tdcg.core.constants import CYCLES, KEY, PLAN_SCHEMA_FILE
from tdcg.core.errors import DuplicateCycleError, InvalidPlanError, NoPlanError
from tdcg.state.json.json_file import load_json
from tdcg.state.json.schema_check import ensure_matches_schema, load_schema_validator
from tdcg.state.plan_file import build_plan_path

_VALIDATOR = load_schema_validator(PLAN_SCHEMA_FILE)


def ensure_plan_valid(project: Path) -> None:
    path = build_plan_path(project)
    if not path.exists():
        raise NoPlanError(path)
    data = load_json(path, InvalidPlanError)
    ensure_matches_schema(data, _VALIDATOR, path, InvalidPlanError)
    _ensure_unique_keys(data, path)


def _ensure_unique_keys(data: dict, path: Path) -> None:
    counts = Counter(cycle[KEY] for cycle in data[CYCLES])
    for key, count in counts.items():
        if count > 1:
            raise DuplicateCycleError(key, path)
