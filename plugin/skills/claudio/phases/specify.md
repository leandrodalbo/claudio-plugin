# SPECIFY

## Goal

Agree on **one behaviour**, in plain words, in one or two sentences. If it doesn't fit in two
sentences, the cycle is too big: say so and suggest going back to PLAN to split it.

## What may change

Nothing. Read the project and ask questions.

## Checklist

- Read the cycle's `what` and `notes` in the plan, and the files it lists.
- Write the behaviour as BDD would: **given** a situation, **when** something happens, **then**
  this result. Add examples, edge cases and error cases.
- Say what is **not** in this cycle, so nobody expects it.
- Name the open questions, each with your suggested answer, and let the user decide. Don't make
  silent decisions: a default, a fallback or "do nothing" is a decision too.
- Check what exists: a similar behaviour, a helper, a library call. Say what you will reuse.
- Messages for people (errors, warnings): agree the text now. Short: what is wrong, what to do.
- Wait for the user's approval. A question from the user ("can we do X?") is a discussion, not
  approval.
- When the user decides something, write it into the project's notes the same turn.

## Craft for this phase

[TDD, BDD, XP](../craft/tdd-bdd-xp.md) (BDD) · [Simplicity](../craft/simplicity.md) (YAGNI:
only what this behaviour needs) · [Safety](../craft/safety.md) (what must fail clearly).
