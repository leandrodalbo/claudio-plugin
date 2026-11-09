"""Reading the claudio skill as Claude Code does: SKILL.md with its frontmatter, and the files it
links."""

import re

from tests.support.hook_processes import PLUGIN_DIR

SKILL_DIR = PLUGIN_DIR / "skills" / "claudio"
SKILL_FILE = SKILL_DIR / "SKILL.md"
FRONTMATTER_LINE = "---"
# A Markdown link to a .md file: [text](path.md)
MARKDOWN_LINK = re.compile(r"\]\(([^)#\s]+\.md)\)")


def build_phase_rules_path(phase):
    return SKILL_DIR / "phases" / f"{phase.lower()}.md"


def load_skill_file(name):
    return (SKILL_DIR / name).read_text(encoding="utf-8")


def load_frontmatter(file=SKILL_FILE):
    """The `key: value` lines between the two --- lines at the top of the file. Read by hand: the
    standard library has no YAML reader, and our files keep each field on one line."""
    lines = file.read_text(encoding="utf-8").splitlines()
    end = lines.index(FRONTMATTER_LINE, 1)
    fields = {}
    for line in lines[1:end]:
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def find_files_linked_from_skill():
    return set(MARKDOWN_LINK.findall(SKILL_FILE.read_text(encoding="utf-8")))


def find_skill_files():
    """Every .md file in the skill folder besides SKILL.md, as a path from the folder."""
    files = set()
    for path in SKILL_DIR.rglob("*.md"):
        if path != SKILL_FILE:
            files.add(path.relative_to(SKILL_DIR).as_posix())
    return files


def has_heading(text, title):
    return re.search(rf"^#+ {re.escape(title)}$", text, re.MULTILINE) is not None
