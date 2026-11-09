# GREEN

## Goal

Make the tests pass with the **simplest implementation that works**, written cleanly from the
first version. GREEN stays simple; the bigger design work happens in REFACTOR.

## What may change

Non-test files only, and only those in the cycle's `files`. Tests are locked: changing a test,
even a small fix, means going back to RED.

## Checklist

- Follow the pattern agreed in PROMPT.
- **Write to the craft rules now, not later:** names that say the behaviour, short functions with
  one job, guard clauses instead of `else`/`elif` chains, error handling kept apart from the logic
  (one `try` around one helper call), no inline literals, texts in the one
  messages place, errors that build their own message.
- **Don't reinvent:** before each helper or loop, check the language, the standard library and
  the project. Use them.
- No silent decisions: a plain `return`, `None` or default that means "allowed" or "skip" is said
  in the name or the docstring.
- Dependencies point inward only.
- Nothing extra: no feature, option or abstraction the tests don't ask for (YAGNI).
- Run the full test suite, not only the new tests. All pass, no new warnings.
- If a test seems wrong, stop and say so. Never weaken it; the user decides whether to go back to
  RED.
- Look over your own diff before you show it: anything repeated, anything unused, anything that
  already existed?

## Craft for this phase

[Clean Code](../craft/clean-code.md) · [Simplicity](../craft/simplicity.md) ·
[Clean Architecture](../craft/clean-architecture.md) · [Safety](../craft/safety.md).
