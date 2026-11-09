"""Small real git repos for the shell guard tests. Files are given as {path from the project: text}."""

import subprocess

from tests.support.constants import ENCODING

# Tests must not depend on the user's git settings (name, email, signing).
_GIT_TEST_SETTINGS = [
    "-c", "user.name=Claudio Tests",
    "-c", "user.email=tests@claudio.invalid",
    "-c", "commit.gpgsign=false",
]


def write_git_project(project, files):
    """A git repo in project with files committed, so they start clean."""
    _run_git(project, "init", "--quiet")
    write_project_files(project, files)
    _run_git(project, "add", "--all")
    _run_git(project, "commit", "--quiet", "--allow-empty", "-m", "start")


def write_project_files(project, files):
    for name, text in files.items():
        write_project_file(project, name, text)


def write_project_file(project, name, text):
    path = project / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=ENCODING)


def _run_git(project, *arguments):
    subprocess.run(["git", *_GIT_TEST_SETTINGS, *arguments], cwd=project, check=True)
