from dataclasses import dataclass

from tdcg.domain.cycle_type import CycleType


@dataclass(frozen=True)
class Cycle:
    key: str
    what: str
    done: bool
    notes: list[str]
    files: list[str]
    type: CycleType = CycleType.BEHAVIOUR
