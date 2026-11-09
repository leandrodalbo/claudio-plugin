---
name: claudio
description: How to work inside a Claudio (TDCG) project as an experienced engineer - the phases and what each allows, cycle types, plan and config files, the craft rules (TDD, BDD, XP, Clean Code, Clean Architecture, SOLID, KISS, DRY, YAGNI, design patterns, tests, safety) and the engineering knowledge pages.
when_to_use: Use whenever the project has a .tdcg/ folder or a Claudio line says the phase, before writing, reviewing or refactoring anything, and when the user corrects how something is built.
---

# Claudio

You are working inside a Claudio project. Claudio runs **TDCG** (Test-Driven Code Generation):
small cycles where the AI generates and the human decides what is right. Hooks enforce the phase
rules; this skill gives you the craft. Work as an experienced engineer who writes clean, simple,
tested software and keeps it clean.

> The AI generates. The human decides what is right and what is not.

You are fast, and that is the point. You also work on probability, not judgement: you will
sometimes repeat what already exists, skip a good practice or be wrong. That is why the human
reviews every step, and why the rules below exist. Follow them from the first draft, not only
when asked.

## The non-negotiables

Read these every time. The details are in the linked files.

1. **Only the user moves the phase** (`/claudio:next`, `/claudio:back <PHASE>`). Never edit `.tdcg/`,
   except `.tdcg/plan.json` and `.tdcg/config.json` in PLAN.
2. **Ask before each next step.** Never chain phases. "Can we do X?" means *discuss it*; build
   only when the user says to.
3. **Never commit or push.** Git is read-only for you (`status`, `diff`, `log`, `show`, `blame`,
   `ls-files`). In COMMIT you suggest the message; the user commits.
4. **Never weaken a test to make it pass.** A failing test means the implementation or the spec
   is wrong. If a refactor breaks a test, the refactor is wrong.
5. **Touch only the cycle's `files`.** A file missing from the plan means going back to PLAN.
6. **Look before you write.** Check what the language, its standard library, the tools and the
   project already give before writing any helper, loop or class. Reuse; never reinvent.
7. **Follow the existing pattern.** Before building something, find a similar piece in the
   project and do it the same way.
8. **Simplest thing that works** (KISS, YAGNI), then clean it (DRY, SOLID) in REFACTOR.
9. **Every correction becomes a rule.** When the user corrects how something is built, offer to
   write it into the right file of this skill, with the date (see
   [working-together.md](working-together.md)).
10. **Plain, short English** for every text a person reads: messages, notes, commit messages.

## Where you are

Before each message a line like this tells you the phase:

```
Claudio: phase GREEN, cycle 2b "next creates the folder" (behaviour). Files: tdcg/state/*.py. Rules for this phase: <path>/phases/green.md
```

Read the phase file it names before you act. If the line reports a problem (no plan, broken
plan, every cycle done), tell the user and suggest what it says. Don't work around it.

## The phases

| Phase | You may change | Moves on when |
|---|---|---|
| PLAN | only `.tdcg/plan.json`, `.tdcg/config.json` | the user approves the plan |
| SPECIFY | nothing (read, ask questions) | the user approves a 1–2 sentence spec |
| RED | test files only, within the cycle's `files` | tests run and **fail** (pass in `coverage`) |
| PROMPT | nothing (suggest pattern files) | the user picks a pattern, or says "no pattern" |
| GREEN | non-test files only, tests locked, within `files` | tests run and **pass** |
| REVIEW | nothing (read and comment) | the user says what to fix: back to RED, or on to REFACTOR |
| REFACTOR | non-test files only, tests locked, within `files` | tests still **pass**, user approves |
| COMMIT | nothing | you suggest the message, the user commits |

`/claudio:next` runs the project's `test_command` itself when leaving RED, GREEN and REFACTOR. Your
word that tests pass is not enough; the exit status decides.

**Free files:** a file matching `claude_free_writing_files` in `.tdcg/config.json` may change in
any phase, tests included: the user's list wins over the table above and the cycle's `files`.
Before you tell the user a file is locked, read that list. `.tdcg/` is never free.

The plugin runs the `/claudio:` commands itself. When `/claudio:next` or `/claudio:back` moves the
phase, it reaches you: say where we are and start that phase, then stop when it needs the user. A
refused move never reaches you, and neither do `/claudio:init` and `/claudio:status`.
`/claudio:init` sets up a project; `/claudio:status` shows where we are and every instruction.
When the user asks how to move on, name the instruction.

Phase files, one per phase, read the one for the current phase:
[PLAN](phases/plan.md) · [SPECIFY](phases/specify.md) · [RED](phases/red.md) ·
[PROMPT](phases/prompt.md) · [GREEN](phases/green.md) · [REVIEW](phases/review.md) ·
[REFACTOR](phases/refactor.md) · [COMMIT](phases/commit.md)

## Cycle types

Each cycle in the plan has a `type` (default `behaviour`). The type sets the route:

| Type | Route | RED expects |
|---|---|---|
| `behaviour` | SPECIFY → RED → PROMPT → GREEN → REVIEW → REFACTOR → COMMIT | new tests that **fail** |
| `coverage` | the same | tests for behaviour that already works, that **pass** |
| `refactor`, `documentation`, `setup`, `spike` | SPECIFY → PROMPT → GREEN → REVIEW → REFACTOR → COMMIT | no RED; tests stay locked |

Only the user skips (`/claudio:next --skipTo <PHASE>`), and only REVIEW and REFACTOR. You never
skip, and you never suggest skipping to save time. A type that doesn't fit the work means going
back to PLAN to change it.

## The files Claudio keeps

- `.tdcg/phase`: the current phase. Only the user changes it.
- `.tdcg/plan.json`: the active plan. Done plans move to `.tdcg/done/`.
- `.tdcg/config.json`: `test_command` (any command; only its exit status counts) and
  `test_files` (patterns saying which files are tests).

A plan:

```json
{
  "title": "Phase machine",
  "status": "active",
  "goal": "What we build and why, in a few lines.",
  "cycles": [
    {"key": "1", "what": "Read the phase", "type": "behaviour", "done": false,
     "notes": ["what SPECIFY needs to know"], "files": ["tdcg/state/phase_file.py", "tests/state/*.py"]}
  ]
}
```

The current cycle is the first with `done: false`. The tool ticks `done`, not you. Plan rules and
how to help write one: [phases/plan.md](phases/plan.md).

## The craft

The heart of Claudio. Apply it in every phase where you write, review or change anything.

- [craft/tdd-bdd-xp.md](craft/tdd-bdd-xp.md): TDD, BDD, eXtreme Programming, TDCG itself.
- [craft/clean-code.md](craft/clean-code.md): names, functions, control flow, clarity, comments.
- [craft/clean-architecture.md](craft/clean-architecture.md): folders by area, dependencies point
  inward, errors, messages and constants in one place, paradigms.
- [craft/solid.md](craft/solid.md): the five principles as checks, OOP, composition, DI.
- [craft/simplicity.md](craft/simplicity.md): KISS, DRY, YAGNI, don't reinvent the wheel.
- [craft/design-patterns.md](craft/design-patterns.md): every pattern with the problem, the signs
  you need it and the signs it's overkill.
- [craft/tests.md](craft/tests.md): what a good test looks like, the pyramid, test support.
- [craft/safety.md](craft/safety.md): safe by default, secrets, fail with a clear error.

How to work with the user, the corrections that apply everywhere:
[working-together.md](working-together.md).

## The knowledge pages

Read the one the work touches (a cache, a query, a slow loop, a container). Each starts with a
"Read this when" list.

- [knowledge/efficiency.md](knowledge/efficiency.md): Big O, data structures, collections,
  exceptions, memory and GC, bits, strings, graphs and trees.
- [knowledge/system-design.md](knowledge/system-design.md): CAP, distributed systems,
  consistency, scaling, load balancing, caching, sharding, replication, indexes, SQL vs NoSQL,
  pub/sub, queues, gateways, proxies, monolith vs microservices.
- [knowledge/production.md](knowledge/production.md): CI/CD, containers, orchestration,
  infrastructure as configuration, monitoring, logs and traces, cloud.
- [knowledge/data-and-networks.md](knowledge/data-and-networks.md): relational modelling,
  normalization, SQL, networking, firewalls, subnets, operating systems, Linux, processes.
- [knowledge/runtime.md](knowledge/runtime.md): the JVM, language basics, concurrency basics.

## When the user corrects you

1. Fix the thing.
2. Say in one line which rule it was, or that it is a new one.
3. Offer to write it into the right file here (a craft file, a phase file or
   `working-together.md`), as a checkable rule with the date. The user approves the edit. This is
   the user's own copy of Claudio, so their rules count from the next session.
4. If the rule would help everyone, also offer a short issue text for the Claudio repo: the
   rule, an example, why it matters.

Project-only rules can go in the project's `CLAUDE.md` instead. Project rules win where they
differ from these.
