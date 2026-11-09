# Claude Code Instructions: Claudio

Claudio is built with Claudio: work follows TDCG cycles, one phase at a time.

## Code style (plugin, Python)

**The rules live in the claudio skill: `plugin/skills/claudio/` (craft/, phases/,
working-together.md). Read them before GREEN and write to them from the first version, not only in
REFACTOR** (user, 2026-11-05). A new correction goes there (2026-11-07); only Python-specific
details go here.

Python specifics:
- Folders by area:
  - `tdcg/core/` = shared pieces: `constants.py` (every fixed value), `messages.py` (every text
    for people, `str.format` templates), `errors.py` (every error; all inherit `TdcgError`, each
    fills in its message from `messages.py`).
  - `tdcg/domain/` = types (enums, data classes), one module per type. Phase order = order of the
    `Phase` enum in `domain/phase.py`.
  - `tdcg/state/` = reading and writing `.tdcg/` files. `state/json/` = shared JSON reading.
  - `tdcg/schema/` = the JSON schemas.
  - `tdcg/guards/` = the rules (allow or raise), no Claude Code details.
  - `tdcg/hooks/` = thin glue between Claude Code's hook JSON and the guards.
  - `tdcg/checks/` = runs the user's test command (3.5).
  - `tdcg/context/` = what Claude is told before each message (3.6).
  - `tdcg/commands/` = what each `/claudio:` command does (3.7).
  - `tdcg/core/plugin_folder.py` = where the plugin and the skill are, found from the package.
- Dependencies point inward: `hooks` → `commands` → `guards`/`checks` → `state` → `domain`/`core`.
- Private helpers start with `_`.
- Tests: pytest, one `test_<module>.py` per module, mirroring the folders (`tests/state/`). Run
  from `plugin/`: `python3 -m pytest`. Shared helpers in `tests/support/`; test values in
  `tests/support/constants.py`, never imported from `tdcg/core/constants.py`.
