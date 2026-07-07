"""Payroll repository boundary.

Repositories will own database reads and writes only. Salary access checks must
be orchestrated by services before repository access.
"""


class PayrollRepository:
    """Placeholder repository boundary without SQLAlchemy models."""

    pass
