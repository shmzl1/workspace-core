"""Security helper placeholders.

Authorization decisions are server-side responsibilities. This module must not
store real secrets.
"""


def mask_sensitive(value: str | None, visible_tail: int = 4) -> str | None:
    if value is None:
        return None
    if len(value) <= visible_tail:
        return "*" * len(value)
    return "*" * (len(value) - visible_tail) + value[-visible_tail:]
