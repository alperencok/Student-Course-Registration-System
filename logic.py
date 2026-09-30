from data import User, Student, Admin, Course
from academic import AcademicEngine

class AppError(Exception):
    pass
class AuthError(AppError):
    pass
class ScheduleConflictError(AppError):
    pass
class PrerequisiteError(AppError):
    pass
class CapacityError(AppError):
    pass
class AlreadyEnrolledError(AppError):
    pass

class Auth:
    def __init__(self, db):
        self.db = db

    def login(self, identifier: str, password: str):
        identifier = identifier.strip()
        password = password.strip()
        row = self.db.fetchone(
            "SELECT * FROM users WHERE (email=? OR student_id=?) AND password=?",
            (identifier, identifier, password)
        )
        if not row:
            return None
        if row["role"] == "admin":
            return Admin(user_id=row["id"], email=row["email"], full_name=row["name"])
        return Student(
            user_id=row["id"],
            email=row["email"],
            full_name=row["name"],
            student_id=row["student_id"],
            semester=row["semester"],
        )

def _row_to_course(row) -> Course:
    return Course(
        course_id=row["id"],
        code=row["code"],
        name=row["name"],
        credit=row["credit"],
        semesters=row["semesters"],
        p_code=row["p_code"],
        day=row["day"],
        t_start=row["t_start"],
        t_end=row["t_end"],
        capacity=row["capacity"],
    )

class Registration:
    def __init__(self, db):
        self.db = db

    def get_courses_for_semester(self, semester: int):
        rows = self.db.fetchall(
            "SELECT * FROM courses WHERE semesters=? ORDER BY day, t_start",
            (semester,)
        )
        return [_row_to_course(r) for r in rows]

    def get_enrollment_status(self, student_id: int, course_id: int):
        row = self.db.fetchone(
            "SELECT status FROM enrollments WHERE student_id=? AND course_id=?",
            (student_id, course_id)
        )
        return row["status"] if row else None

    def get_student_courses(self, student_id: int, semester: int):
        """Returns courses for a specific semester with status and grade."""
        rows = self.db.fetchall(
            "SELECT c.*, e.id as enrollment_id, e.status, e.grade, e.grade_point "
            "FROM courses c "
            "JOIN enrollments e ON c.id = e.course_id "
            "WHERE e.student_id=? AND c.semesters=? "
            "ORDER BY c.day, c.t_start",
            (student_id, semester)
        )
        return rows

    def get_student_transcript(self, student_id: int):
        """Returns all completed or enrolled courses across all semesters with grades."""
        rows = self.db.fetchall(
            "SELECT c.*, e.id as enrollment_id, e.semester as enrolled_semester, "
            "e.status, e.grade, e.grade_point "
            "FROM courses c "
            "JOIN enrollments e ON c.id = e.course_id "
            "WHERE e.student_id=? "
            "ORDER BY e.semester, c.code",
            (student_id,)
        )
        return rows

    def enroll(self, student: Student, course: Course):
        status = self.get_enrollment_status(student.user_id, course.course_id)
        if status is not None:
            raise AlreadyEnrolledError(f"You already have an active request/enrollment for '{course.name}' (status: {status}).")

        # Prerequisite check
        if course.p_code:
            p_row = self.db.fetchone("SELECT id, name FROM courses WHERE code=?", (course.p_code,))
            if p_row:
                p_enrollment = self.db.fetchone(
                    "SELECT status, grade FROM enrollments WHERE student_id=? AND course_id=?",
                    (student.user_id, p_row["id"])
                )
                if not p_enrollment or p_enrollment["status"] != "approved":
                    raise PrerequisiteError(
                        f"Prerequisite not met: You must successfully complete '{course.p_code} ({p_row['name']})' "
                        f"before enrolling in '{course.name}'."
                    )
                # If graded, grade must not be FF
                if p_enrollment["grade"] == "FF":
                    raise PrerequisiteError(
                        f"Prerequisite failed: You failed '{course.p_code}' with grade 'FF'. "
                        f"You must retake and pass it first."
                    )

        # Schedule conflict check within the same semester
        enrolled_courses = self.get_student_courses(student.user_id, course.semesters)
        for ec in enrolled_courses:
            c_obj = _row_to_course(ec)
            if c_obj.course_id != course.course_id and c_obj.overlaps(course):
                raise ScheduleConflictError(
                    f"Schedule conflict: '{course.name}' ({course.schedule_str()}) "
                    f"overlaps with your enrolled course '{c_obj.name}' ({c_obj.schedule_str()})."
                )

        # Capacity check
        enrolled_count = self.db.fetchone(
            "SELECT COUNT(*) as cnt FROM enrollments WHERE course_id=? AND status!='rejected'",
            (course.course_id,)
        )["cnt"]

        if enrolled_count >= course.capacity:
            raise CapacityError(f"Course '{course.name}' has reached its maximum capacity ({course.capacity} students).")

        self.db.execute(
            "INSERT INTO enrollments (student_id, course_id, semester, status) VALUES (?,?,?,?)",
            (student.user_id, course.course_id, course.semesters, "pending")
        )

    def drop(self, student: Student, course: Course):
        status = self.get_enrollment_status(student.user_id, course.course_id)
        if status is None:
            raise AppError(f"You are not currently enrolled in '{course.name}'.")
        self.db.execute(
            "DELETE FROM enrollments WHERE student_id=? AND course_id=?",
            (student.user_id, course.course_id)
        )

    def admin_update_status(self, enrollment_id: int, new_status: str):
        self.db.execute(
            "UPDATE enrollments SET status=? WHERE id=?",
            (new_status, enrollment_id)
        )

    def admin_set_grade(self, enrollment_id: int, letter_grade: str):
        grade_info = AcademicEngine.get_grade_info(letter_grade)
        pt = grade_info["point"] if grade_info else None
        self.db.execute(
            "UPDATE enrollments SET grade=?, grade_point=?, status='approved' WHERE id=?",
            (letter_grade.upper(), pt, enrollment_id)
        )

    def get_pending_enrollments(self):
        return self.db.fetchall(
            "SELECT e.id, e.student_id, e.course_id, e.semester, e.status, "
            "u.name as full_name, u.student_id as student_no, u.email, "
            "c.name as course_name, c.code, c.credit "
            "FROM enrollments e "
            "JOIN users u ON e.student_id = u.id "
            "JOIN courses c ON e.course_id = c.id "
            "WHERE e.status = 'pending' "
            "ORDER BY e.id"
        )

    def get_all_enrollments(self):
        return self.db.fetchall(
            "SELECT e.id, e.student_id, e.course_id, e.semester, e.status, e.grade, e.grade_point, "
            "u.name as full_name, u.student_id as student_no, u.email, "
            "c.name as course_name, c.code, c.credit "
            "FROM enrollments e "
            "JOIN users u ON e.student_id = u.id "
            "JOIN courses c ON e.course_id = c.id "
            "ORDER BY e.semester, u.name, c.code"
        )

    def advance_semester(self, student: Student) -> int:
        new_sem = student.semester + 1
        self.db.execute(
            "UPDATE users SET semester=? WHERE id=?",
            (new_sem, student.user_id)
        )
        student.semester = new_sem
        return new_sem
