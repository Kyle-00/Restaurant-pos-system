"""
Employee Scheduling & Payroll
-----------------------------
Manages shifts, clock in/out, and calculates hours worked.
"""

from database import Database

# All methods are in Database class already.
# This file is just a wrapper for clarity.
class EmployeeScheduler:
    @staticmethod
    def add_shift(user_id, shift_date, start_time, end_time, notes=""):
        return Database.add_shift(user_id, shift_date, start_time, end_time, notes)

    @staticmethod
    def clock_in(user_id, notes=""):
        return Database.clock_in(user_id, notes)

    @staticmethod
    def clock_out(user_id, notes=""):
        return Database.clock_out(user_id, notes)

    @staticmethod
    def get_hours_worked(user_id, start_date, end_date):
        return Database.get_hours_worked(user_id, start_date, end_date)