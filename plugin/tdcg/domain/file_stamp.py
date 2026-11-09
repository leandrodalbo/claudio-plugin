from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileStamp:
    """When a file was last written and its size: enough to see that a command changed it."""

    modified_ns: int
    size: int


# Each changed file, by its path from the project folder.
# None = gone (git knows it, the disk doesn't).
Snapshot = dict[Path, FileStamp | None]
