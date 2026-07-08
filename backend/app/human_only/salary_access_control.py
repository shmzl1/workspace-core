def check_salary_access(
    actor_role: str,
    actor_employee_id: int | None,
    target_employee_id: int,
    target_department: str,
    relation: str | None = None
) -> dict:
    """
    Core salary access control rules.
    Returns a dict with:
      - allowed (bool)
      - accessible_fields (list[str])
      - reason (str)
    """
    # Rule 1: Self access (Employee checking their own salary)
    if actor_employee_id == target_employee_id:
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "reason": "允许员工查询本人薪资信息"
        }
    
    # Rule 2: Payroll Admin access (Full access to all salaries)
    if actor_role == "PAYROLL_ADMIN":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "reason": "允许薪酬管理员查询所有薪资信息"
        }
        
    # Rule 3: HR Specialist access (Can query all salary records but effective_to is masked)
    if actor_role == "HR_SPECIALIST":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from"],
            "reason": "允许HR专员查询薪资信息（已脱敏截止日期）"
        }
        
    # Rule 4: Department Manager access (Can query employees in their department, only base_salary and currency visible)
    if actor_role == "DEPARTMENT_MANAGER" and relation == "manager":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency"],
            "reason": "允许部门经理查询本部门员工薪资信息（仅基本工资与币种）"
        }
        
    # Rule 5: Default fallback (Deny access)
    return {
        "allowed": False,
        "accessible_fields": [],
        "reason": "无权访问此员工的薪资数据"
    }
