from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: int
    email: str
    role: str = "user"
    full_name: str = ""

@dataclass
class Student(User):
    student_id: str = ""
    semester: int = 1

    def __post_init__(self):
        self.role = "student"

@dataclass
class Admin(User):
    def __post_init__(self):
        self.role = "admin"

@dataclass
class Course:
    course_id: int
    code: str
    name: str
    credit: int
    semesters: int
    p_code: Optional[str]
    day: str
    t_start: str
    t_end: str
    capacity: int

    def schedule_str(self) -> str:
        if self.t_start and self.t_end:
            return f"{self.day} {self.t_start}-{self.t_end}"
        return self.day or "TBA"

    def overlaps(self, other: "Course") -> bool:
        if not self.day or not other.day or self.day != other.day:
            return False
        if not self.t_start or not other.t_start:
            return False
        def to_min(t: str) -> int:
            try:
                h, m = t.split(":")
                return int(h) * 60 + int(m)
            except Exception:
                return 0
        s1, e1 = to_min(self.t_start), to_min(self.t_end)
        s2, e2 = to_min(other.t_start), to_min(other.t_end)
        return s1 < e2 and s2 < e1

@dataclass
class Enrollment:
    id: int
    student_id: int
    course_id: int
    semester: int
    status: str = "pending"
    grade: Optional[str] = None
