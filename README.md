# Placement Training System

A complete Flask-based placement preparation system for students and admins.

## Project architecture

PlacementTrainingSystem/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── placement_training/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── student_routes.py
│   │   └── admin_routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── progress_service.py
│   │   └── recommendation_service.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── student_dashboard.html
│   │   ├── company_selection.html
│   │   ├── skills.html
│   │   ├── learning_plan.html
│   │   ├── tasks.html
│   │   ├── tests.html
│   │   ├── progress.html
│   │   ├── leaderboard.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   └── eligibility.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── app.js
│       └── images/
├── .env.example
└── .gitignore

## Phase roadmap

1. Flask project setup
2. MySQL + SQLAlchemy configuration
3. Student/Admin authentication
4. Student dashboard
5. Company and skill management
6. 30-day learning plan
7. Daily task management
8. Weekly test and evaluation
9. Progress calculation
10. Leaderboard
11. Admin dashboard
12. Resume Builder, Mock Interview and Certificate Tracker
13. Company Eligibility Checker
14. AI-based skill recommendation

## MySQL database design

Core tables include:
- students
- admins
- companies
- skills
- company_skills
- student_companies
- learning_plans
- tasks
- student_tasks
- tests
- questions
- test_results
- progress
- mock_interviews
- resumes
- certificates

### ER diagram explanation

The database follows a normalized structure:
- One student can select many companies through `student_companies`.
- One company can have many skills through `company_skills`.
- One student can complete many tasks and many test results.
- One test contains many questions.
- One student has one progress record per company or skill set.
- Admins manage companies, skills, plans, and tests.

## Installation

1. Create a virtual environment:
   python -m venv venv
2. Activate it:
   Windows: venv\Scripts\activate
3. Install packages:
   pip install -r requirements.txt
4. For MySQL, create a database:
   CREATE DATABASE placement_training;
5. Configure environment:
   copy .env.example to .env and update values
   Example for MySQL:
   DATABASE_URL=mysql+pymysql://root:root@localhost:3306/placement_training
6. Start app:
   python app.py

> The project includes a safe SQLite fallback for local testing when MySQL is not available. Set DATABASE_URL to MySQL in production or when you want the full required stack.

## Database URL

Example:
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/placement_training

## Test strategy

- Check route access
- Verify login and role restrictions
- Confirm progress calculations
- Validate weekly test scoring
- Review leaderboard updates

This project is designed so each phase can be added without breaking already working modules.
