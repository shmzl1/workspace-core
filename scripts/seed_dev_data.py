import sys
import os
from datetime import date, time

# Add backend directory to sys.path to allow imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.modules.auth.models import User
from app.modules.employee.models import Employee, LeaveBalance
from app.modules.payroll.models import SalaryRecord
from app.modules.attendance.models import WorkCalendar
from passlib.hash import bcrypt

def seed_data():
    db: Session = SessionLocal()
    try:
        # Clear existing data to allow re-runs
        print("Clearing existing data...")
        db.query(SalaryRecord).delete()
        db.query(LeaveBalance).delete()
        db.query(Employee).delete()
        db.query(User).delete()
        db.query(WorkCalendar).delete()
        db.commit()

        print("Seeding Users...")
        # Hash password 'password'
        password_hash = bcrypt.hash("password")
        
        u1 = User(id=1, username="zhangwei", password_hash=password_hash, role="EMPLOYEE")
        u2 = User(id=2, username="liming", password_hash=password_hash, role="DEPARTMENT_MANAGER")
        u3 = User(id=3, username="linyuqing", password_hash=password_hash, role="HR_SPECIALIST")
        u4 = User(id=4, username="wangqiang", password_hash=password_hash, role="PAYROLL_ADMIN")
        
        db.add_all([u1, u2, u3, u4])
        db.commit()

        print("Seeding Employees...")
        # Managers first
        emp2 = Employee(id=2, user_id=2, employee_no="EMP002", full_name="李明", department="研发部", job_title="研发经理", employment_status="ACTIVE")
        db.add(emp2)
        db.commit()

        emp1 = Employee(id=1, user_id=1, employee_no="EMP001", full_name="张伟", department="研发部", job_title="高级开发工程师", manager_employee_id=2, employment_status="ACTIVE")
        emp3 = Employee(id=3, user_id=3, employee_no="EMP003", full_name="林雨晴", department="人力资源部", job_title="HR专员", employment_status="ACTIVE")
        emp4 = Employee(id=4, user_id=4, employee_no="EMP004", full_name="王强", department="财务部", job_title="薪酬管理员", employment_status="ACTIVE")

        db.add_all([emp1, emp3, emp4])
        db.commit()

        print("Seeding Leave Balances...")
        lb1 = LeaveBalance(employee_id=1, leave_type="ANNUAL", year=2026, total_days=10, used_days=0)
        lb2 = LeaveBalance(employee_id=2, leave_type="ANNUAL", year=2026, total_days=15, used_days=0)
        db.add_all([lb1, lb2])
        db.commit()

        print("Seeding Salary Records...")
        s1 = SalaryRecord(employee_id=1, base_salary=25000.00, currency="CNY", effective_from=date(2026, 1, 1), created_by_user_id=4)
        s2 = SalaryRecord(employee_id=2, base_salary=35000.00, currency="CNY", effective_from=date(2026, 1, 1), created_by_user_id=4)
        s3 = SalaryRecord(employee_id=3, base_salary=18000.00, currency="CNY", effective_from=date(2026, 1, 1), created_by_user_id=4)
        s4 = SalaryRecord(employee_id=4, base_salary=20000.00, currency="CNY", effective_from=date(2026, 1, 1), created_by_user_id=4)
        db.add_all([s1, s2, s3, s4])
        db.commit()

        print("Seeding Work Calendars...")
        today = date.today()
        # Seed calendars from 7 days ago to 7 days ahead
        for i in range(-7, 8):
            day = today + timedelta(days=i)
            # Default weekends as non-workdays, weekdays as workdays
            is_workday = day.weekday() < 5
            wc = WorkCalendar(
                calendar_date=day,
                is_workday=is_workday,
                standard_check_in_time=time(9, 0),
                standard_check_out_time=time(18, 0),
                late_grace_minutes=0,
                holiday_name=None if is_workday else "周末休息"
            )
            db.add(wc)
        db.commit()

        print("Database Seeding Completed Successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import timedelta
    seed_data()
