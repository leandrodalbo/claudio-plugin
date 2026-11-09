import tempfile

import pytest


@pytest.fixture
def temp_folder(tmp_path, monkeypatch):
    """The system temp folder for this test only, so shell snapshots never land in the real one.
    Python's tempfile reads its folder from `tempfile.tempdir` once set."""
    folder = tmp_path / "system-temp"
    folder.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(folder))
    return folder
