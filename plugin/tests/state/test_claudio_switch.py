import pytest

from tdcg.domain.phase import Phase
from tdcg.state.claudio_switch import is_claudio_on, is_off_in, turn_back_on, turn_off_in
from tests.support.constants import OFF_IN_PHASE_FILE, TDCG_DIR
from tests.support.tdcg_files import has_tdcg_path, write_tdcg_text


# is Claudio on in this project?
def test_claudio_is_off_without_a_tdcg_folder(tmp_path):
    assert not is_claudio_on(tmp_path)


def test_claudio_is_on_with_a_tdcg_folder(tmp_path):
    (tmp_path / TDCG_DIR).mkdir()
    assert is_claudio_on(tmp_path)


def test_a_tdcg_file_is_not_a_tdcg_folder(tmp_path):
    (tmp_path / TDCG_DIR).write_text("")
    assert not is_claudio_on(tmp_path)


# off after a bug, for one phase
def test_not_off_when_no_bug_happened(tmp_path):
    (tmp_path / TDCG_DIR).mkdir()
    assert not is_off_in(tmp_path, Phase.GREEN)


def test_off_in_the_phase_of_the_bug(tmp_path):
    (tmp_path / TDCG_DIR).mkdir()
    turn_off_in(tmp_path, Phase.GREEN)
    assert is_off_in(tmp_path, Phase.GREEN)


@pytest.mark.parametrize("phase", [Phase.RED, Phase.REFACTOR])
def test_back_on_in_any_other_phase(tmp_path, phase):
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    assert not is_off_in(tmp_path, phase)


def test_turn_back_on_removes_the_off_file(tmp_path):
    write_tdcg_text(tmp_path, OFF_IN_PHASE_FILE, "GREEN")
    turn_back_on(tmp_path)
    assert not has_tdcg_path(tmp_path, OFF_IN_PHASE_FILE)


def test_turn_back_on_when_already_on_is_fine(tmp_path):
    (tmp_path / TDCG_DIR).mkdir()
    turn_back_on(tmp_path)
