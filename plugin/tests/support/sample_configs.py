from tests.support.constants import FREE_FILES_FIELD


def build_valid_config():
    """A config with one test command and two test file patterns."""
    return {
        "test_command": "python3 -m pytest",
        "test_files": ["tests/**", "src/test/**"],
    }


def build_config_with_field_set_to(field, value):
    config = build_valid_config()
    config[field] = value
    return config


def build_config_with_schema_link():
    return build_config_with_field_set_to("$schema", "./config.schema.json")


def build_config_without_field(field):
    config = build_valid_config()
    del config[field]
    return config


def build_config_with_free_files(patterns):
    return build_config_with_field_set_to(FREE_FILES_FIELD, patterns)


def build_config_with_test_command(command):
    return build_config_with_field_set_to("test_command", command)
