"""The plugin's data folder in a test: venvs that are ready, old or broken, and fake builds, so
only one test pays for a real venv."""

import os
import subprocess
import sys

from tdcg.core.errors import VenvSetupError
from tests.support.constants import (
    DONE_MARK,
    ENCODING,
    INSTALLING_THE_LIBRARIES,
    PLUGIN_DATA_VARIABLE,
    SAMPLE_PIP_ERROR,
    VENV_PYTHON,
)
from tests.support.hook_processes import PLUGIN_DIR
from tests.support.plugin_files import load_plugin_requirements

SETUP_MODULE = "tdcg.setup.venv_setup"


def write_venv_python(data):
    python = data / VENV_PYTHON
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text("", encoding=ENCODING)


def write_broken_venv_python(data):
    """What a Python upgrade leaves: the venv's python3 links to a Python that is gone."""
    python = data / VENV_PYTHON
    python.parent.mkdir(parents=True, exist_ok=True)
    python.symlink_to(data / "python3.gone")


def write_done_mark(data, text):
    data.mkdir(parents=True, exist_ok=True)
    (data / DONE_MARK).write_text(text, encoding=ENCODING)


def write_ready_venv(data):
    write_venv_python(data)
    write_done_mark(data, load_plugin_requirements())


def has_done_mark(data):
    return (data / DONE_MARK).exists()


def load_done_mark(data):
    return (data / DONE_MARK).read_text(encoding=ENCODING)


# Fake builds, passed to ensure_venv in place of the real one
def build_fake_venv(venv, requirements):
    """Makes only the venv's python3, as a real build would."""
    python = venv / "bin" / "python3"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text("", encoding=ENCODING)


def fail_in_pip(venv, requirements):
    """Makes the venv's python3, then fails the way pip does with no internet."""
    build_fake_venv(venv, requirements)
    raise VenvSetupError(INSTALLING_THE_LIBRARIES, SAMPLE_PIP_ERROR)


def refuse_to_build(venv, requirements):
    raise AssertionError("the venv was built again")


# Running it as Claude Code does
def run_setup_process(data):
    environment = {**os.environ, PLUGIN_DATA_VARIABLE: str(data)}
    return _run_setup(environment)


def run_setup_process_without_data_folder():
    environment = dict(os.environ)
    environment.pop(PLUGIN_DATA_VARIABLE, None)
    return _run_setup(environment)


def _run_setup(environment):
    return subprocess.run(
        [sys.executable, "-m", SETUP_MODULE],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        cwd=PLUGIN_DIR,
        env=environment,
    )


def run_command_hook_line(data, event):
    """The command hook's line from hooks.json, with a stand-in for the hook that imports jsonschema
    and gives back the event it read: the real thing, a real venv and real pip."""
    line = (
        f'"{sys.executable}" -m {SETUP_MODULE} && '
        f'"${{{PLUGIN_DATA_VARIABLE}}}/{VENV_PYTHON}" '
        "-c \"import sys, jsonschema; print(sys.stdin.read(), end='')\""
    )
    environment = {**os.environ, PLUGIN_DATA_VARIABLE: str(data)}
    return subprocess.run(
        line,
        shell=True,
        input=event,
        capture_output=True,
        text=True,
        cwd=PLUGIN_DIR,
        env=environment,
    )
