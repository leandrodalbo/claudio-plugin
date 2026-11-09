# Tests

Tests are what make change safe: confidence to refactor, documentation that can't go stale, and a
safety net for anyone who touches a file they didn't write.

## A good test

- **One behaviour per test**, and the **name says the behaviour**.
- **Fast and independent:** no order, no shared state, temporary folders, nothing left behind.
- **Checks the result, not the steps:** test through the public entry points, not private
  helpers.
- **An error test checks the exact error type and its full message,** once. That also proves
  what the message must not contain (no command, no output dump) (2026-11-07).
- **Never weakened to pass.** A failing test means the implementation or the spec is wrong.
- Real processes where the real world is a process (a hook runs as a new Python with JSON on
  stdin); in-process calls for rules.

## Test support

- **One test file per module**, mirroring the folders (`tests/state/test_plan_file.py`).
- **Test files hold only tests.** Fixed test values (sample commands, expected messages) and
  helpers (writing a config, building an event) live in the support folder, even when only one
  file uses them (2026-11-07).
- **A value used by several test files lives there once**, never copied (2026-11-06).
- **Tests keep their own fixed values**, never imported from the implementation they test, so a
  wrong constant can't hide itself (2026-10).
- **Fixed lists are written out in full**, so the reader sees them at a glance; no filtering or
  building them from another list (2026-11-06).
- **Reuse existing helpers.** Builders for sample data (`build_valid_config`,
  `build_config_with_test_command`) and writers (`write_tdcg_json`) compose; a helper that only
  joins two others is not needed (2026-11-07).

## The pyramid

```
        e2e        few: slow, the whole system as a user drives it
     integration   some: real parts together (a service + a real database)
       unit        many: one part, dependencies mocked, fast enough for every save
```

## Kinds of cycle

- `behaviour`: new tests that fail first (RED).
- `coverage`: tests for behaviour that already works; they must pass in RED.
- `refactor` and the others: no RED; the existing tests are the safety net and stay locked.

## In CI

Every commit builds and runs every test; a broken build is visible at once and cheap to fix.
Tests are what make continuous delivery trustworthy.
