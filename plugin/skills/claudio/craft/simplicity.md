# Simplicity

The cheapest software to change is the software that isn't there. Unnecessary cleverness creates
extra cost for every reader after you.

## KISS

Keep it simple: the simplest solution that works.

- Prefer plain steps over clever one-liners.
- Prefer one clear function over a small framework of helpers.
- If it is hard to follow, it is not simple yet: rewrite it plainer.
- Use a design pattern only when the problem asks for it, never to show off.

## DRY

Don't repeat yourself: **every rule, value and text has one source**.

- The same rule in two places (e.g. "is this phase on the route?" checked by two modules) → one
  owner, and the other calls it (2026-11-07).
- The same list or table in two places → one constant both use.
- The same text in two places → one message template.
- Duplication in tests is cleaned too: shared helpers and values in the test support folder.
- DRY is about knowledge, not letters: two lines that look alike but change for different reasons
  can stay apart.

## YAGNI

You aren't gonna need it: build what the current behaviour needs, nothing more.

- No options, flags, settings or abstractions "for later".
- No defaults or fallbacks nobody asked for.
- No new cycle or feature "while we are here".
- When "later" comes, the tests make the change safe.

## Don't reinvent the wheel

**The key rule for working with AI.** Before writing any helper, loop or class, look for what
already exists, in this order:

1. The language itself: `if not word`, `x in ALLOWED`, `word.startswith(…)`, slices.
2. Its standard library: `pathlib`, `shlex`, `itertools.groupby`, `fnmatch`, `subprocess`,
   `types.MappingProxyType`, `any`, `next`.
3. The tools and libraries the project already uses.
4. The project's own helpers, types and test support.

Write your own only when nothing fits, and say why in the docstring. Reinvented parts cost the
reviewer time and hide bugs (2026-11-05). A helper that only joins two existing helpers is not
needed (2026-11-07).
