from dataclasses import dataclass

from tdcg.domain.cycle import Cycle
from tdcg.domain.plan_status import PlanStatus


@dataclass(frozen=True)
class Plan:
    title: str
    status: PlanStatus
    goal: str
    cycles: list[Cycle]
