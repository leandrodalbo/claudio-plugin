"""The snapshot taken before a shell command, kept until the after hook reads it. It lives in the
system temp folder, not in .tdcg/: there it would be a change itself, and `rm -rf .tdcg` would
wipe it. One folder per user, one file per tool call, named by Claude Code's tool_use_id."""

import getpass
import json
import tempfile
from dataclasses import astuple
from pathlib import Path

from tdcg.core.constants import ENCODING, JSON_EXTENSION, SNAPSHOT_DIR
from tdcg.domain.file_stamp import FileStamp, Snapshot


def write_snapshot(call_id: str, snapshot: Snapshot) -> None:
    path = _build_snapshot_path(call_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    stamps = {}
    for file, stamp in snapshot.items():
        stamps[file.as_posix()] = _build_json_from_stamp(stamp)
    path.write_text(json.dumps(stamps), encoding=ENCODING)


def load_snapshot(call_id: str) -> Snapshot | None:
    """None when no snapshot was saved for this call."""
    path = _build_snapshot_path(call_id)
    if not path.exists():
        return None
    snapshot = {}
    for name, stamp in json.loads(path.read_text(encoding=ENCODING)).items():
        snapshot[Path(name)] = _build_stamp_from_json(stamp)
    return snapshot


def remove_snapshot(call_id: str) -> None:
    _build_snapshot_path(call_id).unlink(missing_ok=True)


def _build_snapshot_path(call_id: str) -> Path:
    folder = f"{SNAPSHOT_DIR}-{getpass.getuser()}"
    return Path(tempfile.gettempdir()) / folder / f"{call_id}{JSON_EXTENSION}"


def _build_json_from_stamp(stamp: FileStamp | None) -> list[int] | None:
    if stamp is None:
        return None
    return list(astuple(stamp))


def _build_stamp_from_json(stamp: list[int] | None) -> FileStamp | None:
    if stamp is None:
        return None
    return FileStamp(*stamp)
