import json
from pathlib import Path

from jsonschema.exceptions import ValidationError
from jsonschema.protocols import Validator
from jsonschema.validators import validator_for

from tdcg.core import messages
from tdcg.core.constants import DESCRIPTION, ENCODING, RULES_EXPLAINED_IN_WORDS
from tdcg.core.plugin_folder import SCHEMA_FOLDER
from tdcg.state.json.json_file import InvalidFileError


def load_schema_validator(schema_file: str) -> Validator:
    schema = json.loads((SCHEMA_FOLDER / schema_file).read_text(encoding=ENCODING))
    return validator_for(schema)(schema)


def ensure_matches_schema(
    data: object, validator: Validator, path: Path, invalid_error: InvalidFileError
) -> None:
    """Raises invalid_error listing every problem, in words where the schema has them."""
    errors = sorted(validator.iter_errors(data), key=lambda error: error.json_path)
    if errors:
        raise invalid_error([_describe_in_words(error) for error in errors], path)


def _describe_in_words(error: ValidationError) -> str:
    description = error.schema.get(DESCRIPTION)
    if error.validator in RULES_EXPLAINED_IN_WORDS and description:
        return messages.SCHEMA_RULE_IN_WORDS.format(
            where=error.json_path, value=repr(error.instance), rule=description
        )
    return messages.SCHEMA_PROBLEM.format(where=error.json_path, problem=error.message)
