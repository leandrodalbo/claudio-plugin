import subprocess
from pathlib import Path

from tdcg.core.constants import ENCODING, GIT_LIST_CHANGED_FILES, NUL, TDCG_DIR
from tdcg.core.errors import NotAGitRepoError
from tdcg.domain.file_stamp import FileStamp, Snapshot


def take_snapshot(project: Path) -> Snapshot:
    """Every file git sees as changed or new in the project, plus every file in .tdcg/ (git may
    ignore it), each with its stamp. Git-ignored files are left out."""
    snapshot = {}
    for relative in _list_git_changed_files(project) + _list_tdcg_files(project):
        snapshot[relative] = _load_stamp(project / relative)
    return snapshot


def _list_git_changed_files(project: Path) -> list[Path]:
    result = subprocess.run(
        GIT_LIST_CHANGED_FILES, cwd=project, capture_output=True, encoding=ENCODING
    )
    if result.returncode != 0:
        raise NotAGitRepoError(project)
    # Each name ends with NUL, so the last piece after splitting is always empty.
    names = result.stdout.split(NUL)[:-1]
    return [Path(name) for name in names]


def _list_tdcg_files(project: Path) -> list[Path]:
    tdcg_files = []
    for path in (project / TDCG_DIR).rglob("*"):
        if path.is_file():
            tdcg_files.append(path.relative_to(project))
    return tdcg_files


def _load_stamp(path: Path) -> FileStamp | None:
    if not path.exists():
        return None
    stat = path.stat()
    return FileStamp(stat.st_mtime_ns, stat.st_size)
