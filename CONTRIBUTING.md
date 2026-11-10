# Contributing to ClaudioXP

Thanks for helping. ClaudioXP is built the XP way: small steps, tests first, feedback early.

Questions? Ask on [Discord](https://discord.gg/AjyKgTbNtr). Please follow the
[code of conduct](CODE_OF_CONDUCT.md).

## What you need

- git
- Python 3 (on Debian/Ubuntu also `python3-venv`)
- [Claude Code](https://code.claude.com/docs)

## 1. Set up

Fork the repo on GitHub, then:

```
git clone https://github.com/<you>/claudio-plugin.git
cd claudio-plugin
python3 -m venv .venv
source .venv/bin/activate
pip install -r plugin/requirements.txt pytest
```

## 2. Run the tests

```
cd plugin
python3 -m pytest
```

All tests should pass before you change anything. One test builds a real venv, so it needs
internet and takes a few seconds.

## 3. Try your copy in Claude Code

If you installed ClaudioXP from the marketplace, remove it first. With both on, every hook runs
twice:

```
claude plugin uninstall claudio@claudio-plugin
```

Then start Claude Code in any test project with your copy:

```
claude --plugin-dir /path/to/claudio-plugin/plugin
```

Your edits show up at the next session start, or after `/reload-plugins`.

## 4. How we work

We build ClaudioXP with ClaudioXP. Every change is a TDCG cycle: PLAN → SPECIFY → RED → PROMPT →
GREEN → REVIEW → REFACTOR → COMMIT. Turn it on in your clone with `/claudio:init` and let it
guide you. `.tdcg/` is not in git, so in PLAN you write your own plan and config. For the config,
use:

- test command: `cd plugin && python3 -m pytest -q`
- test files: `plugin/tests/**`

The XP practices we use:

- **Pair programming:** Claude types, you steer and decide.
- **Test first:** a failing test, then the code.
- **Refactoring:** every cycle, tests green.
- **Small releases:** one cycle, one pull request.
- **Collective ownership:** anyone can improve any part.
- **Coding standard:** `plugin/skills/claudio/craft/`.

Write plain, short English.

## 5. Open a pull request

`main` is protected: every change goes in through a pull request. Before you open one:

```
cd plugin && python3 -m pytest
claude plugin validate --strict ./plugin
```

Both must pass. Then push your branch and open the pull request; the template asks for the rest.

## Found a bug or have an idea?

[Open an issue](https://github.com/leandrodalbo/claudio-plugin/issues/new/choose). For a security
problem, see [SECURITY.md](SECURITY.md) instead.
