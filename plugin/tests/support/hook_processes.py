"""Running a hook as Claude Code does: a new Python process, the event as JSON on stdin."""

import io
import json
import os
import subprocess
import sys
from pathlib import Path

import tdcg

PLUGIN_DIR = Path(tdcg.__file__).parent.parent
PROJECT_DIR_VARIABLE = "CLAUDE_PROJECT_DIR"
# Python's tempfile reads the system temp folder from TMPDIR, so tests never use the real one.
TEMP_DIR_VARIABLE = "TMPDIR"


def run_hook(module, project, event, temp_folder):
    return run_hook_process(module, json.dumps(event), build_environment_for(project, temp_folder))


def run_hook_process(module, stdin_text, environment):
    return subprocess.run(
        [sys.executable, "-m", module],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=PLUGIN_DIR,
        env=environment,
    )


def find_modules_loaded_by(module):
    """Names in sys.modules after importing module in a fresh Python (pytest has loaded others)."""
    script = (
        "import importlib, json, sys; "
        f"importlib.import_module({module!r}); "
        "print(json.dumps(list(sys.modules)))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, cwd=PLUGIN_DIR, check=True
    )
    return set(json.loads(result.stdout))


def build_environment_for(project, temp_folder):
    return {**os.environ, PROJECT_DIR_VARIABLE: str(project), TEMP_DIR_VARIABLE: str(temp_folder)}


def build_environment_without_project(temp_folder):
    environment = build_environment_for("", temp_folder)
    del environment[PROJECT_DIR_VARIABLE]
    return environment


def make_crash(monkeypatch, module, name):
    """Replaces module.name with a function that raises an error Claudio did not expect."""

    def crash(*arguments):
        raise KeyError("something Claudio did not expect")

    monkeypatch.setattr(module, name, crash)


def run_hook_main_here(hook, event, project, monkeypatch, capsys):
    """A hook's main in this test's own process (so a part of it can be made to crash), with the
    event on stdin as Claude Code sends it. Gives back what it printed, read as JSON."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(event)))
    monkeypatch.setenv(PROJECT_DIR_VARIABLE, str(project))
    hook.main()
    return json.loads(capsys.readouterr().out)
