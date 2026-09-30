import re
import datetime
import tkinter.messagebox as messagebox
from data import Student

class Enroll:
    def __init__(self, reg_system, db):
        self.reg = reg_system
        self.db = db

    def enroll_wvalidation(self, student: Student, course):
        try:
            self.reg.enroll(student, course)
            return True, f"Successfully submitted enrollment request for '{course.name}'."
        except Exception as e:
            return False, str(e)

    def drop_wvalidation(self, student: Student, course):
        try:
            self.reg.drop(student, course)
            return True, f"Successfully dropped '{course.name}'."
        except Exception as e:
            return False, str(e)

    def get_enroll_sum(self, student_id: int, semester: int):
        enrolled = self.reg.get_student_courses(student_id, semester)
        return {
            "approved": len([r for r in enrolled if r["status"] == "approved"]),
            "pending":  len([r for r in enrolled if r["status"] == "pending"]),
            "rejected": len([r for r in enrolled if r["status"] == "rejected"]),
            "total":    len(enrolled)
        }

class SemesterTransition:
    def __init__(self, reg_system, db):
        self.reg = reg_system
        self.db = db

    def advance_possible(self, student: Student):
        if student.semester >= 2:
            return False, "You are already enrolled in the maximum available semester."

        enrolled = self.reg.get_student_courses(student.user_id, student.semester)
        approved = [r for r in enrolled if r["status"] == "approved"]

        if not approved:
            return False, "You must have at least one approved course to advance to the next semester."
        return True, "Eligible to advance."

    def advance(self, student: Student):
        can_advance, msg = self.advance_possible(student)
        if not can_advance:
            raise Exception(msg)
        return self.reg.advance_semester(student)

    def info(self, student: Student):
        current = student.semester
        new_sem = current + 1
        enrolled = self.reg.get_student_courses(student.user_id, current)
        approved = [r for r in enrolled if r["status"] == "approved"]

        return {
            "semester": current,
            "new_sem": new_sem,
            "approved_count": len(approved),
            "advance_possible": len(approved) > 0
        }

    def course_stats(self, course_id: int):
        course = self.db.fetchone("SELECT * FROM courses WHERE id=?", (course_id,))
        stats = self.db.fetchone(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) as approved, "
            "SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending, "
            "SUM(CASE WHEN status='rejected' THEN 1 ELSE 0 END) as rejected "
            "FROM enrollments WHERE course_id=?", (course_id,)
        )
        return {
            "course_name": course["name"],
            "code": course["code"],
            "capacity": course["capacity"],
            "enroll": {
                "total": stats["total"] or 0,
                "approved": stats["approved"] or 0,
                "pending": stats["pending"] or 0,
                "rejected": stats["rejected"] or 0
            }
        }

    def admin_sum(self):
        total_users = self.db.fetchone("SELECT COUNT(*) as c FROM users WHERE role='student'")["c"]
        total_courses = self.db.fetchone("SELECT COUNT(*) as c FROM courses")["c"]
        total_enrolls = self.db.fetchone("SELECT COUNT(*) as c FROM enrollments")["c"]
        pending = self.db.fetchone("SELECT COUNT(*) as c FROM enrollments WHERE status='pending'")["c"]
        approved = self.db.fetchone("SELECT COUNT(*) as c FROM enrollments WHERE status='approved'")["c"]

        return {
            "total_students": total_users,
            "total_courses": total_courses,
            "total_enrollments": total_enrolls,
            "pending_requests": pending,
            "approved_enrollments": approved
        }

class CourseMenu:
    def __init__(self, reg_system, db):
        self.reg = reg_system
        self.db = db

    def get_courses(self, student: Student, max_suggestions=10):
        current_courses = self.reg.get_student_courses(student.user_id, student.semester)
        current_codes = {r["code"] for r in current_courses}

        all_courses = self.reg.get_courses_for_semester(student.semester)
        not_enrolled = [c for c in all_courses if c.code not in current_codes]

        def sort_key(c):
            return (c.p_code is not None, c.code)
        prioritized = sorted(not_enrolled, key=sort_key)
        return prioritized[:max_suggestions]

class Validation:
    @staticmethod
    def validate_email(email: str):
        email = email.strip()
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, email):
            return False, "Please enter a valid email address (e.g. name@university.edu)."
        return True, ""

    @staticmethod
    def validate_password(password: str):
        return len(password.strip()) >= 4

    @staticmethod
    def validate_student_id(student_id: str):
        if not student_id or len(str(student_id).strip()) < 3:
            return False, "Invalid Student ID or username."
        return True, ""

class Messages:
    @staticmethod
    def success(title, message):
        messagebox.showinfo(title, message)

    @staticmethod
    def error(title, message):
        messagebox.showerror(title, message)

    @staticmethod
    def warning(title, message):
        messagebox.showwarning(title, message)

    @staticmethod
    def confirm(title, message):
        return messagebox.askyesno(title, message)

class Theme:
    """Modern Slate & Indigo UI Theme."""
    COLORS = {
        "sidebar_bg":     "#0F172A",  # Slate 900
        "sidebar_hover":  "#1E293B",  # Slate 800
        "header_bg":       "#1E293B",  # Slate 800
        "primary":        "#4F46E5",  # Indigo 600
        "primary_hover":  "#4338CA",  # Indigo 700
        "primary_light":  "#EEF2FF",  # Indigo 50
        "content_bg":     "#F8FAFC",  # Slate 50
        "card_bg":        "#FFFFFF",  # Pure White
        "card_border":    "#E2E8F0",  # Slate 200
        "text_primary":   "#0F172A",  # Slate 900
        "text_secondary": "#64748B",  # Slate 500
        "text_muted":     "#94A3B8",  # Slate 400
        "success":        "#10B981",  # Emerald 500
        "success_bg":     "#ECFDF5",  # Emerald 50
        "warning":        "#F59E0B",  # Amber 500
        "warning_bg":     "#FFFBEB",  # Amber 50
        "danger":         "#EF4444",  # Red 500
        "danger_bg":      "#FEF2F2",  # Red 50
        "info":           "#0EA5E9",  # Sky 500
        "white":          "#FFFFFF",
        "gray":           "#E2E8F0",
    }

    FONTS = {
        "title":     ("Segoe UI", 16, "bold"),
        "subtitle":  ("Segoe UI", 12, "bold"),
        "heading":   ("Segoe UI", 11, "bold"),
        "body":      ("Segoe UI", 10),
        "body_bold": ("Segoe UI", 10, "bold"),
        "small":     ("Segoe UI", 9),
        "button":    ("Segoe UI", 10, "bold"),
    }

    @classmethod
    def get_color(cls, name):
        return cls.COLORS.get(name, "#000000")

    @classmethod
    def get_font(cls, name):
        return cls.FONTS.get(name, ("Segoe UI", 10))

class Logger:
    def __init__(self):
        self.logs = []

    def log_action(self, action: str, actor: str, target: str, details: str = ""):
        self.logs.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "actor": actor,
            "target": target,
            "details": details
        })

    def get_logs(self, actor=None):
        if actor:
            return [l for l in self.logs if l["actor"] == actor]
        return self.logs

class Permission:
    PERMISSIONS = {
        "student": [
            "view_courses", "enroll_course", "drop_course",
            "view_grades", "view_transcript", "advance_semester"
        ],
        "admin": [
            "view_all_students", "approve_enrollment",
            "reject_enrollment", "assign_grades", "manage_courses",
            "view_reports", "audit_logs"
        ]
    }

    @classmethod
    def has_permission(cls, role, permission):
        return permission in cls.PERMISSIONS.get(role, [])

class DataExport:
    def __init__(self, db):
        self.db = db

    def export_enroll(self):
        return self.db.fetchall(
            "SELECT u.name, u.student_id, c.code, c.name as course_name, c.credit, e.semester, e.status, e.grade "
            "FROM enrollments e "
            "JOIN users u ON e.student_id = u.id "
            "JOIN courses c ON e.course_id = c.id "
            "ORDER BY u.name, c.code"
        )
