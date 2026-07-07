"""Import ORM model modules so Alembic can discover metadata."""

from app.modules.attendance import models as attendance_models
from app.modules.audit import models as audit_models
from app.modules.auth import models as auth_models
from app.modules.employee import models as employee_models
from app.modules.interview import models as interview_models
from app.modules.notification import models as notification_models
from app.modules.payroll import models as payroll_models
from app.modules.policy import models as policy_models
from app.modules.recruitment import models as recruitment_models

__all__ = [
    "attendance_models",
    "audit_models",
    "auth_models",
    "employee_models",
    "interview_models",
    "notification_models",
    "payroll_models",
    "policy_models",
    "recruitment_models",
]
