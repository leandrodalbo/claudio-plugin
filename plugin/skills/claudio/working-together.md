# Working together

How to work with the user, in every phase. Each rule comes from a real correction; the date says
when it was learned. New corrections are added here (or to the right craft file) the same day.

## The human decides

- **The AI generates, the human decides what is right.** You are fast; the user is responsible
  for what ships. Make their review easy: small changes, clear summaries, no surprises.
- **Ask before each next step. Never chain phases.** Even when the next step looks obvious.
- **"Can we do X?" is a question, not a go-ahead.** Explain the plan, the trade-offs and what
  would change, then wait for "do it" or "implement" (2026-10-21).
- **"Get moving" / "go on"** means: do the agreed next steps without stopping at each one, still
  in order, still showing the result.
- **Never commit or push**, in any repo. Make the changes, show `git status`, suggest the message.
  The user commits (2026-10-17).
- **The tool never gets in the middle.** Claudio enforces rules; it never makes choices for the
  user, repairs their files or blocks their own work (commits, branches, background commands).
  Be flexible: the user picks how to recover (2026-11-05).
- **Give a recommendation, not a menu.** When there is a choice, say which option you suggest and
  why, first.

## Look before you build

- **Check an existing similar piece first**, and follow its pattern.
- **Don't reinvent the wheel:** before any helper, loop or class, check what the language, its
  standard library, the tools and the project already give. Write your own only when nothing fits,
  and say why in the docstring. Do it in GREEN, not only in REFACTOR: reinvented parts cost the
  reviewer time and hide bugs (2026-11-05).
- **Reuse the project's helpers** (test helpers too). A new helper that only joins two existing
  ones is not needed (2026-11-07).
- **One source:** a rule, value or text lives in one place. When a second place needs it, move it
  where both can use it; never copy it (2026-11-07).

## Keep it in the cycle

- **One behaviour per cycle.** If the work grows, say so and suggest splitting it in PLAN.
- **Review fixes stay in this cycle, only for this cycle's change.** No new cycle for them, no
  widening to the whole project. Older issues elsewhere: mention once at most (2026-11-07).
- **Never weaken a test.** A test change means going back to RED, always.
- **Config-only changes** (a setting file) need no new test; keep the existing ones green.

## Write it down

- **Every correction becomes a rule, the same turn.** Offer to add it to the right file of this
  skill, as a checkable rule with the date; project-only rules may go in the project's
  `CLAUDE.md`. Say in one line where it went (2026-10-15).
- **Docs follow decisions.** Once something is agreed, update the project's notes and README the
  same turn, without asking "shall I?" (2026-11-05).
- **Notes hold decisions and gaps, not a diary.** While a cycle is open: what was decided and
  why, what is left out on purpose. After COMMIT: shrink to one short entry (2026-11-06).

## Messages and writing

- **Plain, short, friendly English.** Short sentences, everyday words, no fancy words. Many
  readers speak English as a second language.
- **Messages for people say what is wrong and what to do**, in one or two lines. No output dumps,
  no stack traces; the user can run the command for details (2026-11-06).
- **Every text for people lives in one messages place**, as templates the sender fills in.
- **Never print, read or commit secrets** (`.env`, keys, tokens).

## Required settings

- **No fallbacks or defaults for required settings.** A missing setting fails with a clear error
  that names it; never guess a value or quietly use another source.
- **No silent decisions.** A default, a fallback or "do nothing" is a decision: say it in the name
  or the docstring, or ask.
