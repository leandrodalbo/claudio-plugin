"""Projects with Claudio on: .tdcg/ with the sample plan and config, in a given phase."""

from tests.support.git_projects import write_git_project
from tests.support.sample_configs import build_valid_config
from tests.support.sample_plans import build_valid_plan
from tests.support.tdcg_files import write_tdcg_state

# Git ignores what Python and pytest write, as a real project does.
GITIGNORE = "__pycache__/\n.pytest_cache/\n"


def write_project_in(project, phase):
    write_tdcg_state(project, phase, build_valid_plan(), build_valid_config())


def write_git_project_in(project, phase, files):
    """A git repo with files committed and .gitignore, then .tdcg/ (not committed) in phase."""
    write_git_project(project, {".gitignore": GITIGNORE, **files})
    write_project_in(project, phase)
