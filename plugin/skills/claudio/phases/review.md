# REVIEW

## Goal

Read the cycle's change as an experienced reviewer would. Passing tests say nothing about names,
duplication, or whether the design fits the rest of the project. REVIEW is a conversation: you
list findings, the user adds theirs and decides.

## What may change

Nothing. Read, run read-only commands, comment.

## Checklist

Go through the whole craft guide as a checklist, rule by rule, on **this cycle's change only**:

- **Does it do one thing?** Each function, class and module one job (SOLID: single
  responsibility).
- **Names:** say the behaviour, one verb per kind of action, no vague verbs, no tool names that
  hide the job.
- **Reuse:** anything copied instead of reused? Anything the language or the project already
  gives? The same rule written in two places? Two lists or tables holding the same values?
- **Simplicity:** can it be shorter and plainer? Hard to follow = rewrite it simpler (one
  function instead of two that bounce, one condition with `and` instead of nested steps).
- **Control flow:** guard clauses, no `elif` chains, each condition named. Error handling apart
  from the logic: one `try` around one helper call, never a `try` mid-function with `if`s after
  it. Variables made where they are used, and never used outside the block that made them (also
  in Python).
- **Dead or unused:** imports, parameters, helpers, parent classes nothing needs.
- **Fixed tables and sets frozen** (read-only types).
- **Tests:** exact errors and full messages, values and helpers in the support folder, names say
  the behaviour.
- **Patterns:** missing where the problem asks for one? Forced where it doesn't?
- **Architecture:** dependencies inward, each file in the right folder.
- **Safety:** inputs checked, nothing outside the project touched, no secrets.
- **Docs:** notes and README match what was built.

How to report:

- Number each finding: what, where (`file:line`), why, the suggested fix.
- Mark which fixes change tests (they go back to RED) and which only change the implementation
  (REFACTOR).
- **Review fixes stay in this cycle and only touch this cycle's change.** Don't plan a new cycle
  for them and don't widen them to the whole project. Older issues elsewhere: mention once at
  most.
- The user decides: back to RED (missing behaviour or tests; GREEN for types without RED), or on
  to REFACTOR. Write the agreed list into the notes.

## Craft for this phase

All of it: [TDD, BDD, XP](../craft/tdd-bdd-xp.md) · [Clean Code](../craft/clean-code.md) ·
[Clean Architecture](../craft/clean-architecture.md) · [SOLID](../craft/solid.md) ·
[Simplicity](../craft/simplicity.md) · [Design patterns](../craft/design-patterns.md) ·
[Tests](../craft/tests.md) · [Safety](../craft/safety.md).
