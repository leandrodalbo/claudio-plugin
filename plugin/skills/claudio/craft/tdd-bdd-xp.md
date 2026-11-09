# TDD, BDD and eXtreme Programming

The discipline under every Claudio cycle. TDCG is TDD where the AI writes both the test and the
implementation, and the human approves each step.

## TDD

Test-Driven Development: **red → green → refactor**.

- Write a failing test first. It proves the test can fail and pins down what "done" means.
- Write the least implementation that makes it pass.
- Clean up with the tests green. If a refactor breaks a test, the refactor is wrong.
- The test is the contract: writing it first forces you to think about the interface before the
  implementation.
- Never change a test to make it pass. Fix the implementation, or agree a new spec.
- A compile error or a missing module counts as RED.

## BDD

Behaviour-Driven Development: describe **behaviour in plain words**, with examples, before
building it.

- **Given** a situation, **when** something happens, **then** this result.
- Examples beat abstract rules: "given a refactor cycle, when the user skips RED, then …".
- Name edge cases and error cases in the spec, not later.
- Test names read as behaviour: `test_back_from_green_to_red_is_allowed`.

## eXtreme Programming

XP: small steps, the simplest thing that works, refactor all the time, short feedback loops.

- **Small releases, small cycles:** one behaviour per cycle; if it needs "and", split it.
- **Simple design:** the simplest thing that could possibly work, then improve it.
- **Refactor mercilessly**, with tests as the safety net.
- **Continuous integration:** every change builds and passes all tests.
- **Pair programming and review:** two people see different problems. Here, the user is the pair.
- **The order matters:** GREEN stays simple; the design work happens in REFACTOR.

## TDCG

Test-Driven Code Generation, the loop Claudio enforces:

```
1. SPECIFY  - agree one behaviour, in plain language
2. RED      - AI writes failing tests, human reviews and approves
3. PROMPT   - spec + approved tests + an existing file as the pattern
4. GREEN    - AI writes the implementation, tests pass
5. REVIEW   - human checks names, responsibilities, duplication, dead parts
6. REFACTOR - apply what review found, tests stay green
7. COMMIT   - one small, focused commit with a clear why
```

- **SPECIFY** forces one small behaviour at a time. More than two sentences = split.
- **RED** before any implementation: a human who never read the test doesn't own the spec.
- **PROMPT** gives a pattern: without one, the AI invents its own approach and drifts.
- **REVIEW** is the gate: passing tests say nothing about names, duplication or design fit.
- **COMMIT** stays small: easy to understand, easy to undo.
- Works best when the project has clear patterns and the "what" is clear. Be more careful with
  greenfield design (the spec must be more precise), and with performance and security work
  (tests prove the behaviour asked for, not speed or safety against an attacker).

## Agile values

From the Agile Manifesto (2001): **individuals and interactions** over processes and tools,
**working software** over comprehensive documentation, **customer collaboration** over contract
negotiation, **responding to change** over following a plan. The right side still has value; in
a conflict, the left wins. A plan never matters more than working software.
