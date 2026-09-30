"""
Academic Grading & Performance Evaluation Engine.
Provides credit-weighted GPA calculation, standard 4.0 grading scale mapping,
course-level pass/fail evaluation, and semester academic standing determination.
"""

from typing import List, Dict, Tuple, Optional

# Standard 4.0 Grading Scale
GRADE_SCALE = {
    "AA": {"point": 4.00, "status": "Passed", "description": "Excellent", "color": "#10B981"},
    "BA": {"point": 3.50, "status": "Passed", "description": "Very Good", "color": "#10B981"},
    "BB": {"point": 3.00, "status": "Passed", "description": "Good", "color": "#10B981"},
    "CB": {"point": 2.50, "status": "Passed", "description": "Fair", "color": "#3B82F6"},
    "CC": {"point": 2.00, "status": "Passed", "description": "Satisfactory", "color": "#3B82F6"},
    "DC": {"point": 1.50, "status": "Conditional Pass", "description": "Conditional", "color": "#F59E0B"},
    "DD": {"point": 1.00, "status": "Conditional Pass", "description": "Warning", "color": "#F59E0B"},
    "FF": {"point": 0.00, "status": "Failed", "description": "Unsuccessful", "color": "#EF4444"},
}

AVAILABLE_GRADES = list(GRADE_SCALE.keys())


class AcademicEngine:
    """Calculates weighted grade point averages and evaluates academic standing."""

    @staticmethod
    def get_grade_info(grade: str) -> Optional[dict]:
        """Returns metadata for a given letter grade."""
        if not grade:
            return None
        return GRADE_SCALE.get(grade.upper().strip())

    @staticmethod
    def get_course_status(grade: str) -> str:
        """Determines if a student passed, conditionally passed, or failed a course."""
        info = AcademicEngine.get_grade_info(grade)
        return info["status"] if info else "In Progress"

    @staticmethod
    def calculate_gpa(courses_with_grades: List[dict]) -> Tuple[float, int, int]:
        """
        Calculates credit-weighted GPA from a list of course records.
        Each record should contain 'credit' and 'grade'.
        
        Returns:
            Tuple of (gpa, total_graded_credits, total_passed_credits)
        """
        total_points = 0.0
        total_graded_credits = 0
        total_passed_credits = 0

        for item in courses_with_grades:
            if hasattr(item, "keys"):
                grade = item["grade"] if "grade" in item.keys() else None
                credit = item["credit"] if "credit" in item.keys() else 0
            else:
                grade = getattr(item, "grade", None)
                credit = getattr(item, "credit", 0)

            if not grade or grade.upper() not in GRADE_SCALE:
                continue

            info = GRADE_SCALE[grade.upper()]
            grade_point = info["point"]

            total_points += grade_point * credit
            total_graded_credits += credit

            # Earn credits if passed or conditionally passed
            if info["status"] in ("Passed", "Conditional Pass"):
                total_passed_credits += credit

        if total_graded_credits == 0:
            return 0.0, 0, 0

        gpa = round(total_points / total_graded_credits, 2)
        return gpa, total_graded_credits, total_passed_credits

    @staticmethod
    def get_academic_standing(gpa: float, total_credits: int = 0) -> Tuple[str, str, str]:
        """
        Determines student academic standing based on GPA.
        Returns:
            Tuple of (Standing Title, Status Label [Passed/Warning/Failed], Hex Color)
        """
        if total_credits == 0:
            return "No Graded Courses", "New Student", "#64748B"

        if gpa >= 3.50:
            return "High Honor", "Passed", "#10B981"
        elif gpa >= 3.00:
            return "Honor", "Passed", "#059669"
        elif gpa >= 2.00:
            return "Satisfactory", "Passed", "#3B82F6"
        elif gpa >= 1.80:
            return "Academic Probation", "Conditional", "#F59E0B"
        else:
            return "Unsatisfactory", "Failed", "#EF4444"
