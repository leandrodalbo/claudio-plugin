# Try ClaudioXP yourself: TypeScript in VS Code

Build a small ID generator with Claude while ClaudioXP keeps the work honest. One small cycle, from
plan to commit.

You will also ask Claude to break the rules on purpose, so you can see what stops it.

## What you need

- [Claude Code](https://code.claude.com/docs)
- Python 3.11 or newer
- git
- Node.js 24 or newer
- VS Code
- ClaudioXP, installed: see [Install](../../docs/install.md)

Keep a second terminal open for your git commit.

## 1. Set up an empty project

Start Claude Code in a new folder, without ClaudioXP for now:

```
mkdir id-generator && cd id-generator
git init
claude
```

Ask Claude:

> Create an empty TypeScript project for Node 24 with Jasmine, and one test that passes. No
> compile step: set "type": "module" and let Jasmine load spec/**/*.spec.ts directly, using
> Node's built-in TypeScript support. Imports keep their .ts ending. Add typescript and
> @types/jasmine, a tsconfig.json with noEmit and allowImportingTsExtensions, and a .gitignore
> for node_modules/. No other features.

Check that the test passes with `npm test --silent`. Then exit Claude and commit, in the terminal:

```
git add -A
git commit -m "Empty project"
```

## 2. Turn ClaudioXP on

Open the folder in VS Code (`code .`), then open the Claude panel, or a terminal (**Terminal →
New Terminal**) and start Claude there:

```
claude
```

Then:

```
/claudio:init
```

You should see `Claudio: set up here. Phase PLAN.`, then a line telling you to give Claude your
plan. Claude Code labels that answer as "blocked by hook". That's normal here: this command only
reports, so it never goes to Claude.

## 3. Plan

> Write the plan. Title: ID generator. One behaviour cycle, object-oriented: a Singleton class
> IdGenerator with a private constructor. There must be exactly one instance, because two
> generators would hand out the same IDs. IdGenerator.getInstance() always returns the same
> object. next() returns a new number each time, higher than the last. The instance is shared
> between tests, so tests never check exact numbers. Nothing else: no reset method, no saving to
> disk. Also write the config: test command `npm test --silent`, test files `spec/**`. The cycle
> may change `src/**` and `spec/**`.

Read the plan. Happy with it? From here on, only you move the phase, and Claude starts each new
phase by itself.

```
/claudio:next
```

## 4. Build it, and try to break the rules

**SPECIFY:** nothing may change here. Claude proposes the spec. Agree it, then `/claudio:next`.

**RED:** tests only. Claude writes a failing test. When it stops, ask for a shortcut:

> Now write the real thing too. Try it anyway, let's see what happens.

The edit is blocked:

> RED only allows test files, and \<the file\> is not one (see test_files in .tdcg/config.json).

Read the test: it's your definition of "right". Then `/claudio:next`, which runs your tests and
needs them to fail.

**PROMPT:** Claude looks for an existing file to follow. This project is new, so answer:

> No file to follow, the project is new. When we get to GREEN, don't start until I say.

Then `/claudio:next`.

**GREEN:** the tests are locked now. First, move on too early:

```
/claudio:next
```

Claudio runs your tests and refuses, whatever anyone says:

> GREEN: the tests fail. Make them pass, then /claudio:next.

Now ask for the classic cheat:

> Change the test so it passes. Try it anyway, let's see what happens.

The edit is blocked:

> Tests are locked in GREEN, and \<the test file\> is a test file. Go back to RED to change a test.

Back to the proper way:

> OK, make the test pass by building the real thing.

Then `/claudio:next`, which needs the tests to pass.

**REVIEW:** Claude reviews the change and you read it. You decide if it's right. Then
`/claudio:next`.

**REFACTOR:** Claude says what is worth cleaning up, with the tests still locked. Then
`/claudio:next`, which needs the tests to still pass.

**COMMIT:** commits are yours. Claude suggests a message. Ask:

> Commit it for me. Try it anyway, let's see what happens.

The command is blocked:

> git commit is blocked: Claudio keeps git read-only (status, diff, log, show, blame, ls-files).
> Run it yourself.

Commit in your second terminal, with the message Claude suggested:

```
git add -A
git commit -m "<the message>"
```

Then `/claudio:next`. Claudio files your finished plan in `.tdcg/done/`. You are done.

## If something looks different

- **Claude says no before trying:** it knows the rules too. Tell it to try anyway, and Claudio
  does the stopping.
- **Claude says a Singleton is overkill:** usually it would be, and Claudio's rules say so. The plan
  gives the reason for this one. You pick the pattern, Claude follows.
- **Claude started GREEN without waiting:** press Esc, or skip the "too early" step. Those are the
  only two things that depend on it waiting.
- **Lost?** `/claudio:status` shows where you are and every command.
- **Need to change a test?** `/claudio:back RED`.
- **Need to change the plan?** `/claudio:back PLAN`.

Using another language? Follow the same steps with your own project, test command and test files.
