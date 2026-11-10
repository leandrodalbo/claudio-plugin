import pytest

from tdcg.core.errors import VenvSetupError
from tdcg.setup.venv_setup import build_venv, ensure_venv
from tests.support.constants import (
    DATA_FOLDER_NOT_SET,
    FILE_IN_THE_WAY,
    FINDING_THE_DATA_FOLDER,
    INSTALLING_THE_LIBRARIES,
    MAKING_THE_VENV,
    NEW_DATA_DIR,
    OLD_REQUIREMENTS,
    OLD_VENV_FILE,
    OTHER_PYTHON_VERSION,
    SAMPLE_HOOK_EVENT,
    SAMPLE_PIP_ERROR,
    VENV_DIR,
    VENV_PYTHON,
    VENV_SETUP_FAILED,
    VENV_UNDER_A_FILE_ERROR,
)
from tests.support.plugin_files import PLUGIN_REQUIREMENTS, load_plugin_requirements
from tests.support.venv_setups import (
    THIS_PYTHON_VERSION,
    build_done_mark,
    build_fake_venv,
    build_ready_done_mark,
    fail_in_pip,
    has_done_mark,
    load_done_mark,
    refuse_to_build,
    run_command_hook_line,
    run_setup_process,
    run_setup_process_without_data_folder,
    write_broken_venv_python,
    write_done_mark,
    write_ready_venv,
    write_venv_python,
)


# first session
def test_an_empty_data_folder_gets_a_venv(tmp_path):
    ensure_venv(tmp_path, build_fake_venv)
    assert (tmp_path / VENV_PYTHON).exists()


def test_a_data_folder_that_does_not_exist_yet_is_made(tmp_path):
    data = tmp_path / NEW_DATA_DIR
    ensure_venv(data, build_fake_venv)
    assert (data / VENV_PYTHON).exists()


def test_the_done_mark_holds_the_python_version_and_the_plugins_requirements(tmp_path):
    ensure_venv(tmp_path, build_fake_venv)
    assert load_done_mark(tmp_path) == build_ready_done_mark()


def test_the_build_gets_the_venv_folder_and_the_plugins_requirements(tmp_path):
    calls = []
    ensure_venv(tmp_path, lambda venv, requirements: calls.append((venv, requirements)))
    assert calls == [(tmp_path / VENV_DIR, PLUGIN_REQUIREMENTS)]


# ready
def test_a_ready_venv_is_not_built_again(tmp_path):
    write_ready_venv(tmp_path)
    ensure_venv(tmp_path, refuse_to_build)
    assert load_done_mark(tmp_path) == build_ready_done_mark()


# not ready: built again
def test_changed_libraries_build_the_venv_again(tmp_path):
    """A plugin update changed requirements.txt."""
    write_venv_python(tmp_path)
    write_done_mark(tmp_path, build_done_mark(THIS_PYTHON_VERSION, OLD_REQUIREMENTS))
    ensure_venv(tmp_path, build_fake_venv)
    assert load_done_mark(tmp_path) == build_ready_done_mark()


def test_a_venv_made_by_another_python_version_is_built_again(tmp_path):
    """A Python upgrade: the venv's python3 links to /usr/bin/python3, which still works, but the
    libraries were installed for the old version."""
    write_venv_python(tmp_path)
    write_done_mark(tmp_path, build_done_mark(OTHER_PYTHON_VERSION, load_plugin_requirements()))
    ensure_venv(tmp_path, build_fake_venv)
    assert load_done_mark(tmp_path) == build_ready_done_mark()


def test_a_missing_venv_python_builds_the_venv_again(tmp_path):
    write_done_mark(tmp_path, build_ready_done_mark())
    ensure_venv(tmp_path, build_fake_venv)
    assert (tmp_path / VENV_PYTHON).exists()


def test_a_broken_venv_python_builds_the_venv_again(tmp_path):
    """The Python the venv's python3 links to is gone."""
    write_broken_venv_python(tmp_path)
    write_done_mark(tmp_path, build_ready_done_mark())
    ensure_venv(tmp_path, build_fake_venv)
    assert (tmp_path / VENV_PYTHON).is_file()


def test_a_venv_built_again_starts_from_an_empty_folder(tmp_path):
    write_venv_python(tmp_path)
    (tmp_path / OLD_VENV_FILE).write_text("old", encoding="utf-8")
    write_done_mark(tmp_path, build_done_mark(THIS_PYTHON_VERSION, OLD_REQUIREMENTS))
    ensure_venv(tmp_path, build_fake_venv)
    assert not (tmp_path / OLD_VENV_FILE).exists()


# it fails
def test_a_failed_build_raises_with_the_step_and_the_error(tmp_path):
    with pytest.raises(VenvSetupError) as raised:
        ensure_venv(tmp_path, fail_in_pip)
    assert str(raised.value) == VENV_SETUP_FAILED.format(
        step=INSTALLING_THE_LIBRARIES, error=SAMPLE_PIP_ERROR
    )


def test_a_failed_build_leaves_no_done_mark(tmp_path):
    """Even a mark that matched before: the venv's python3 exists now, so an old mark would make
    the half-built venv look ready next session."""
    write_broken_venv_python(tmp_path)
    write_done_mark(tmp_path, build_ready_done_mark())
    with pytest.raises(VenvSetupError):
        ensure_venv(tmp_path, fail_in_pip)
    assert not has_done_mark(tmp_path)


def test_a_venv_that_cant_be_made_names_the_step_and_pythons_error(tmp_path):
    """The real build, failing at once with no internet needed: the venv folder is under a file."""
    blocker = tmp_path / FILE_IN_THE_WAY
    blocker.write_text("", encoding="utf-8")
    venv = blocker / VENV_DIR
    with pytest.raises(VenvSetupError) as raised:
        build_venv(venv, PLUGIN_REQUIREMENTS)
    assert str(raised.value) == VENV_SETUP_FAILED.format(
        step=MAKING_THE_VENV, error=VENV_UNDER_A_FILE_ERROR.format(path=venv)
    )


# run as Claude Code runs it
def test_a_ready_venv_says_nothing(tmp_path):
    write_ready_venv(tmp_path)
    result = run_setup_process(tmp_path)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_without_a_data_folder_the_user_is_told_on_stderr_with_exit_2():
    result = run_setup_process_without_data_folder()
    message = VENV_SETUP_FAILED.format(step=FINDING_THE_DATA_FOLDER, error=DATA_FOLDER_NOT_SET)
    assert (result.returncode, result.stdout, result.stderr) == (2, "", message + "\n")


def test_the_command_hook_line_gets_a_real_venv_and_the_untouched_event(tmp_path):
    """The one real build (internet, a few seconds): the venv is made, jsonschema works in it, the
    setup printed nothing, and the hook after it still reads the event on stdin."""
    result = run_command_hook_line(tmp_path / NEW_DATA_DIR, SAMPLE_HOOK_EVENT)
    assert (result.returncode, result.stdout, result.stderr) == (0, SAMPLE_HOOK_EVENT, "")
