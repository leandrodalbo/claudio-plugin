# COMMIT

## Goal

One small, focused commit per cycle, made by the user. You write the suggested message. A small,
tested, reviewed change is easy to understand and easy to undo.

## What may change

Nothing. Never run `git commit`, `git push` or any other git write. Git is read-only for you.

## Checklist

- Show `git status` and a short summary of what changed.
- Suggest the commit message:
  - first line: the cycle key and what was done, short (`3.5 test check: review fixes`);
  - a blank line, then what and **why**, a few bullet points, from the cycle's `what`, the spec
    and the diff;
  - plain words, no filler.
- Remind the user of anything not in the commit on purpose (git-ignored files, notes kept
  private).
- After the user commits, they choose: stay in this cycle, or go back to PLAN and add one. The
  tool ticks the cycle done when they move on with `/claudio:next`. After the last cycle, that also
  files the plan under `.tdcg/done/` and goes back to PLAN.
- Afterwards, shrink the cycle's notes to one entry: what it does, the decisions and why, the gaps
  left on purpose. Notes hold decisions, not a diary.

## Craft for this phase

[TDD, BDD, XP](../craft/tdd-bdd-xp.md) (small commits, TDCG) ·
[Working together](../working-together.md).
