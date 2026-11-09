from dataclasses import dataclass, field


@dataclass(frozen=True)
class Config:
    test_command: str
    test_files: list[str]
    claude_free_writing_files: list[str] = field(default_factory=list)
