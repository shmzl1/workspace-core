"""Payroll model boundary.

Formal ORM models will be added after database design is approved. Payroll
states are planned as: draft -> pre_audit_generated -> pending_hr_confirmation
-> confirmed.
"""

PAYROLL_STATES = ("草稿", "已生成预审", "待 HR 确认", "已确认")
