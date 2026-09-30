# Student Course Registration System

A desktop academic management and course registration application built with Python, Tkinter, and SQLite.

## Features

- **Student Portal:**
  - Browse course catalog and register for available semester courses.
  - Automatic prerequisite validation and schedule clash checking.
  - View grades, calculated semester GPA, cumulative GPA (CGPA), and academic standing.
- **Admin Portal:**
  - Review, approve, or reject student registration requests.
  - Assign letter grades (AA through FF) with automatic GPA recalculation.
  - View enrolled students and monitor course capacities.
- **Database:** SQLite database initialized with seed data from Excel files.

## Project Structure

- `main.py`: Tkinter GUI application and screen management.
- `academic.py`: Academic grading scale, GPA/CGPA calculation, and standing determination.
- `data.py`: Data models and course schedule overlap logic.
- `database.py`: SQLite database queries and Excel seed data loader.
- `enrollandsettings.py`: UI styling constants, input validation, and audit logger.
- `logic.py`: Enrollment business rules and authentication handlers.
- `data/`: Excel seed files (`Users.xlsx`, `Courses.xlsx`) and SQLite database (`university.db`).

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/alperencok/Student-Course-Registration-System.git
   cd Student-Course-Registration-System
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Author

- **alperencok** (https://github.com/alperencok)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
