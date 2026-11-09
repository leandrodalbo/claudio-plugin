import getpass
from pathlib import Path

from tdcg.domain.file_stamp import FileStamp
from tdcg.state.shell_snapshot_file import load_snapshot, remove_snapshot, write_snapshot
from tests.support.constants import SNAPSHOT_DIR


def build_snapshot():
    return {
        Path("src/a.py"): FileStamp(1_700_000_000_123_456_789, 42),
        Path("src/my file é.py"): FileStamp(1_700_000_000_000_000_001, 0),
        Path("src/gone.py"): None,
    }


def test_written_snapshot_loads_back_the_same(temp_folder):
    write_snapshot("toolu_01", build_snapshot())
    assert load_snapshot("toolu_01") == build_snapshot()


def test_empty_snapshot_loads_back_empty(temp_folder):
    write_snapshot("toolu_01", {})
    assert load_snapshot("toolu_01") == {}


def test_missing_snapshot_loads_as_none(temp_folder):
    assert load_snapshot("toolu_01") is None


def test_snapshot_lives_in_a_temp_folder_per_user_under_its_call_id(temp_folder):
    """Not in .tdcg/: it would be a change itself, and `rm -rf .tdcg` would wipe it. Per user:
    on Linux /tmp is shared, and a folder made by another user can't be written."""
    write_snapshot("toolu_01", build_snapshot())
    assert (temp_folder / f"{SNAPSHOT_DIR}-{getpass.getuser()}" / "toolu_01.json").is_file()


def test_each_call_id_has_its_own_snapshot(temp_folder):
    write_snapshot("toolu_01", build_snapshot())
    write_snapshot("toolu_02", {})
    assert load_snapshot("toolu_01") == build_snapshot()
    assert load_snapshot("toolu_02") == {}


def test_removed_snapshot_is_gone(temp_folder):
    write_snapshot("toolu_01", build_snapshot())
    remove_snapshot("toolu_01")
    assert load_snapshot("toolu_01") is None


def test_removing_a_missing_snapshot_is_fine(temp_folder):
    remove_snapshot("toolu_01")
    assert load_snapshot("toolu_01") is None
