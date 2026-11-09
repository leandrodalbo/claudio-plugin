from enum import Enum


class Phase(Enum):
    """The order here is the TDCG order."""

    PLAN = "PLAN"
    SPECIFY = "SPECIFY"
    RED = "RED"
    PROMPT = "PROMPT"
    GREEN = "GREEN"
    REVIEW = "REVIEW"
    REFACTOR = "REFACTOR"
    COMMIT = "COMMIT"

    @property
    def is_skippable(self) -> bool:
        """Only the user skips (/claudio:next --skipTo), and only these. Every other phase must
        happen: you need the spec, the prompt, passing tests, and a commit."""
        return self in _SKIPPABLE


_SKIPPABLE = frozenset({Phase.REVIEW, Phase.REFACTOR})
