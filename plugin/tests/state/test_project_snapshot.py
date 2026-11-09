from pathlib import Path

import pytest

from tdcg.core.errors import NotAGitRepoError, TdcgError
from tdcg.domain.file_stamp import FileStamp
from tdcg.state.project_snapshot import take_snapshot
from tests.support.git_projects import write_git_project, write_project_file
from tests.support.tdcg_files import write_tdcg_text


def build_stamp_of(path):
    stat = path.stat()
    return FileStamp(stat.st_mtime_ns, stat.st_size)


# what is in it
def test_clean_repo_gives_an_empty_snapshot(tmp_path):
    write_git_project(tmp_path, {"src/a.py": "a = 1"})
    assert take_snapshot(tmp_path) == {}


def test_new_file_is_in_it_with_its_time_and_size(tmp_path):
    write_git_project(tmp_path, {})
    write_project_file(tmp_path, "src/new.py", "x = 1")
    assert take_snapshot(tmp_path) == {Path("src/new.py"): build_stamp_of(tmp_path / "src/new.py")}


def test_changed_tracked_file_is_in_it(tmp_path):
    write_git_project(tmp_path, {"src/a.py": "a = 1"})
    write_project_file(tmp_path, "src/a.py", "a = 22")
    assert take_snapshot(tmp_path) == {Path("src/a.py"): build_stamp_of(tmp_path / "src/a.py")}


def test_deleted_tracked_file_is_in_it_as_gone(tmp_path):
    write_git_project(tmp_path, {"src/a.py": "a = 1"})
    (tmp_path / "src/a.py").unlink()
    assert take_snapshot(tmp_path) == {Path("src/a.py"): None}


def test_each_file_in_a_new_folder_is_in_it(tmp_path):
    write_git_project(tmp_path, {})
    write_project_file(tmp_path, "src/new/a.py", "a")
    write_project_file(tmp_path, "src/new/deeper/b.py", "b")
    assert set(take_snapshot(tmp_path)) == {Path("src/new/a.py"), Path("src/new/deeper/b.py")}


def test_odd_file_names_are_read_as_they_are(tmp_path):
    write_git_project(tmp_path, {})
    write_project_file(tmp_path, "src/my file é.py", "a")
    assert set(take_snapshot(tmp_path)) == {Path("src/my file é.py")}


# what is left out
def test_git_ignored_files_are_left_out(tmp_path):
    write_git_project(tmp_path, {".gitignore": "__pycache__/\nbuild/\n"})
    write_project_file(tmp_path, "src/__pycache__/a.cpython-313.pyc", "x")
    write_project_file(tmp_path, "build/out.txt", "x")
    assert take_snapshot(tmp_path) == {}


def test_only_files_inside_the_project_folder_count(tmp_path):
    """The project can be a folder inside a bigger repo; paths count from the project folder."""
    project = tmp_path / "apps/shop"
    write_git_project(tmp_path, {"apps/shop/a.py": "a", "other/b.py": "b"})
    write_project_file(tmp_path, "apps/shop/a.py", "a changed")
    write_project_file(tmp_path, "other/b.py", "b changed")
    assert set(take_snapshot(project)) == {Path("a.py")}


# .tdcg/
def test_tdcg_files_are_in_it(tmp_path):
    write_git_project(tmp_path, {})
    write_tdcg_text(tmp_path, "phase", "RED")
    assert Path(".tdcg/phase") in take_snapshot(tmp_path)


def test_tdcg_files_are_in_it_even_when_git_ignores_them(tmp_path):
    write_git_project(tmp_path, {".gitignore": ".tdcg/\n"})
    write_tdcg_text(tmp_path, "phase", "RED")
    write_tdcg_text(tmp_path, "done/old.json", "{}")
    assert take_snapshot(tmp_path) == {
        Path(".tdcg/phase"): build_stamp_of(tmp_path / ".tdcg/phase"),
        Path(".tdcg/done/old.json"): build_stamp_of(tmp_path / ".tdcg/done/old.json"),
    }


# no git repo
def test_folder_that_is_not_a_git_repo_raises(tmp_path):
    with pytest.raises(NotAGitRepoError, match="not a git repo"):
        take_snapshot(tmp_path)


def test_not_a_git_repo_is_a_claudio_error():
    assert issubclass(NotAGitRepoError, TdcgError)
