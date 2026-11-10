# Troubleshooting

The usual problems, and what to do. Lost at any point? `/claudio:status` shows where you are and
every command.

## "Claudio couldn't install its Python libraries"

> Claudio couldn't install its Python libraries (\<step\>: \<error\>). Guard rails still work;
> /claudio: commands don't. Fix: check your internet; on Debian/Ubuntu: sudo apt install
> python3-venv. Then try any /claudio: command again.

ClaudioXP builds its libraries once, at the first session. If that fails:

- Check your internet.
- On Debian or Ubuntu: `sudo apt install python3-venv`.
- Check your Python: `python3 --version` must say 3.11 or newer.

Then run any `/claudio:` command: it tries again. The guard rails keep working meanwhile.

## I upgraded Python

Nothing to do. ClaudioXP notices the new version at the next session and rebuilds its libraries
by itself.

## VS Code says "blocked by hook"

VS Code's Claude panel shows each `/claudio:` answer as "UserPromptExpansion operation blocked by
hook: …". That's normal: the text after it is ClaudioXP's answer.

## The `/claudio:` commands don't show up

- Start a new session, or type `/reload-plugins`: an open session doesn't see a new plugin.
- Check it's installed and on: `/plugin` → **Installed**.
- Look for errors: `/plugin` → **Errors**.
- Check the hooks are loaded: `/hooks`.

## Two copies are on

With the marketplace copy and a local copy loaded with `--plugin-dir` both on, both run their
hooks. Keep one: `claude plugin uninstall claudio@claudio-plugin`, or start Claude
without `--plugin-dir`.

## "Claudio is not set up here"

> Claudio is not set up here. Start with /claudio:init.

ClaudioXP is off in this project. Run `/claudio:init` to turn it on.

## "No plan" or "Bad plan"

> No plan at \<path\>. Write one in the PLAN phase first.

Ask Claude to write the plan, then `/claudio:next`. A "Bad plan" or "Bad config" message lists
every problem with the line or field: ask Claude to fix them, still in PLAN. See
[plan and config](plan-and-config.md).

## An edit or command was blocked

That's ClaudioXP doing its job. The message says why and what to do, for example:

> Tests are locked in GREEN, and \<the file\> is a test file. Go back to RED to change a test.

> \<the file\> is not in cycle \<key\>'s files. Go back to PLAN to add it.

Move the phase yourself (`/claudio:next`, `/claudio:back <PHASE>`) when you agree.

## "Claudio hit a bug"

> Claudio hit a bug (\<kind\>: \<error\>). \<what now\>

A bug never stops your work: the tool runs, and the message says what was not checked. Please
[open an issue](https://github.com/leandrodalbo/claudio-plugin/issues/new/choose) with the
message.

## Still stuck?

Ask on [Discord](https://discord.gg/AjyKgTbNtr).
