# Phases and cycle types

Work moves through phases. Each phase allows only certain changes, and only you move it on. The
exact rules Claude follows live in the skill:
[`plugin/skills/claudio/SKILL.md`](../plugin/skills/claudio/SKILL.md) and one file per phase in
[`phases/`](../plugin/skills/claudio/phases/).

## The phases

| Phase | Claude may change | Moves on when |
|---|---|---|
| PLAN | only `.tdcg/plan.json`, `.tdcg/config.json` | you approve the plan |
| SPECIFY | nothing (read, ask questions) | you approve a 1–2 sentence spec |
| RED | test files only, within the cycle's files | tests run and **fail** (pass in `coverage`) |
| PROMPT | nothing (suggest pattern files) | you pick a pattern, or say "no pattern" |
| GREEN | non-test files only, tests locked, within the cycle's files | tests run and **pass** |
| REVIEW | nothing (read and comment) | you say what to fix: back to RED, or on to REFACTOR |
| REFACTOR | non-test files only, tests locked, within the cycle's files | tests still **pass** |
| COMMIT | nothing | Claude suggests the message, you commit |

`/claudio:next` runs your test command itself when leaving RED, GREEN and REFACTOR. Claude's word
that the tests pass is not enough: the exit status decides.

At all times:

- Claude never changes `.tdcg/` (except the plan and config, in PLAN), nor files outside the
  project.
- Git is read-only for Claude: `status`, `diff`, `log`, `show`, `blame`, `ls-files`. You commit.
- Before each of your messages, Claude is told the phase, the cycle and the rules to read.

## Cycle types

Each cycle in the plan has a `type` (default `behaviour`). The type sets the route:

| Type | Route | RED expects |
|---|---|---|
| `behaviour` | SPECIFY → RED → PROMPT → GREEN → REVIEW → REFACTOR → COMMIT | new tests that **fail** |
| `coverage` | the same | tests for behaviour that already works, that **pass** |
| `refactor`, `documentation`, `setup`, `spike` | SPECIFY → PROMPT → GREEN → REVIEW → REFACTOR → COMMIT | no RED; tests stay locked |

A type that doesn't fit the work? Go back to PLAN and change it.

## The commands

| Command | What it does |
|---|---|
| `/claudio:init` | set up ClaudioXP in this project |
| `/claudio:next` | move to the next phase |
| `/claudio:next --skipTo <PHASE>` | jump ahead, skipping phases |
| `/claudio:back <PHASE>` | go back to an earlier phase |
| `/claudio:status` | where we are, and this list |

**Skipping:** only REVIEW and REFACTOR can be skipped, and only by you. The plan notes the skip
with the date. Claude never skips.

**Going back** is normal: `/claudio:back RED` to change a test, `/claudio:back PLAN` to change the
plan. After a plan change, work restarts at SPECIFY of the first cycle not done.

## Free files

Some files may change in any phase, tests included: list them in `claude_free_writing_files` in
the config ([plan and config](plan-and-config.md)). Handy for notes and docs. `.tdcg/` is never
free.
