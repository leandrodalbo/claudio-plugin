# Clean Code

Software that is easy to read, understand and change. The goal: reduce what the next person
needs to hold in their head to make a change. Bad design costs more over time, and producing more
with AI only makes the mess faster.

## Names

- **Names say the behaviour:** verb first, what it acts on, what it gives back.
  `calc(a, b)` → `calculate_tax(price, tax_rate)` (2026-10).
- **One verb per kind of action**, the same across the project: e.g. `build_` = new data in
  memory, `write_` = to disk, `load_` = from disk, `read_` = from disk into a type (2026-10).
- **The name says what comes back.** `is_…` / `has_…` return a bool and never throw.
  `ensure_…` (Java: `require…`) returns quietly or throws with the reason. If the caller needs the
  *why*, a bool is not enough: throw, or return a result with the reason (2026-11-02).
- **No vague verbs:** `handle`, `process`, `check`, `manage`, `do`. Say what it decides or gives
  back: `handle_edit_hook` → `decide_edit`, `check_edit` → `ensure_edit_allowed` (2026-11-02).
- **`decide_` only when choosing the answer is the job.** A function that mainly does something
  is named for that, even if it also returns an answer (2026-11-06).
- **No tool names that hide the job**, and no name wider than the function: "bash" for the shell,
  `decide_bash_command` for a git-only rule → `decide_git_in_command` (2026-11-06).
- **Names for what was expected**, e.g. errors: `TestsShouldHaveFailedError`, not
  `TestsPassInRedError` (2026-11-07).
- No abbreviations nobody would say aloud. No `data`, `info`, `manager`, `helper`, `util` alone.
- Each name says what the thing is: `changed`, `tdcg_files`, `path`. **Don't repeat one word**:
  `sorted(file for file in files if is_changed(file))` says "file" four times and hides the filter
  (2026-11-06).

## Functions

- **Short, one job each.** If you need "and" to describe it, split it. The caller puts the steps
  together (2026-10).
- **No "do X and also return Y":** `finish_cycle` only ticks; getting the next cycle is its own
  function.
- **Act on a named thing** when there is one: pass its key, don't guess "the first one" (2026-10).
- **No empty functions.** A function that does nothing (only a docstring or `pass`) only to fill
  a table row or a pattern is noise. "Do nothing" for one case is a decision: a guard clause where
  it is decided, said in the docstring. The same for parameters a function never uses and fake
  values (`{}`, `None`) passed only to fit a shape (2026-11-07).
- **Few parameters.** Many parameters, or a flag that changes behaviour, means two functions or a
  small type.
- **Private helpers are marked** (`_` in Python, `private` in Java/Kotlin). Only the real entry
  points are public (2026-10).
- **Say who calls an entry point:** a `main` or hook says who runs it, what it gets (e.g. JSON on
  stdin) and how the answer goes back (e.g. exit status) (2026-11-02).

## Control flow

- **Few if/else. No `elif` / `else if` chains.** Use early returns or throws (guard clauses). The
  happy path ends the function, not indented (2026-11-02).
- **The helper that owns a rule throws for it**, instead of returning `None` for the caller to
  test (2026-11-02).
- **Name each condition.** No bare expression in an `if` that needs a comment to read: write a
  small helper or use the clear library call. `(project / ".tdcg").is_dir()` →
  `is_claudio_on(project)`; `path.parts[:1] == (X,)` → `path.is_relative_to(X)` (2026-11-02).
- **Keep error handling apart from the logic.** A function either does the plain steps or handles
  their errors, never both. The handler is one `try` around one call to a helper that does the
  steps; no `try` in the middle of a function with `if`s after it (2026-11-07).
- **Keep each variable's scope tight, in every language.** A variable made inside a block (`try`,
  `if`, loop, `with`) is used only inside that block, even where the language would let it leak
  out (Python). Make it where it is used, inside the helper (2026-11-07).
- **One function beats two that bounce.** When a helper only exists to be called once from the
  same place, and following it is hard, fold it back: one function with `if a and not b: raise`
  first, then the plain steps (2026-11-07).
- **No nested loops** (user, 2026-11-08). First ask whether the walk is needed at all (compare the
  whole structure, use a lookup); otherwise a library call or one small function per level.
- **A ternary only picks between two plain values** with a short condition
  (`PASS if status == 0 else FAIL`): never nested, no calls or filters inside (2026-11-07).
- **A type switch repeated** in several places → polymorphism or Strategy.
- **A row of `if x is A … if x is B …` on one value → a read-only table** from each value to a
  small function (or value), and one lookup. Each function one job; a new case = a new row; a
  missing case fails loudly instead of being skipped. The table lives where its details belong
  (Claude Code's JSON stays in the hook glue, not on a domain enum) (2026-11-07).

## Clarity

- **Reads like plain steps, for a human.** No packed one-liners that filter and change in one go
  (`[w for w in x if w]`). The language's own tools for a job are fine and preferred (`any(…)`,
  `next(…)`, `re.findall`) (2026-11-05).
- **Any filter is a plain loop** (`for` + `if` + `append`), even one that only filters, even
  inside `sorted(…)` (2026-11-06).
- **No silent decisions.** A plain `return`, `None` or default that really means "allowed" or
  "skip" is said in the name or docstring. If it is a rule, spell it out (2026-11-02).
- **No inline literals:** fixed values (folder and file names, separators, field names) live in
  one constants place. An order that matters comes from one source, e.g. the order of an enum
  (2026-10).
- **Every text for people lives in one messages place**, as templates the sender fills in (Python:
  `str.format`). Messages ≠ constants: constants are values the logic depends on (2026-11-06).
- **Fixed tables and sets are read-only:** `frozenset`, `MappingProxyType` (Python), `setOf`,
  `mapOf` (Kotlin), `List.of`, `Map.of` (Java) (2026-11-07).
- **Comments say why, not what.** If a comment explains what a line does, rename instead.
  Docstrings say who calls, what comes back, and any rule that isn't obvious.
- **No dead parts:** unused imports, parameters, helpers, parent classes nothing needs.
- **Wrap lines** at the project's width (here 100).

## Language notes (examples, not core rules)

- Kotlin: constant values as `const val` in a `companion object`; `runCatching { }.onFailure { }`
  instead of try/catch, always rethrow (`throw it`) unless swallowing is truly meant; MockK for
  test doubles, no hand-written fakes.
- Python: enum classes named `Test…` need `__test__ = False`, or pytest tries to collect them.
- **Python: write as if blocks had their own scope** (user, 2026-11-07). Python only makes a
  scope for functions, classes and modules, so a variable made inside a `try`, `if`, `for` or
  `with` still lives after it. Don't use that: a variable made inside a block is used only inside
  that block, as in Java or Kotlin. Need the value after the block? Put the block in its own small
  function and return the value.
- **Python: imports go at the top of the file, never inside a function** (user, 2026-11-08). If a
  module is too heavy to load every time, fix why it runs every time.
- Before catching an error, check whether a caller already catches it (e.g. the shared hook glue
  turns every bug into a warning). A second `try` for the same thing is a copy (2026-11-07).
- Java: `StringBuilder` in loops, never `+=` on a `String` (see
  [efficiency](../knowledge/efficiency.md)).
