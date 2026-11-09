"""What Claude is told before every message: where we are, as plain facts. The rules themselves
live in the claudio skill; this only says which phase file to read."""

from pathlib import Path

from tdcg.core import messages
from tdcg.core.constants import LIST_SEPARATOR
from tdcg.core.errors import TdcgError
from tdcg.core.plugin_folder import build_phase_rules_path
from tdcg.domain.phase import Phase
from tdcg.state.claudio_switch import is_claudio_on, is_off_in
from tdcg.state.phase_file import read_phase
from tdcg.state.plan_file import find_next_cycle


def build_where_we_are(project: Path) -> str | None:
    """None = Claudio is off in this project, so there is nothing to tell. A problem reading
    .tdcg/ is told with the guards' own message: Claude learns it before it hits it."""
    if not is_claudio_on(project):
        return None
    try:
        return _build_line(project)
    except TdcgError as error:
        return messages.WHERE_WE_ARE_PROBLEM.format(problem=error)


def _build_line(project: Path) -> str:
    phase = read_phase(project)
    if is_off_in(project, phase):
        return messages.WHERE_WE_ARE_OFF.format(phase=phase.value)
    if phase is Phase.PLAN:
        return messages.WHERE_WE_ARE_IN_PLAN.format(rules=build_phase_rules_path(phase.value))
    cycle = find_next_cycle(project)
    return messages.WHERE_WE_ARE_IN_CYCLE.format(
        phase=phase.value,
        key=cycle.key,
        what=cycle.what,
        type=cycle.type.value,
        files=LIST_SEPARATOR.join(cycle.files),
        rules=build_phase_rules_path(phase.value),
    )
