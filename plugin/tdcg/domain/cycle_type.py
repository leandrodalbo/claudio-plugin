from enum import Enum
from types import MappingProxyType

from tdcg.core.errors import PhaseNotInRouteError
from tdcg.domain.phase import Phase
from tdcg.domain.test_result import TestResult


class CycleType(Enum):
    """Set in the plan, per cycle. The type sets the cycle's route: a phase not on it is not a
    skip, the plan already says so."""

    BEHAVIOUR = "behaviour"
    COVERAGE = "coverage"
    REFACTOR = "refactor"
    DOCUMENTATION = "documentation"
    SETUP = "setup"
    SPIKE = "spike"

    @property
    def route(self) -> list[Phase]:
        """The cycle's phases, in the order of the Phase enum."""
        route = []
        for phase in Phase:
            if self._is_on_route(phase):
                route.append(phase)
        return route

    @property
    def steps(self) -> list[Phase]:
        """What a project walks through: PLAN, then the cycle's route."""
        return [Phase.PLAN] + self.route

    def ensure_has_step(self, phase: Phase) -> None:
        if phase not in self.steps:
            raise PhaseNotInRouteError(phase.value, self.value)

    def expect_when_leaving(self, phase: Phase) -> TestResult | None:
        """What the test command must give before the cycle leaves `phase`. None = the command
        doesn't run: only RED, GREEN and REFACTOR are checked."""
        self.ensure_has_step(phase)
        if phase is Phase.RED:
            return _EXPECTED_WHEN_LEAVING_RED[self]
        return _EXPECTED_WHEN_LEAVING.get(phase)

    def _is_on_route(self, phase: Phase) -> bool:
        """PLAN belongs to the plan, not to a cycle. Only some types write tests first (RED)."""
        if phase is Phase.PLAN:
            return False
        if phase is Phase.RED:
            return self in _EXPECTED_WHEN_LEAVING_RED
        return True


_EXPECTED_WHEN_LEAVING = MappingProxyType({
    Phase.GREEN: TestResult.PASS,
    Phase.REFACTOR: TestResult.PASS,
})
"""The same for every type. RED depends on the type, so it has its own table."""

_EXPECTED_WHEN_LEAVING_RED = MappingProxyType({
    CycleType.BEHAVIOUR: TestResult.FAIL,
    CycleType.COVERAGE: TestResult.PASS,
})
"""Behaviour tests are new, so they must fail first. Coverage tests are for code that already
works, so they must pass. A type not here has no RED."""
