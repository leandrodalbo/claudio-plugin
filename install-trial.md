# Install trial: install from the marketplace

Install Claudio the way a new user will, with an empty data folder, and check it works
everywhere. Run it before each release, and after any change to the install (`requirements.txt`,
`tdcg/setup/`, `hooks.json`, `plugin.json`, `marketplace.json`).

Each run: copy the results table at the end into the step's notes (e.g. `devinfo/step5`) with the
date and the commit, and keep this file clean. A check that fails is a bug: fix it in a cycle
before the release. Keep the guide up to date when the install changes (a new command, a renamed
plugin: e.g. ClaudioXP changes `claudio@claudio-plugin` and every `/claudio:`).

First written for step 5.1 (2026-11-10).

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

- [x] Both commands say they worked.

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

## 6. A ready venv is left alone

```bash
stat -c %y "$DATA"/venv-done.txt
```

Close Claude, start it again, run `/claudio:status`, then `stat` again.

- [ ] Same time: nothing was built again. The start was not slower.

## 7. A command typed during the first build

```bash
rm -rf "$DATA"/venv "$DATA"/venv-done.txt
cd ~/claudio-trial && claude
```

Type `/claudio:status` **straight away**, before the build can finish.

- [ ] What happened? (works / waits / error: copy the message)
- [ ] After both finish: `"$DATA"/venv/bin/python3 -c "import jsonschema"` works, and
      `venv-done.txt` is there.
- [ ] Start a new session: `/claudio:status` works.

If the venv ends up broken, note it: that's a bug to fix before the release.

## 8. The failure message (no internet)

pip reads `PIP_INDEX_URL`, so a dead address makes the install fail:

```bash
rm -rf "$DATA"/venv "$DATA"/venv-done.txt
cd ~/claudio-trial && PIP_INDEX_URL=http://127.0.0.1:9/simple claude
```

- [ ] At start you see: "Claudio couldn't install its Python libraries (installing the
      libraries: …)". Is the part after the colon clear?
- [ ] `/claudio:status` is blocked with the same message.
- [ ] An edit or a shell command still goes through the guard rails (try one the phase blocks).
- [ ] No `venv-done.txt` in `$DATA`.

Close it and start plain `claude` again:

- [ ] It builds, and `/claudio:status` works (it repairs itself).

## 9. A Python upgrade

Pretend the venv came from another Python:

```bash
sed -i '1s/.*/python 3.0/' "$DATA"/venv-done.txt
```

Start Claude, wait, then:

- [ ] `head -1 "$DATA"/venv-done.txt` shows your real version again (it was rebuilt).

## 10. VS Code panel

Open `~/claudio-trial` in VS Code and open the Claude panel.

- [ ] Typing `/claudio:` lists init, next, back and status.
- [ ] `/claudio:status` works there.

## 11. IntelliJ button

Open `~/claudio-trial` in IntelliJ and start Claude with its button.

- [ ] `/claudio:` commands show and `/claudio:status` works.

## 12. Validate

```bash
cd ~/earn-the-day/claudio-plugin
claude plugin validate --strict ./plugin
claude plugin validate --strict .
```

- [ ] Both pass.

## 13. Clean up

```bash
claude plugin uninstall claudio@claudio-plugin
claude plugin marketplace remove claudio-plugin
rm -rf ~/claudio-trial
```

- [ ] `ls ~/.claude/plugins/data/` (note whether the data folder is gone too; the docs page on
      uninstall needs this).

## Results

Copy this table into the step's notes for each run: date, commit, Python version, OS.

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Two-command install | | |
| 3 | First session builds the venv, says nothing | | |
| 4 | `/claudio:init`, `/claudio:status` | | |
| 5 | Phase rules without `--add-dir` | | |
| 6 | Ready venv not rebuilt | | |
| 7 | Command during the first build | | |
| 8 | Failure message, guard rails still on, repairs | | |
| 9 | Python upgrade rebuilds | | |
| 10 | VS Code panel | | |
| 11 | IntelliJ button | | |
| 12 | `validate --strict` | | |
| 13 | Uninstall leaves / removes data | | |
