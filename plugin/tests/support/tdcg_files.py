"""Files inside a project's .tdcg folder. `name` is the path inside it, e.g. PLAN_FILE or "done/x.json"."""

import json

from tests.support.constants import CONFIG_FILE, ENCODING, JSON_INDENT, PHASE_FILE, PLAN_FILE, TDCG_DIR


def write_tdcg_json(project, name, data):
    write_tdcg_text(project, name, json.dumps(data, indent=JSON_INDENT, ensure_ascii=False))


def write_tdcg_text(project, name, text):
    _build_parent_dir_path(project, name).mkdir(parents=True, exist_ok=True)
    _build_tdcg_path(project, name).write_text(text, encoding=ENCODING)


def write_tdcg_bytes(project, name, data):
    """For files that are not valid UTF-8, which write_tdcg_text can't make."""
    _build_parent_dir_path(project, name).mkdir(parents=True, exist_ok=True)
    _build_tdcg_path(project, name).write_bytes(data)


def write_tdcg_state(project, phase, plan, config):
    """Phase, plan and config together, as a project in the middle of a cycle has them."""
    write_tdcg_text(project, PHASE_FILE, phase)
    write_tdcg_json(project, PLAN_FILE, plan)
    write_tdcg_json(project, CONFIG_FILE, config)


def load_tdcg_json(project, name):
    return json.loads(load_tdcg_text(project, name))


def load_tdcg_text(project, name):
    return _build_tdcg_path(project, name).read_text(encoding=ENCODING)


def has_tdcg_path(project, name):
    return _build_tdcg_path(project, name).exists()


def _build_tdcg_path(project, name):
    return project / TDCG_DIR / name


def _build_parent_dir_path(project, name):
    return _build_tdcg_path(project, name).parent
