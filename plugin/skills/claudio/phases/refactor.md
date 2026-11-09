# REFACTOR

## Goal

Apply what REVIEW found. Same behaviour, better structure: rename, simplify, remove duplication,
delete dead parts, move towards a pattern where the change asks for it. Tests stay green the
whole time.

## What may change

Non-test files only, within the cycle's `files`. Tests are locked. A finding that needs a test
change means going back to RED first.

## Checklist

- Work through the agreed REVIEW list, nothing more. No new behaviour.
- Small steps, run the tests after each one.
- DRY: one source for each rule, value and text. When two places need the same thing, move it to
  where both can use it.
- SOLID: split a class or function that has two reasons to change.
- Smells to remove: long functions, long parameter lists, the same `if` on a type in several
  places (→ Strategy or polymorphism), feature envy, flags that change behaviour, comments that
  explain unclear names (rename instead).
- If a refactor breaks a test, the refactor is wrong, not the test.
- Update the notes: what changed and why. Then the full test suite once more.

## Craft for this phase

[SOLID](../craft/solid.md) · [Simplicity](../craft/simplicity.md) (DRY) ·
[Design patterns](../craft/design-patterns.md) · [Clean Code](../craft/clean-code.md).
