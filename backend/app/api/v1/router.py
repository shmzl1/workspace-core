"""API v1 router aggregation.

Endpoint modules only expose route boundaries here. Business orchestration must
flow through Services and Repositories.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    agent,
    analytics,
    attendance,
    audit,
    auth,
    employee,
    interview,
    payroll,
    payroll_review,
    policy,
    recruitment,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(employee.router, prefix="/employees", tags=["employees"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(policy.router, prefix="/policies", tags=["policies"])
api_router.include_router(payroll.router, prefix="/payroll", tags=["payroll"])
api_router.include_router(payroll_review.router, prefix="/payroll-review", tags=["payroll-review"])
api_router.include_router(recruitment.router, prefix="/recruitment", tags=["recruitment"])
api_router.include_router(interview.router, prefix="/interviews", tags=["interviews"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
