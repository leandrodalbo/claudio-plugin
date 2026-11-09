"""The claudio skill holds all the knowledge Claude works with. These checks keep it complete and
in the shape Claude Code reads."""

import pytest

from tests.support.constants import (
    ALL_PHASES,
    DESIGN_PATTERNS,
    PHASE_FILE_SECTIONS,
    SIMPLICITY_PRINCIPLES,
    SKILL_FILES,
    SKILL_MAX_DESCRIPTION,
    SKILL_MAX_LINES,
    SKILL_NAME,
    SOLID_PRINCIPLES,
    TDD_BDD_XP_PRACTICES,
)
from tests.support.skill_files import (
    SKILL_FILE,
    build_phase_rules_path,
    find_files_linked_from_skill,
    find_skill_files,
    has_heading,
    load_frontmatter,
    load_skill_file,
)


# the shape Claude Code reads
def test_the_skill_is_named_claudio():
    assert load_frontmatter()["name"] == SKILL_NAME


def test_the_description_fits_what_claude_always_sees():
    """Claude Code cuts description + when_to_use at 1,536 characters."""
    fields = load_frontmatter()
    assert fields["description"]
    assert len(fields["description"] + fields.get("when_to_use", "")) <= SKILL_MAX_DESCRIPTION


def test_skill_md_stays_short():
    """Claude Code's advice: under 500 lines, details in linked files."""
    assert len(SKILL_FILE.read_text(encoding="utf-8").splitlines()) < SKILL_MAX_LINES


# every file is there and reachable
def test_the_skill_has_exactly_its_files():
    assert find_skill_files() == set(SKILL_FILES)


def test_skill_md_links_every_file():
    """Claude only finds a file that SKILL.md links."""
    assert find_files_linked_from_skill() == set(SKILL_FILES)


# phases
@pytest.mark.parametrize("phase", ALL_PHASES)
@pytest.mark.parametrize("section", PHASE_FILE_SECTIONS)
def test_each_phase_file_has_its_sections(phase, section):
    text = build_phase_rules_path(phase).read_text(encoding="utf-8")
    assert has_heading(text, section)


# nothing lost
@pytest.mark.parametrize("pattern", DESIGN_PATTERNS)
def test_every_design_pattern_is_in_the_patterns_file(pattern):
    assert has_heading(load_skill_file("craft/design-patterns.md"), pattern)


@pytest.mark.parametrize("principle", SOLID_PRINCIPLES)
def test_every_solid_principle_is_in_the_solid_file(principle):
    assert has_heading(load_skill_file("craft/solid.md"), principle)


@pytest.mark.parametrize("principle", SIMPLICITY_PRINCIPLES)
def test_every_simplicity_principle_is_in_its_file(principle):
    assert has_heading(load_skill_file("craft/simplicity.md"), principle)


@pytest.mark.parametrize("practice", TDD_BDD_XP_PRACTICES)
def test_tdd_bdd_and_xp_are_in_their_file(practice):
    assert has_heading(load_skill_file("craft/tdd-bdd-xp.md"), practice)
