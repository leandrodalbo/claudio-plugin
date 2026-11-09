# PLAN

## Goal

Agree with the user on a plan: what we build, why, and the small cycles that get there. No cycle
starts without a plan. You draft; the user approves with `/claudio:next`.

## What may change

Only `.tdcg/plan.json` and `.tdcg/config.json`, plus the config's `claude_free_writing_files`.
Nothing else, not even notes.

## Checklist

- **New project:** `/claudio:init` makes `.tdcg/` with the phase and `plan.schema.json`, and no plan
  or config. You help write both. A plan may start with `"$schema": "./plan.schema.json"`.
- **Ask first.** What is the goal, who uses it, what exists already, what must not change. Read
  the project before you suggest anything: its folders, its patterns, its tests.
- **Small cycles, one behaviour each** (XP). If a cycle needs "and" to describe it, split it. If
  it needs subtasks, it is more than one cycle.
- **Pick the right `type`** for each cycle:
  - `behaviour`: new behaviour, tests written first that fail.
  - `coverage`: tests for behaviour that already works (they must pass).
  - `refactor`: same behaviour, better structure. No RED.
  - `documentation`, `setup`, `spike`: no RED.
- **List every file** a cycle may touch in `files`, tests and shared ones included (errors,
  constants, types). Patterns are fine (`src/state/*.py`); `*` also crosses folders. A file left
  out means coming back to PLAN later.
- **Order matters:** the first cycle not done is the current one. Put what others need first.
- **`notes`** hold what SPECIFY will need: decisions, edge cases, open questions.
- **KISS, YAGNI:** plan only what the goal needs now. No "while we are here" cycles.
- Keys: `1`, `2`, `2b`, `3` … The cycle key names the cycle.
- The plan is strict JSON, checked against `plan.schema.json`. If `/claudio:next` lists problems,
  fix every one; the tool never fixes the plan for you.
- **Changing the plan mid-way** is normal: the user goes `back PLAN` from any phase, you make the
  change, and work restarts at SPECIFY of the first cycle not done. A change to a done cycle =
  add a new cycle, or set its `done` back to `false`.
- The config: `test_command` is any command the user wants (build, lint, tests chained with
  `&&`); Claudio only reads its exit status. `test_files` lists the patterns for test files.
  Optional `claude_free_writing_files` (see Free files in `SKILL.md`): `docs/**` covers a whole
  folder, a folder's name alone matches nothing. Only add what the user asks for. Help fix a
  broken config only here, in PLAN. `/claudio:next` waits for the command to finish, so a very
  slow one makes every phase move slow.

## Craft for this phase

[TDD, BDD, XP](../craft/tdd-bdd-xp.md) (small steps) · [Simplicity](../craft/simplicity.md)
(KISS, YAGNI) · [Clean Architecture](../craft/clean-architecture.md) (where things belong).
