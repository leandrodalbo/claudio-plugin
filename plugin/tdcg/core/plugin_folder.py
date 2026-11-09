"""Where the plugin's own files are, found from this package: the same in a clone, an install
and the tests, with no setting to get wrong."""

from pathlib import Path

from tdcg.core.constants import (
    CLAUDIO_SKILL,
    MARKDOWN_EXTENSION,
    PHASES_DIR,
    SCHEMA_DIR,
    SKILLS_DIR,
)

# tdcg/core/plugin_folder.py → the tdcg/ package, and the plugin folder that holds it and skills/
_PACKAGE_FOLDER = Path(__file__).resolve().parents[1]
_PLUGIN_FOLDER = _PACKAGE_FOLDER.parent
SKILL_FOLDER = _PLUGIN_FOLDER / SKILLS_DIR / CLAUDIO_SKILL
SCHEMA_FOLDER = _PACKAGE_FOLDER / SCHEMA_DIR


def build_phase_rules_path(phase_name: str) -> Path:
    """Takes the phase's name, not the Phase type: core sits below domain."""
    return SKILL_FOLDER / PHASES_DIR / (phase_name.lower() + MARKDOWN_EXTENSION)
