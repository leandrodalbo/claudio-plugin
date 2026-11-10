# Install

Two commands install ClaudioXP once on your machine. Then you turn it on in each project where
you want it.

## What you need

- [Claude Code](https://code.claude.com/docs)
- git
- Python 3.11 or newer (`python3 --version`). On Debian or Ubuntu, also `python3-venv`:
  `sudo apt install python3-venv`.
- Internet, the first time: ClaudioXP installs its own Python libraries.

It works on Linux, macOS, and Windows through WSL.

## 1. Install the plugin

In a terminal:

```
claude plugin marketplace add leandrodalbo/claudio-plugin
claude plugin install claudio@claudio-plugin
```

Or inside Claude Code, the same two steps:

```
/plugin marketplace add leandrodalbo/claudio-plugin
/plugin install claudio@claudio-plugin
```

You don't clone anything: Claude Code fetches the plugin itself.

## 2. Start a new session

A session that was already open doesn't see the plugin until you restart it, or type
`/reload-plugins`. The first new session also builds ClaudioXP's Python libraries quietly, once
(about 20 seconds).

## 3. Turn it on in your project

ClaudioXP stays off in every project until you turn it on there. In the project's folder, start
Claude and run:

```
/claudio:init
```

You should see:

> Claudio: set up here. Phase PLAN. Now tell Claude your plan: what to build, your test command
> and your test files.

The guard rails start now, in this project only. Next: [your first cycle](first-cycle.md).

## Editors

ClaudioXP runs inside Claude Code, so it works wherever Claude Code runs:

- **Terminal:** `claude` in your project's folder.
- **VS Code:** the Claude panel, or `claude` in VS Code's terminal. The `/claudio:` commands work
  in both.
- **IntelliJ and Neovim:** run Claude Code in their terminal, or through their Claude Code
  plugin.

VS Code's panel shows each `/claudio:` answer as "UserPromptExpansion operation blocked by hook:
…". That's normal: the text after it is ClaudioXP's answer.

## Update

```
claude plugin update claudio@claudio-plugin
```

Then start a new session. If the new version needs other libraries, ClaudioXP rebuilds them by
itself.

## Uninstall

```
claude plugin uninstall claudio@claudio-plugin
claude plugin marketplace remove claudio-plugin
```

ClaudioXP keeps its libraries in `~/.claude/plugins/data/claudio-claudio-plugin/`. Delete that
folder if it is still there. Your projects keep their `.tdcg/` folder; delete it to remove the
plan and config from a project.
