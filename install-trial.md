# Install trial: install from the marketplace

Install Claudio the way a new user will, with an empty data folder, and check it works
everywhere. Run it before each release, and after any change to the install (`requirements.txt`,
`tdcg/setup/`, `hooks.json`, `plugin.json`, `marketplace.json`).

Before you start:
- Use a terminal **outside** this repo, with no `--plugin-dir` and no `--add-dir`.
- Make sure the dev copy (`claudio@inline`) is not on in the trial project, or the hooks run
  twice. Check with `/plugin` → Installed.
- A local marketplace installs what is on disk **now**, including changes not committed yet.

## 0. A trial project

```bash
mkdir -p ~/claudio-trial && cd ~/claudio-trial && git init
```

## 1. Install with the two commands

```bash
claude plugin marketplace add ~/earn-the-day/claudio-plugin
claude plugin install claudio@claudio-plugin
```

- [ ] Both commands say they worked.

## 2. Empty data folder

```bash
ls ~/.claude/plugins/data/
```

Find the Claudio folder (something like `claudio-claudio-plugin`). Look at what's in it, then
empty it:

```bash
DATA=~/.claude/plugins/data/<the claudio folder>
ls -la "$DATA"
rm -rf "$DATA"/venv "$DATA"/venv-done.txt
```

If there is no folder yet, that's fine: the first session makes it.

## 3. First session builds the venv

```bash
cd ~/claudio-trial && claude
```

Wait about 10–20 seconds, then in another terminal:

```bash
ls "$DATA"
head -1 "$DATA"/venv-done.txt
"$DATA"/venv/bin/python3 -c "import jsonschema; print(jsonschema.__version__)"
```

- [ ] `venv/` and `venv-done.txt` are there.
- [ ] The first line is `python 3.14` (your Python's version).
- [ ] jsonschema prints `4.26.0`.
- [ ] Claude said nothing about the setup (no text from the build in the chat).
- [ ] This proves Claude Code set `CLAUDE_PLUGIN_DATA` for the hook.

## 4. The commands work

In the session:

```
/claudio:init
/claudio:status
```

- [ ] Both run, and status shows the phase.

## 5. Phase rules without `--add-dir`

Move to a phase (`/claudio:next`) and let Claude start it.

- [ ] Claude reads `phases/<phase>.md` from the installed plugin with no permission error.
  The README can't ask people for `--add-dir`.
