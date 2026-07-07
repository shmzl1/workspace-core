"""File storage path helpers.

The current skeleton only normalizes configured storage roots. Upload, report
and policy handling must be implemented in services with permission checks.
"""

from pathlib import Path


def ensure_relative_storage_root(root: str) -> Path:
    path = Path(root)
    if path.is_absolute():
        return path
    return Path.cwd() / path
