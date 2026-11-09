# Clean Architecture

Business rules free of details. Details (files, databases, frameworks, HTTP, the tool calling
you) sit at the edge and depend on the rules, never the other way round.

## Dependencies point inward

- **Glue → rules → storage → types**, never back. In Claudio: `hooks` → `commands`/`guards`/`checks`/`context`
  → `state` → `domain`/`core` (2026-10).
- The inner parts know nothing about the outer ones: a rule never reads hook JSON, a type never
  touches a file.
- An inner part that needs an outer one gets it passed in (Dependency Injection), behind a small
  interface it owns (Dependency Inversion).
- `core` sits below `domain`: shared pieces must not import the types; pass a plain value (a
  phase's name) instead (2026-11-07).

## Folders by area

- **Tidy from the start:** folders by area, even while small (2026-10). E.g. `core/` (constants,
  messages, errors), `domain/` (types, one module per type), `state/` (reading and writing
  files), `guards/` (allow or raise), `hooks/` (thin glue), `checks/`, `context/`, `commands/`.
- **No folder for a single file**, unless the area is agreed and will grow.
- **One job per module.** One-off checks go in `scripts/`, never in the package.
- **A new area gets a new folder** when its job fits none of the existing ones (e.g. "what Claude
  is told" is not a guard and not state → `context/`) (2026-11-07).

## Errors, messages, constants

- **One base error for the project;** anything else is a bug (2026-10).
- **All error classes in one place.** Each builds its own message from its arguments; no empty
  `pass` classes, no enum of messages.
- **One error per case, named for what was expected**, each straight from the base error. A
  parent class only when something catches it (2026-11-07).
- Callers catch the base error; the hook glue turns it into an answer.
- **Every text for people in one messages place**, as templates. **Every fixed value in one
  constants place.** Environment variable names and the functions that read them in one config
  place.
- **Bugs never stop the user** in a tool that guards their work: warn once, carry on, and let a
  rule error (a real block) through as a block.

## Boundaries

- A module's public functions are its contract. Keep them few, named for the behaviour, and say
  in the docstring what they return or raise.
- Read a file once, in one place (a repository-like module), and pass typed values on.
- Quick reads for hot paths (hooks run on every action) and the full check where it runs once
  (e.g. schema validation only when the phase moves) (2026-11-06).
- Where the tool's own files are is found from the package itself, not from a setting, so it is
  the same in a clone, an install and the tests (2026-11-07).

## Paradigms

None replaced the others; know which one you use and why.

- **Structured:** sequence, selection, iteration; each block with a clear start and end. Inside
  functions.
- **Object-oriented:** data and the behaviour on it together, details hidden behind an interface,
  polymorphism to swap implementations. To organise modules. Abstractions help change but can
  hurt understanding: add one only when it earns its place.
- **Functional:** pure functions, immutable data, functions as values. For transformations
  without shared state; easier to reason about under concurrency.
