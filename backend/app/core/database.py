"""Database boundary placeholders.

Repositories will own database reads and writes. Routes, Agents and Tools must
not import ORM sessions directly from here.
"""

from collections.abc import Iterator


def get_db_session() -> Iterator[None]:
    """Placeholder dependency until SQLAlchemy session wiring is implemented."""
    yield None
