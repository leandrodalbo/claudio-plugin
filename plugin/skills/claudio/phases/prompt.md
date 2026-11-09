# PROMPT

## Goal

Hand over everything GREEN needs: the approved spec, the failing tests, and **an existing file
to follow as the pattern**. The pattern is what stops the implementation from drifting away from
the project's style. No pattern (greenfield) is fine only when the user says so on purpose; then
the spec must be more precise.

## What may change

Nothing. Suggest pattern files and the design.

## Checklist

- Find the closest existing piece in the project and suggest it as the pattern. Say what to copy
  from it (structure, naming, error handling, tests).
- Say the design: which module or class, where it sits in the architecture (which folder, which
  way the dependencies point) and why.
- Name the existing helpers, library calls and types you will reuse. Name anything that must
  move so two places can share it (one source, never a copy).
- Pick a design pattern only if the problem asks for it (a type switch → Strategy, a request
  passed along → Chain of Responsibility). Say why, or say "no pattern needed".
- Say which knowledge pages apply (caching, data structures, a query…) and read them.
- Write the plan short, in the project's notes, so the user can check it.
- Wait for the user before GREEN.

## Craft for this phase

[Design patterns](../craft/design-patterns.md) ·
[Clean Architecture](../craft/clean-architecture.md) · [SOLID](../craft/solid.md) ·
[Simplicity](../craft/simplicity.md) (KISS, YAGNI).
