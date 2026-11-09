# RED

## Goal

Write the tests that say what "done" means for this cycle, before any implementation. In a
`behaviour` cycle they must **fail**; in a `coverage` cycle they must **pass**. The user reads
and approves them: if a human never reads the test, they don't own the specification.

## What may change

Test files only (the config's `test_files`), and only those in the cycle's `files`. Test support
files count as test files.

## Checklist

- **One behaviour per test**, and the test name says the behaviour:
  `test_next_from_commit_goes_to_specify`, not `test_next_3`.
- **Cover the spec:** each example, each edge case, each error case. An error test checks the
  exact error type and its full message, once.
- **Fast and independent:** no order between tests, no shared state, temporary folders for files.
- **Test files hold only tests.** Fixed values and helpers live in the test support folder, even
  when only one file uses them. A value used by several test files lives there once.
- Tests keep their own fixed values; never import them from the implementation under test.
- **Fixed lists are written out in full**, so the reader sees them at a glance.
- Reuse the test helpers that exist before adding one. A new helper that only joins two existing
  ones is not needed.
- Test behaviour through the public entry points, not private helpers.
- Run the tests and show the result: they fail for the right reason (a missing module or class
  counts as failing in RED). Then wait for approval.

## Craft for this phase

[Tests](../craft/tests.md) · [TDD, BDD, XP](../craft/tdd-bdd-xp.md) ·
[Clean Code](../craft/clean-code.md) (tests are clean too: names, no duplication).
