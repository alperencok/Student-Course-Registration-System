import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManagement
from logic import Auth, Registration, AppError
from data import User, Student, Admin, Course
from academic import AcademicEngine, GRADE_SCALE, AVAILABLE_GRADES
from enrollandsettings import (
    Theme, Enroll, SemesterTransition, CourseMenu,
    Validation, Messages, Logger, Permission, DataExport
)

# Color Palette Shortcuts
C_SIDEBAR   = Theme.get_color("sidebar_bg")
C_HOVER     = Theme.get_color("sidebar_hover")
C_HEADER    = Theme.get_color("header_bg")
C_PRIMARY   = Theme.get_color("primary")
C_PRI_HOVER = Theme.get_color("primary_hover")
C_BG        = Theme.get_color("content_bg")
C_CARD      = Theme.get_color("card_bg")
C_BORDER    = Theme.get_color("card_border")
C_TEXT      = Theme.get_color("text_primary")
C_MUTED     = Theme.get_color("text_secondary")
C_SUCCESS   = Theme.get_color("success")
C_WARNING   = Theme.get_color("warning")
C_DANGER    = Theme.get_color("danger")
C_WHITE     = Theme.get_color("white")

F_TITLE     = Theme.get_font("title")
F_SUBTITLE  = Theme.get_font("subtitle")
F_HEAD      = Theme.get_font("heading")
F_BODY      = Theme.get_font("body")
F_BOLD      = Theme.get_font("body_bold")
F_SMALL     = Theme.get_font("small")
F_BTN       = Theme.get_font("button")


# -------------------------------------------------------------
# Reusable Modern UI Custom Buttons
# -------------------------------------------------------------
class ModernButton(tk.Button):
    def __init__(self, parent, text, command, bg=C_PRIMARY, fg=C_WHITE, active_bg=C_PRI_HOVER, **kw):
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=active_bg, activeforeground=fg,
            font=F_BTN, relief="flat", cursor="hand2", bd=0,
            padx=12, pady=6, **kw
        )

class SecondaryButton(tk.Button):
    def __init__(self, parent, text, command, **kw):
        super().__init__(
            parent, text=text, command=command,
            bg="#E2E8F0", fg=C_TEXT, activebackground="#CBD5E1", activeforeground=C_TEXT,
            font=F_BTN, relief="flat", cursor="hand2", bd=0,
            padx=12, pady=6, **kw
        )


# -------------------------------------------------------------
# Modern Sleek Sidebar
# -------------------------------------------------------------
class ModernSidebar(tk.Frame):
    def __init__(self, parent, title="", subtitle=""):
        super().__init__(parent, bg=C_SIDEBAR, width=230)
        self.pack_propagate(False)

        # Profile / App Header Banner
        header = tk.Frame(self, bg=C_SIDEBAR, pady=18, padx=16)
        header.pack(fill="x")

        # Academic Badge Icon Placeholder
        tk.Label(header, text="🎓", font=("Segoe UI Emoji", 24), bg=C_SIDEBAR, fg=C_WHITE).pack(anchor="w")
        if title:
            tk.Label(header, text=title, font=F_HEAD, bg=C_SIDEBAR, fg=C_WHITE, wraplength=190, justify="left").pack(anchor="w", pady=(4, 0))
        if subtitle:
            tk.Label(header, text=subtitle, font=F_SMALL, bg=C_SIDEBAR, fg="#94A3B8", wraplength=190, justify="left").pack(anchor="w")

        # Separator Line
        tk.Frame(self, bg="#334155", height=1).pack(fill="x", padx=16, pady=(4, 12))

    def add_nav_btn(self, label, command, is_primary=False):
        bg = C_PRIMARY if is_primary else C_SIDEBAR
        fg = C_WHITE if is_primary else "#CBD5E1"
        hover = C_PRI_HOVER if is_primary else C_HOVER

        btn = tk.Button(
            self, text=f"  {label}", command=command,
            bg=bg, fg=fg, activebackground=hover, activeforeground=C_WHITE,
            font=F_BODY, relief="flat", cursor="hand2", bd=0,
            anchor="w", padx=16, pady=8
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def add_spacer(self):
        tk.Frame(self, bg=C_SIDEBAR, height=12).pack()


# -------------------------------------------------------------
# 1. Login Screen
# -------------------------------------------------------------
class LoginScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C_BG)
        self.app = app
        self._logo_img = None
        self._build()

    def _build(self):
        # Top Minimalist Banner
        banner = tk.Frame(self, bg=C_HEADER, height=60)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        tk.Label(
            banner, text="STUDENT INFORMATION & COURSE REGISTRATION SYSTEM",
            bg=C_HEADER, fg=C_WHITE, font=F_SUBTITLE
        ).place(relx=0.5, rely=0.5, anchor="center")

        tk.Frame(self, bg=C_PRIMARY, height=3).pack(fill="x")

        # Centered Authentication Card
        card = tk.Frame(self, bg=C_CARD, padx=40, pady=35, relief="solid", bd=1)
        card.place(relx=0.5, rely=0.52, anchor="center")

        # App Logo Icon
        base = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base, "assets", "icon.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base, "icon.png")

        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).resize((72, 72), Image.Resampling.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
                tk.Label(card, image=self._logo_img, bg=C_CARD).pack(pady=(0, 10))
            except Exception:
                tk.Label(card, text="🎓", font=("Segoe UI Emoji", 32), bg=C_CARD).pack(pady=(0, 10))
        else:
            tk.Label(card, text="🎓", font=("Segoe UI Emoji", 32), bg=C_CARD).pack(pady=(0, 10))

        tk.Label(card, text="Portal Authentication", font=F_TITLE, bg=C_CARD, fg=C_TEXT).pack()
        tk.Label(card, text="Sign in to access your student or faculty account", font=F_SMALL, bg=C_CARD, fg=C_MUTED).pack(pady=(2, 20))

        # Username / ID Input
        tk.Label(card, text="Student ID or Email", font=F_BOLD, bg=C_CARD, fg=C_TEXT, anchor="w").pack(fill="x")
        self._email = tk.Entry(card, font=F_BODY, width=32, relief="solid", bd=1, highlightthickness=1)
        self._email.pack(pady=(4, 14), ipady=6)

        # Password Input
        tk.Label(card, text="Password", font=F_BOLD, bg=C_CARD, fg=C_TEXT, anchor="w").pack(fill="x")
        self._pw = tk.Entry(card, font=F_BODY, width=32, show="●", relief="solid", bd=1, highlightthickness=1)
        self._pw.pack(pady=(4, 18), ipady=6)

        ModernButton(card, "SIGN IN", self._attempt, width=28).pack(ipady=4)

        # Demo Credentials Helper Card
        demo_box = tk.LabelFrame(card, text=" Quick Demo Logins ", font=F_SMALL, bg=C_CARD, fg=C_MUTED, padx=10, pady=8)
        demo_box.pack(fill="x", pady=(20, 0))

        demos = [
            ("Admin Account", "admin", "admin"),
            ("Alex Morgan (GPA: 3.65 - High Honor)", "202401001", "01001"),
            ("Taylor Bennett (Probation / Retake)", "202401003", "01003"),
            ("Jordan Lee (Semester 1 - Pending)", "202401002", "01002")
        ]

        for lbl, u, p in demos:
            f = tk.Frame(demo_box, bg=C_CARD)
            f.pack(fill="x", pady=1)
            tk.Label(f, text=lbl, font=F_SMALL, bg=C_CARD, fg=C_TEXT).pack(side="left")
            btn = tk.Button(
                f, text="Use", font=("Segoe UI", 8), bg="#EEF2FF", fg=C_PRIMARY,
                relief="flat", cursor="hand2", padx=6, pady=0,
                command=lambda un=u, pw=p: self._fill_creds(un, pw)
            )
            btn.pack(side="right")

        self._email.focus_set()
        self._pw.bind("<Return>", lambda e: self._attempt())

    def _fill_creds(self, username, password):
        self._email.delete(0, tk.END)
        self._email.insert(0, username)
        self._pw.delete(0, tk.END)
        self._pw.insert(0, password)
        self._attempt()

    def _attempt(self):
        user = self.app.auth.login(self._email.get(), self._pw.get())
        if user is None:
            messagebox.showerror("Authentication Failed", "Invalid student ID, email, or password.")
            return
        if isinstance(user, Admin):
            self.app.show_admin(user)
        else:
            self.app.show_student(user)


# -------------------------------------------------------------
# 2. Student Dashboard
# -------------------------------------------------------------
class StudentDashboard(tk.Frame):
    def __init__(self, parent, app, student: Student):
        super().__init__(parent, bg=C_BG)
        self.app = app
        self.student = student
        self._build()

    def _build(self):
        # Sidebar Navigation
        sb = ModernSidebar(self, self.student.full_name or "Student", f"ID: {self.student.student_id} | Sem {self.student.semester}")
        sb.pack(side="left", fill="y")

        sb.add_nav_btn("📋  My Enrolled Courses", lambda: self.app.show_student(self.student), is_primary=True)
        sb.add_nav_btn("🎓  Transcript & GPA", lambda: self.app.show_transcript(self.student))
        sb.add_nav_btn("➕  Register / Drop Courses", lambda: self.app.show_selection(self.student))

        sem_other = 2 if self.student.semester == 1 else 1
        sb.add_nav_btn(f"🔄  View Semester {sem_other}", lambda: self._switch_sem(sem_other))

        if self.student.semester == 1:
            sb.add_nav_btn("⚡  Advance to Semester 2", self._advance)

        sb.add_spacer()
        tk.Button(
            sb, text="🚪  Sign Out", command=self.app.show_login,
            bg=C_SIDEBAR, fg="#EF4444", activebackground="#334155", activeforeground="#EF4444",
            font=F_BODY, relief="flat", cursor="hand2", bd=0, anchor="w", padx=16, pady=8
        ).pack(side="bottom", fill="x", padx=10, pady=16)

        # Main Content Area
        main = tk.Frame(self, bg=C_BG)
        main.pack(side="left", fill="both", expand=True)

        # Header Title
        hdr = tk.Frame(main, bg=C_WHITE, height=54, highlightthickness=1, highlightbackground=C_BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(
            hdr, text=f"Academic Portal — Semester {self.student.semester} Enrolled Courses",
            font=F_SUBTITLE, bg=C_WHITE, fg=C_TEXT
        ).pack(side="left", padx=24)

        container = tk.Frame(main, bg=C_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        # Top Summary Cards (GPA, Credits, Approved, Pending)
        self._render_metrics(container)

        # Course List Table
        self._render_course_table(container)

    def _render_metrics(self, parent):
        enrolled = self.app.reg.get_student_courses(self.student.user_id, self.student.semester)
        approved = [r for r in enrolled if r["status"] == "approved"]
        pending  = [r for r in enrolled if r["status"] == "pending"]

        # Calculate Term GPA for current semester
        term_gpa, graded_credits, passed_credits = AcademicEngine.calculate_gpa(enrolled)
        standing_title, status_label, badge_color = AcademicEngine.get_academic_standing(term_gpa, graded_credits)

        cards_frame = tk.Frame(parent, bg=C_BG)
        cards_frame.pack(fill="x", pady=(0, 16))

        metrics = [
            ("Term GPA", f"{term_gpa:.2f}" if graded_credits > 0 else "N/A", C_PRIMARY, f"{graded_credits} Graded ECTS"),
            ("Academic Standing", status_label, badge_color, standing_title),
            ("Approved Courses", str(len(approved)), C_SUCCESS, f"{sum(r['credit'] for r in approved)} Total ECTS"),
            ("Pending Approval", str(len(pending)), C_WARNING, "Awaiting Review"),
        ]

        for title, value, color, subtitle in metrics:
            card = tk.Frame(cards_frame, bg=C_CARD, padx=16, pady=12, relief="solid", bd=1, highlightthickness=0)
            card.pack(side="left", expand=True, fill="both", padx=6)

            tk.Label(card, text=title, font=F_SMALL, bg=C_CARD, fg=C_MUTED).pack(anchor="w")
            tk.Label(card, text=value, font=("Segoe UI", 16, "bold"), bg=C_CARD, fg=color).pack(anchor="w", pady=(2, 0))
            tk.Label(card, text=subtitle, font=("Segoe UI", 8), bg=C_CARD, fg=C_MUTED).pack(anchor="w")

    def _render_course_table(self, parent):
        table_frame = tk.Frame(parent, bg=C_CARD, padx=16, pady=16, relief="solid", bd=1)
        table_frame.pack(fill="both", expand=True)

        header_frame = tk.Frame(table_frame, bg=C_CARD)
        header_frame.pack(fill="x", pady=(0, 10))
        tk.Label(header_frame, text=f"Semester {self.student.semester} Course Registrations", font=F_HEAD, bg=C_CARD, fg=C_TEXT).pack(side="left")

        enrolled = self.app.reg.get_student_courses(self.student.user_id, self.student.semester)

        if not enrolled:
            empty_box = tk.Frame(table_frame, bg=C_CARD, pady=40)
            empty_box.pack(fill="both", expand=True)
            tk.Label(empty_box, text="No courses registered in this semester yet.", font=F_BODY, bg=C_CARD, fg=C_MUTED).pack()
            ModernButton(empty_box, "Browse & Register Courses", lambda: self.app.show_selection(self.student)).pack(pady=10)
            return

        columns = ("code", "name", "credit", "schedule", "grade", "status")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8, selectmode="browse")

        tree.heading("code", text="Code")
        tree.heading("name", text="Course Title")
        tree.heading("credit", text="Credits (ECTS)")
        tree.heading("schedule", text="Lecture Schedule")
        tree.heading("grade", text="Letter Grade")
        tree.heading("status", text="Approval Status")

        tree.column("code", width=85, anchor="center")
        tree.column("name", width=280, anchor="w")
        tree.column("credit", width=95, anchor="center")
        tree.column("schedule", width=180, anchor="w")
        tree.column("grade", width=95, anchor="center")
        tree.column("status", width=110, anchor="center")

        tree.tag_configure("approved", foreground="#059669", font=F_BOLD)
        tree.tag_configure("pending", foreground="#D97706", font=F_BOLD)
        tree.tag_configure("rejected", foreground="#DC2626", font=F_BOLD)

        for row in enrolled:
            sched = f"{row['day']} {row['t_start']}-{row['t_end']}" if row['t_start'] else (row['day'] or "TBA")
            grd = f"{row['grade']} ({row['grade_point']:.1f})" if row['grade'] else "In Progress"
            status = row['status'].upper()

            tree.insert("", "end", values=(
                row["code"],
                row["name"],
                f"{row['credit']} ECTS",
                sched,
                grd,
                status
            ), tags=(row['status'],))

        tree.pack(fill="both", expand=True)

    def _switch_sem(self, sem):
        self.student.semester = sem
        self.app.show_student(self.student)

    def _advance(self):
        can_advance, msg = self.app.semester_manager.advance_possible(self.student)
        if not can_advance:
            messagebox.showwarning("Cannot Advance", msg)
            return
        self.app.semester_manager.advance(self.student)
        self.app.audit_log.log_action(
            "semester_advance", self.student.student_id, f"Semester 1 → 2"
        )
        messagebox.showinfo("Semester Advanced", "You have officially advanced to Semester 2!\nYou can now register for Semester 2 courses.")
        self.app.show_student(self.student)


# -------------------------------------------------------------
# 3. Academic Transcript & GPA View (Core Enhancement)
# -------------------------------------------------------------
class TranscriptScreen(tk.Frame):
    def __init__(self, parent, app, student: Student):
        super().__init__(parent, bg=C_BG)
        self.app = app
        self.student = student
        self._build()

    def _build(self):
        # Sidebar
        sb = ModernSidebar(self, self.student.full_name or "Student", f"ID: {self.student.student_id}")
        sb.pack(side="left", fill="y")

        sb.add_nav_btn("📋  My Enrolled Courses", lambda: self.app.show_student(self.student))
        sb.add_nav_btn("🎓  Transcript & GPA", lambda: self.app.show_transcript(self.student), is_primary=True)
        sb.add_nav_btn("➕  Register / Drop Courses", lambda: self.app.show_selection(self.student))
        sb.add_spacer()
        tk.Button(
            sb, text="🚪  Sign Out", command=self.app.show_login,
            bg=C_SIDEBAR, fg="#EF4444", activebackground="#334155", activeforeground="#EF4444",
            font=F_BODY, relief="flat", cursor="hand2", bd=0, anchor="w", padx=16, pady=8
        ).pack(side="bottom", fill="x", padx=10, pady=16)

        # Main Content
        main = tk.Frame(self, bg=C_BG)
        main.pack(side="left", fill="both", expand=True)

        hdr = tk.Frame(main, bg=C_WHITE, height=54, highlightthickness=1, highlightbackground=C_BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="Official Academic Transcript & Performance Evaluation", font=F_SUBTITLE, bg=C_WHITE, fg=C_TEXT).pack(side="left", padx=24)

        container = tk.Frame(main, bg=C_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        # Pull all courses across all semesters
        all_courses = self.app.reg.get_student_transcript(self.student.user_id)

        # Calculate Overall Cumulative CGPA
        cgpa, total_graded_ects, total_passed_ects = AcademicEngine.calculate_gpa(all_courses)
        standing_title, status_label, badge_color = AcademicEngine.get_academic_standing(cgpa, total_graded_ects)

        # Top Summary Cards
        cards_frame = tk.Frame(container, bg=C_BG)
        cards_frame.pack(fill="x", pady=(0, 16))

        cards = [
            ("Cumulative CGPA", f"{cgpa:.2f} / 4.00" if total_graded_ects > 0 else "N/A", C_PRIMARY, "Weighted by Credits"),
            ("Overall Academic Standing", status_label, badge_color, standing_title),
            ("Earned Credits", f"{total_passed_ects} ECTS", C_SUCCESS, f"{total_graded_ects} Total Graded Credits"),
            ("Grading System", "4.00 Standard", "#0EA5E9", "Standard 4.0 Scale")
        ]

        for title, val, color, sub in cards:
            c = tk.Frame(cards_frame, bg=C_CARD, padx=16, pady=12, relief="solid", bd=1)
            c.pack(side="left", expand=True, fill="both", padx=6)
            tk.Label(c, text=title, font=F_SMALL, bg=C_CARD, fg=C_MUTED).pack(anchor="w")
            tk.Label(c, text=val, font=("Segoe UI", 16, "bold"), bg=C_CARD, fg=color).pack(anchor="w", pady=(2, 0))
            tk.Label(c, text=sub, font=("Segoe UI", 8), bg=C_CARD, fg=C_MUTED).pack(anchor="w")

        # Transcript Table Container
        table_card = tk.Frame(container, bg=C_CARD, padx=16, pady=16, relief="solid", bd=1)
        table_card.pack(fill="both", expand=True)

        tk.Label(table_card, text="Detailed Course-by-Course Evaluation & Pass/Fail Status", font=F_HEAD, bg=C_CARD, fg=C_TEXT).pack(anchor="w", pady=(0, 10))

        cols = ("sem", "code", "name", "credit", "grade", "points", "weighted", "result")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=9, selectmode="browse")

        tree.heading("sem", text="Semester")
        tree.heading("code", text="Course Code")
        tree.heading("name", text="Course Title")
        tree.heading("credit", text="Credits (ECTS)")
        tree.heading("grade", text="Letter Grade")
        tree.heading("points", text="Grade Point")
        tree.heading("weighted", text="Weighted Score")
        tree.heading("result", text="Academic Result")

        tree.column("sem", width=80, anchor="center")
        tree.column("code", width=85, anchor="center")
        tree.column("name", width=250, anchor="w")
        tree.column("credit", width=95, anchor="center")
        tree.column("grade", width=90, anchor="center")
        tree.column("points", width=90, anchor="center")
        tree.column("weighted", width=105, anchor="center")
        tree.column("result", width=125, anchor="center")

        tree.tag_configure("passed", foreground="#059669", font=F_BOLD)
        tree.tag_configure("conditional", foreground="#D97706", font=F_BOLD)
        tree.tag_configure("failed", foreground="#DC2626", font=F_BOLD)
        tree.tag_configure("pending", foreground="#64748B")

        for r in all_courses:
            grd = r["grade"]
            credit = r["credit"]
            pt = r["grade_point"]

            if grd:
                w_score = f"{credit * pt:.1f}"
                res = AcademicEngine.get_course_status(grd)
                if res == "Passed":
                    tag = "passed"
                    res_display = "PASSED"
                elif res == "Conditional Pass":
                    tag = "conditional"
                    res_display = "CONDITIONAL"
                else:
                    tag = "failed"
                    res_display = "FAILED"
            else:
                w_score = "-"
                pt = "-"
                grd = "In Progress"
                res_display = "Enrolled"
                tag = "pending"

            tree.insert("", "end", values=(
                f"Semester {r['enrolled_semester']}",
                r["code"],
                r["name"],
                f"{credit} ECTS",
                grd,
                f"{pt:.2f}" if isinstance(pt, float) else pt,
                w_score,
                res_display
            ), tags=(tag,))

        tree.pack(fill="both", expand=True)


# -------------------------------------------------------------
# 4. Course Registration & Selection Screen
# -------------------------------------------------------------
class CourseSelectionScreen(tk.Frame):
    def __init__(self, parent, app, student: Student):
        super().__init__(parent, bg=C_BG)
        self.app = app
        self.student = student
        self._build()

    def _build(self):
        sb = ModernSidebar(self, self.student.full_name or "Student", f"ID: {self.student.student_id}")
        sb.pack(side="left", fill="y")

        sb.add_nav_btn("📋  My Enrolled Courses", lambda: self.app.show_student(self.student))
        sb.add_nav_btn("🎓  Transcript & GPA", lambda: self.app.show_transcript(self.student))
        sb.add_nav_btn("➕  Register / Drop Courses", lambda: self.app.show_selection(self.student), is_primary=True)
        sb.add_spacer()
        tk.Button(
            sb, text="🚪  Sign Out", command=self.app.show_login,
            bg=C_SIDEBAR, fg="#EF4444", activebackground="#334155", activeforeground="#EF4444",
            font=F_BODY, relief="flat", cursor="hand2", bd=0, anchor="w", padx=16, pady=8
        ).pack(side="bottom", fill="x", padx=10, pady=16)

        main = tk.Frame(self, bg=C_BG)
        main.pack(side="left", fill="both", expand=True)

        hdr = tk.Frame(main, bg=C_WHITE, height=54, highlightthickness=1, highlightbackground=C_BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text=f"Course Catalog & Enrollment — Semester {self.student.semester}", font=F_SUBTITLE, bg=C_WHITE, fg=C_TEXT).pack(side="left", padx=24)

        container = tk.Frame(main, bg=C_BG, padx=24, pady=16)
        container.pack(fill="both", expand=True)

        # Instructions banner
        notice = tk.Frame(container, bg="#EEF2FF", padx=14, pady=8, relief="solid", bd=1, highlightthickness=0)
        notice.pack(fill="x", pady=(0, 12))
        tk.Label(
            notice,
            text="💡 Tip: Select courses according to your degree requirements. Prerequisites and timetable schedule conflicts are verified automatically.",
            font=F_SMALL, bg="#EEF2FF", fg=C_PRIMARY
        ).pack(anchor="w")

        # Scrollable course list
        canvas = tk.Canvas(container, bg=C_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=C_BG)

        self._scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_win, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._populate()

    def _populate(self):
        for w in self._scroll_frame.winfo_children():
            w.destroy()

        courses = self.app.reg.get_courses_for_semester(self.student.semester)
        if not courses:
            tk.Label(self._scroll_frame, text="No courses listed for this semester.", font=F_BODY, bg=C_BG, fg=C_MUTED).pack(pady=40)
            return

        for course in courses:
            status = self.app.reg.get_enrollment_status(self.student.user_id, course.course_id)
            enrolled_count = self.app.db.fetchone(
                "SELECT COUNT(*) as c FROM enrollments WHERE course_id=? AND status!='rejected'",
                (course.course_id,)
            )["c"]

            card = tk.Frame(self._scroll_frame, bg=C_CARD, padx=16, pady=12, relief="solid", bd=1)
            card.pack(fill="x", pady=4)

            # Left Course Info
            info_frame = tk.Frame(card, bg=C_CARD)
            info_frame.pack(side="left", fill="both", expand=True)

            code_badge = tk.Label(info_frame, text=course.code, font=F_BOLD, bg="#F1F5F9", fg=C_PRIMARY, padx=6, pady=2)
            code_badge.pack(side="left", anchor="w", padx=(0, 10))

            details = tk.Frame(info_frame, bg=C_CARD)
            details.pack(side="left", fill="both", expand=True)

            tk.Label(details, text=course.name, font=F_HEAD, bg=C_CARD, fg=C_TEXT).pack(anchor="w")

            meta_txt = f"{course.credit} ECTS  •  {course.schedule_str()}"
            if course.p_code:
                meta_txt += f"  •  Prerequisite: {course.p_code}"
            tk.Label(details, text=meta_txt, font=F_SMALL, bg=C_CARD, fg=C_MUTED).pack(anchor="w", pady=(2, 0))

            # Capacity Indicator
            cap_color = C_DANGER if enrolled_count >= course.capacity else C_SUCCESS
            tk.Label(card, text=f"Seats: {enrolled_count}/{course.capacity}", font=F_SMALL, bg=C_CARD, fg=cap_color, width=12).pack(side="left", padx=10)

            # Action Buttons
            btn_frame = tk.Frame(card, bg=C_CARD)
            btn_frame.pack(side="right")

            if status is None:
                ModernButton(btn_frame, "Register", lambda c=course: self._enroll(c), width=10).pack(side="left")
            elif status == "pending":
                tk.Label(btn_frame, text="⏳ Pending", font=F_BOLD, bg=C_CARD, fg="#D97706").pack(side="left", padx=6)
                SecondaryButton(btn_frame, "Drop", lambda c=course: self._drop(c), width=7).pack(side="left")
            elif status == "approved":
                tk.Label(btn_frame, text="✓ Enrolled", font=F_BOLD, bg=C_CARD, fg=C_SUCCESS).pack(side="left", padx=6)
                SecondaryButton(btn_frame, "Drop", lambda c=course: self._drop(c), width=7).pack(side="left")
            elif status == "rejected":
                tk.Label(btn_frame, text="✕ Rejected", font=F_BOLD, bg=C_CARD, fg=C_DANGER).pack(side="left", padx=6)
                ModernButton(btn_frame, "Re-apply", lambda c=course: self._enroll(c), width=9).pack(side="left")

    def _enroll(self, course):
        success, msg = self.app.enrollment_handler.enroll_wvalidation(self.student, course)
        if success:
            self.app.audit_log.log_action("course_enroll", self.student.student_id, course.code, f"Sem {course.semesters}")
            messagebox.showinfo("Enrollment Submitted", f"Enrollment request for '{course.name}' submitted successfully.\nWaiting for advisor/admin approval.")
            self._populate()
        else:
            messagebox.showerror("Registration Conflict / Error", msg)

    def _drop(self, course):
        if not messagebox.askyesno("Confirm Drop", f"Are you sure you want to drop '{course.name}'?"):
            return
        success, msg = self.app.enrollment_handler.drop_wvalidation(self.student, course)
        if success:
            self.app.audit_log.log_action("course_drop", self.student.student_id, course.code)
            messagebox.showinfo("Success", msg)
            self._populate()
        else:
            messagebox.showerror("Error", msg)


# -------------------------------------------------------------
# 5. Administrator Dashboard (With Grade Assignment & Transcripts)
# -------------------------------------------------------------
class AdminDashboard(tk.Frame):
    def __init__(self, parent, app, admin: Admin):
        super().__init__(parent, bg=C_BG)
        self.app = app
        self.admin = admin
        self._build()

    def _build(self):
        sb = ModernSidebar(self, "System Administrator", "Department Coordinator")
        sb.pack(side="left", fill="y")

        self._active_tab = tk.StringVar(value="requests")

        sb.add_nav_btn("📥  Pending Requests", lambda: self._switch_tab("requests"), is_primary=True)
        sb.add_nav_btn("🎓  Assign Grades", lambda: self._switch_tab("grades"))
        sb.add_nav_btn("📚  Course Management", lambda: self._switch_tab("courses"))
        sb.add_nav_btn("📜  Audit & Activity Logs", lambda: self._switch_tab("logs"))
        sb.add_spacer()
        tk.Button(
            sb, text="🚪  Sign Out", command=self.app.show_login,
            bg=C_SIDEBAR, fg="#EF4444", activebackground="#334155", activeforeground="#EF4444",
            font=F_BODY, relief="flat", cursor="hand2", bd=0, anchor="w", padx=16, pady=8
        ).pack(side="bottom", fill="x", padx=10, pady=16)

        self.main_content = tk.Frame(self, bg=C_BG)
        self.main_content.pack(side="left", fill="both", expand=True)

        self._show_requests_tab()

    def _switch_tab(self, tab):
        self._active_tab.set(tab)
        for w in self.main_content.winfo_children():
            w.destroy()

        if tab == "requests":
            self._show_requests_tab()
        elif tab == "grades":
            self._show_grades_tab()
        elif tab == "courses":
            self._show_courses_tab()
        elif tab == "logs":
            self._show_logs_tab()

    def _show_requests_tab(self):
        hdr = tk.Frame(self.main_content, bg=C_WHITE, height=54, highlightthickness=1, highlightbackground=C_BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Course Registration Approval Queue", font=F_SUBTITLE, bg=C_WHITE, fg=C_TEXT).pack(side="left", padx=24)

        container = tk.Frame(self.main_content, bg=C_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        requests = self.app.reg.get_pending_enrollments()

        summary_bar = tk.Frame(container, bg=C_CARD, padx=16, pady=10, relief="solid", bd=1)
        summary_bar.pack(fill="x", pady=(0, 14))
        tk.Label(summary_bar, text=f"Pending Student Registration Requests: {len(requests)}", font=F_HEAD, bg=C_CARD, fg=C_TEXT).pack(side="left")

        table_card = tk.Frame(container, bg=C_CARD, padx=16, pady=16, relief="solid", bd=1)
        table_card.pack(fill="both", expand=True)

        cols = ("id", "student_no", "student_name", "code", "course", "credits", "actions")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=10, selectmode="browse")

        tree.heading("id", text="Req ID")
        tree.heading("student_no", text="Student ID")
        tree.heading("student_name", text="Student Full Name")
        tree.heading("code", text="Course")
        tree.heading("course", text="Course Title")
        tree.heading("credits", text="Credits")
        tree.heading("actions", text="Status")

        tree.column("id", width=60, anchor="center")
        tree.column("student_no", width=95, anchor="center")
        tree.column("student_name", width=180, anchor="w")
        tree.column("code", width=80, anchor="center")
        tree.column("course", width=240, anchor="w")
        tree.column("credits", width=80, anchor="center")
        tree.column("actions", width=90, anchor="center")

        for r in requests:
            tree.insert("", "end", values=(
                r["id"], r["student_no"], r["full_name"], r["code"],
                r["course_name"], f"{r['credit']} ECTS", "PENDING"
            ))

        tree.pack(fill="both", expand=True, pady=(0, 12))

        # Bottom Action Bar
        act_bar = tk.Frame(table_card, bg=C_CARD)
        act_bar.pack(fill="x")

        def _approve_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Request", "Please select a pending request from the table.")
                return
            item = tree.item(sel[0])["values"]
            req_id = item[0]
            self.app.reg.admin_update_status(req_id, "approved")
            self.app.audit_log.log_action("approve_enrollment", "admin", f"Enrollment #{req_id}", f"Student {item[1]} for {item[3]}")
            messagebox.showinfo("Approved", f"Enrollment request #{req_id} approved successfully.")
            self._show_requests_tab()

        def _reject_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Request", "Please select a pending request from the table.")
                return
            item = tree.item(sel[0])["values"]
            req_id = item[0]
            self.app.reg.admin_update_status(req_id, "rejected")
            self.app.audit_log.log_action("reject_enrollment", "admin", f"Enrollment #{req_id}", f"Student {item[1]} for {item[3]}")
            messagebox.showinfo("Rejected", f"Enrollment request #{req_id} has been rejected.")
            self._show_requests_tab()

        ModernButton(act_bar, "✓  Approve Selected", _approve_selected, bg=C_SUCCESS, active_bg="#059669", width=18).pack(side="left", padx=(0, 10))
        ModernButton(act_bar, "✕  Reject Selected", _reject_selected, bg=C_DANGER, active_bg="#DC2626", width=18).pack(side="left")

    def _show_grades_tab(self):
        hdr = tk.Frame(self.main_content, bg=C_WHITE, height=54, highlightthickness=1, highlightbackground=C_BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Academic Grade Assignment & Transcripts", font=F_SUBTITLE, bg=C_WHITE, fg=C_TEXT).pack(side="left", padx=24)

        container = tk.Frame(self.main_content, bg=C_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        all_enrollments = self.app.reg.get_all_enrollments()

        # Grade Management Controls Bar
        control_card = tk.Frame(container, bg=C_CARD, padx=16, pady=14, relief="solid", bd=1)
        control_card.pack(fill="x", pady=(0, 14))

        tk.Label(control_card, text="Assign Letter Grade to Selected Enrollment:", font=F_HEAD, bg=C_CARD, fg=C_TEXT).pack(side="left", padx=(0, 12))

        grade_var = tk.StringVar(value="AA")
        grade_combo = ttk.Combobox(control_card, textvariable=grade_var, values=AVAILABLE_GRADES, state="readonly", width=8, font=F_BOLD)
        grade_combo.pack(side="left", padx=6)

        table_card = tk.Frame(container, bg=C_CARD, padx=16, pady=16, relief="solid", bd=1)
        table_card.pack(fill="both", expand=True)

        cols = ("id", "student_no", "name", "sem", "code", "course", "credit", "status", "grade", "gpa_pts")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=11, selectmode="browse")

        tree.heading("id", text="ID")
        tree.heading("student_no", text="Student ID")
        tree.heading("name", text="Student Name")
        tree.heading("sem", text="Sem")
        tree.heading("code", text="Course")
        tree.heading("course", text="Course Title")
        tree.heading("credit", text="Credits")
        tree.heading("status", text="Status")
        tree.heading("grade", text="Grade")
        tree.heading("gpa_pts", text="Point")

        tree.column("id", width=45, anchor="center")
        tree.column("student_no", width=85, anchor="center")
        tree.column("name", width=140, anchor="w")
        tree.column("sem", width=50, anchor="center")
        tree.column("code", width=75, anchor="center")
        tree.column("course", width=220, anchor="w")
        tree.column("credit", width=70, anchor="center")
        tree.column("status", width=85, anchor="center")
        tree.column("grade", width=70, anchor="center")
        tree.column("gpa_pts", width=65, anchor="center")

        for r in all_enrollments:
            tree.insert("", "end", values=(
                r["id"], r["student_no"], r["full_name"], r["semester"],
                r["code"], r["course_name"], f"{r['credit']} ECTS",
                r["status"].upper(), r["grade"] or "—",
                f"{r['grade_point']:.1f}" if r["grade_point"] is not None else "—"
            ))

        tree.pack(fill="both", expand=True)

        def _apply_grade():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select Enrollment", "Please click an enrollment row from the table above.")
                return
            item = tree.item(sel[0])["values"]
            enroll_id = item[0]
            new_grade = grade_var.get()
            self.app.reg.admin_set_grade(enroll_id, new_grade)
            self.app.audit_log.log_action("assign_grade", "admin", f"Enrollment #{enroll_id}", f"Assigned grade '{new_grade}' to {item[2]} ({item[4]})")
            messagebox.showinfo("Grade Assigned", f"Grade '{new_grade}' assigned successfully to {item[2]} for '{item[4]}'.\nGPA updated automatically!")
            self._show_grades_tab()

        ModernButton(control_card, "Submit Grade", _apply_grade, width=14).pack(side="left", padx=10)

    def _show_courses_tab(self):
        hdr = tk.Frame(self.main_content, bg=C_WHITE, height=54, highlightthickness=1, highlightbackground=C_BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Academic Curriculum & Course Capacity Status", font=F_SUBTITLE, bg=C_WHITE, fg=C_TEXT).pack(side="left", padx=24)

        container = tk.Frame(self.main_content, bg=C_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        table_card = tk.Frame(container, bg=C_CARD, padx=16, pady=16, relief="solid", bd=1)
        table_card.pack(fill="both", expand=True)

        courses = self.app.db.fetchall("SELECT * FROM courses ORDER BY semesters, code")

        cols = ("code", "name", "sem", "credit", "prereq", "schedule", "capacity", "enrolled")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=12)

        tree.heading("code", text="Code")
        tree.heading("name", text="Course Title")
        tree.heading("sem", text="Semester")
        tree.heading("credit", text="Credits")
        tree.heading("prereq", text="Prerequisite")
        tree.heading("schedule", text="Timetable")
        tree.heading("capacity", text="Cap")
        tree.heading("enrolled", text="Enrolled")

        tree.column("code", width=80, anchor="center")
        tree.column("name", width=260, anchor="w")
        tree.column("sem", width=70, anchor="center")
        tree.column("credit", width=75, anchor="center")
        tree.column("prereq", width=95, anchor="center")
        tree.column("schedule", width=180, anchor="w")
        tree.column("capacity", width=65, anchor="center")
        tree.column("enrolled", width=75, anchor="center")

        for c in courses:
            enr_count = self.app.db.fetchone(
                "SELECT COUNT(*) as cnt FROM enrollments WHERE course_id=? AND status!='rejected'",
                (c["id"],)
            )["cnt"]
            sched = f"{c['day']} {c['t_start']}-{c['t_end']}" if c['t_start'] else (c['day'] or "TBA")

            tree.insert("", "end", values=(
                c["code"], c["name"], f"Sem {c['semesters']}",
                f"{c['credit']} ECTS", c["p_code"] or "None",
                sched, c["capacity"], enr_count
            ))

        tree.pack(fill="both", expand=True)

    def _show_logs_tab(self):
        hdr = tk.Frame(self.main_content, bg=C_WHITE, height=54, highlightthickness=1, highlightbackground=C_BORDER)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Security & Administrative Audit Logs", font=F_SUBTITLE, bg=C_WHITE, fg=C_TEXT).pack(side="left", padx=24)

        container = tk.Frame(self.main_content, bg=C_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        table_card = tk.Frame(container, bg=C_CARD, padx=16, pady=16, relief="solid", bd=1)
        table_card.pack(fill="both", expand=True)

        logs = self.app.audit_log.get_logs()

        cols = ("time", "actor", "action", "target", "details")
        tree = ttk.Treeview(table_card, columns=cols, show="headings", height=12)

        tree.heading("time", text="Timestamp")
        tree.heading("actor", text="Actor / User")
        tree.heading("action", text="Action")
        tree.heading("target", text="Target Entity")
        tree.heading("details", text="Event Details")

        tree.column("time", width=140, anchor="center")
        tree.column("actor", width=100, anchor="center")
        tree.column("action", width=140, anchor="w")
        tree.column("target", width=150, anchor="w")
        tree.column("details", width=260, anchor="w")

        if not logs:
            tree.insert("", "end", values=("-", "System", "audit_log_initialized", "Core System", "Audit service active."))
        else:
            for l in reversed(logs):
                tree.insert("", "end", values=(l["timestamp"], l["actor"], l["action"], l["target"], l["details"]))

        tree.pack(fill="both", expand=True)


# -------------------------------------------------------------
# Main Application Controller
# -------------------------------------------------------------
class CourseRegistrationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Academic Course Registration & GPA Management System")
        self.geometry("1100x700")
        self.minsize(980, 620)
        self.configure(bg=C_BG)

        # Apply Modern ttk Style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", font=F_BODY, rowheight=28, background=C_WHITE, fieldbackground=C_WHITE)
        style.configure("Treeview.Heading", font=F_BOLD, background="#F1F5F9", foreground=C_TEXT, relief="flat")
        style.map("Treeview.Heading", background=[("active", "#E2E8F0")])

        # Core Services
        self.db = DatabaseManagement()
        self.auth = Auth(self.db)
        self.reg = Registration(self.db)
        self.enrollment_handler = Enroll(self.reg, self.db)
        self.semester_manager = SemesterTransition(self.reg, self.db)
        self.audit_log = Logger()

        self._current_frame = None
        self.show_login()

    def _swap(self, frame_cls, *args):
        if self._current_frame:
            self._current_frame.destroy()
        self._current_frame = frame_cls(self, self, *args)
        self._current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self._swap(LoginScreen)

    def show_student(self, student: Student):
        self._swap(StudentDashboard, student)

    def show_transcript(self, student: Student):
        self._swap(TranscriptScreen, student)

    def show_selection(self, student: Student):
        self._swap(CourseSelectionScreen, student)

    def show_admin(self, admin: Admin):
        self._swap(AdminDashboard, admin)


if __name__ == "__main__":
    app = CourseRegistrationApp()
    app.mainloop()
