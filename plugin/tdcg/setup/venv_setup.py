"""The plugin's own venv, so people never install a library by hand. Plain Python only: it runs
before the venv exists. It never reads stdin, so the hook after it on the same line still gets
Claude Code's event."""

import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import (
    BLOCK_EXIT_CODE,
    MAKE_VENV,
    PIP_INSTALL,
    PLUGIN_DATA_VARIABLE,
    REQUIREMENTS_FILE,
    VENV_DIR,
    VENV_PYTHON,
)
from tdcg.core.errors import TdcgError, VenvSetupError
from tdcg.core.plugin_folder import REQUIREMENTS_PATH


def build_venv(venv: Path, requirements: Path) -> None:
    """Makes the venv with the Python running this, then installs the pinned libraries into it.
    Raises VenvSetupError naming the step that failed."""
    _run_step(messages.MAKING_THE_VENV, [sys.executable, *MAKE_VENV, str(venv)])
    pip_command = [str(venv.joinpath(*VENV_PYTHON)), *PIP_INSTALL, str(requirements)]
    _run_step(messages.INSTALLING_THE_LIBRARIES, pip_command)


def ensure_venv(data: Path, build: Callable[[Path, Path], None] = build_venv) -> None:
    """Returns quietly when the venv is ready. Otherwise builds it again from nothing; the done
    mark is deleted first and written last, so a build that stops half way is never taken for
    ready. Raises VenvSetupError when the build fails."""
    mark = data / REQUIREMENTS_FILE
    venv = data / VENV_DIR
    if _is_ready(venv, mark):
        return
    mark.unlink(missing_ok=True)
    shutil.rmtree(venv, ignore_errors=True)
    data.mkdir(parents=True, exist_ok=True)
    build(venv, REQUIREMENTS_PATH)
    shutil.copyfile(REQUIREMENTS_PATH, mark)


def _is_ready(venv: Path, mark: Path) -> bool:
    """The venv's python3 is there (a link to a Python that is gone counts as missing) and it was
    built from the plugin's requirements.txt as it is now."""
    if not venv.joinpath(*VENV_PYTHON).exists() or not mark.exists():
        return False
    return mark.read_bytes() == REQUIREMENTS_PATH.read_bytes()


def _run_step(step: str, command: list[str]) -> None:
    """Output is kept, never printed: at session start, what a hook prints goes to Claude."""
    finished = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    if finished.returncode != 0:
        raise VenvSetupError(step, _find_last_error_line(finished))


def _find_last_error_line(finished: subprocess.CompletedProcess) -> str:
    """The last words on stderr say what went wrong; with none, the exit code."""
    lines = finished.stderr.strip().splitlines()
    if not lines:
        return messages.STEP_EXIT_CODE.format(code=finished.returncode)
    return lines[-1]


def _find_data_folder() -> Path:
    data = os.environ.get(PLUGIN_DATA_VARIABLE)
    if not data:
        raise VenvSetupError(messages.FINDING_THE_DATA_FOLDER, messages.DATA_FOLDER_NOT_SET)
    return Path(data)


def _set_up() -> None:
    ensure_venv(_find_data_folder())


def main() -> None:
    """Claude Code runs this at session start, and before each /claudio: command, in hooks.json.
    Ready: prints nothing, exit 0. Failed: the message on stderr, exit 2, which the user sees.
    Any other error is a bug and stops it as Python does; the guards don't need the venv."""
    try:
        _set_up()
    except TdcgError as error:
        print(error, file=sys.stderr)
        sys.exit(BLOCK_EXIT_CODE)


if __name__ == "__main__":
    main()
