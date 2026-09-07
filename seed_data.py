from werkzeug.security import generate_password_hash
from sqlalchemy import text

from placement_training import create_app, db


def fetch_one(sql, params=None):
    params = params or {}
    result = db.session.execute(text(sql), params).fetchone()
    return result[0] if result else None


def ensure_admin(username='admin', email='admin@placement.com', password='admin123'):
    admin_id = fetch_one(
        'SELECT id FROM admins WHERE username = :username LIMIT 1',
        {'username': username}
    )
    if admin_id is None:
        admin_id = db.session.execute(
            text('''
                INSERT INTO admins (username, email, password_hash, role)
                VALUES (:username, :email, :password_hash, 'admin')
            '''),
            {
                'username': username,
                'email': email,
                'password_hash': generate_password_hash(password),
            }
        ).lastrowid
        db.session.commit()
    return admin_id


def ensure_company(name, description=''):
    company_id = fetch_one(
        'SELECT id FROM companies WHERE name = :name LIMIT 1',
        {'name': name}
    )
    if company_id is None:
        company_id = db.session.execute(
            text('''
                INSERT INTO companies (name, description, eligibility_criteria)
                VALUES (:name, :description, :eligibility_criteria)
            '''),
            {
                'name': name,
                'description': description,
                'eligibility_criteria': 'Open to eligible students',
            }
        ).lastrowid
        db.session.commit()
    return company_id


def ensure_skill(name, category='Core', description=''):
    skill_id = fetch_one(
        'SELECT id FROM skills WHERE name = :name LIMIT 1',
        {'name': name}
    )
    if skill_id is None:
        skill_id = db.session.execute(
            text('''
                INSERT INTO skills (name, category, description, priority, is_required)
                VALUES (:name, :category, :description, :priority, :is_required)
            '''),
            {
                'name': name,
                'category': category,
                'description': description,
                'priority': 1,
                'is_required': 1,
            }
        ).lastrowid
        db.session.commit()
    return skill_id


def ensure_company_skill(company_id, skill_id, priority=1, required=True):
    exists = fetch_one(
        'SELECT id FROM company_skills WHERE company_id = :company_id AND skill_id = :skill_id LIMIT 1',
        {'company_id': company_id, 'skill_id': skill_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO company_skills (company_id, skill_id, priority, required)
                VALUES (:company_id, :skill_id, :priority, :required)
            '''),
            {
                'company_id': company_id,
                'skill_id': skill_id,
                'priority': priority,
                'required': 1 if required else 0,
            }
        )
        db.session.commit()


def ensure_student(name, email, password='Student@123', department='CSE', year=2025,
                  cgpa=7.5, backlog_count=0, backlogs=0, phone='9999999999',
                  college_name='Demo College', dream_company_id=None):
    student_id = fetch_one(
        'SELECT id FROM students WHERE email = :email LIMIT 1',
        {'email': email}
    )
    if student_id is None:
        student_id = db.session.execute(
            text('''
                INSERT INTO students (
                    name, email, password_hash, department, year, cgpa, backlog_count,
                    backlogs, phone, college_name, is_active, dream_company_id, resume_completed
                )
                VALUES (
                    :name, :email, :password_hash, :department, :year, :cgpa, :backlog_count,
                    :backlogs, :phone, :college_name, :is_active, :dream_company_id, :resume_completed
                )
            '''),
            {
                'name': name,
                'email': email,
                'password_hash': generate_password_hash(password),
                'department': department,
                'year': year,
                'cgpa': float(cgpa),
                'backlog_count': backlog_count,
                'backlogs': backlogs,
                'phone': phone,
                'college_name': college_name,
                'is_active': 1,
                'dream_company_id': dream_company_id,
                'resume_completed': 0,
            }
        ).lastrowid
        db.session.commit()
    return student_id


def ensure_student_company(student_id, company_id, status='selected'):
    exists = fetch_one(
        'SELECT id FROM student_companies WHERE student_id = :student_id AND company_id = :company_id LIMIT 1',
        {'student_id': student_id, 'company_id': company_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO student_companies (student_id, company_id, status)
                VALUES (:student_id, :company_id, :status)
            '''),
            {'student_id': student_id, 'company_id': company_id, 'status': status}
        )
        db.session.commit()


def ensure_student_skill(student_id, skill_id, completed=1, score=80.00,
                        proficiency=80, completion_percent=80):
    exists = fetch_one(
        'SELECT id FROM student_skills WHERE student_id = :student_id AND skill_id = :skill_id LIMIT 1',
        {'student_id': student_id, 'skill_id': skill_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO student_skills (
                    student_id, skill_id, completed, score, proficiency, completion_percent,
                    last_practiced_at, completed_at
                )
                VALUES (
                    :student_id, :skill_id, :completed, :score, :proficiency, :completion_percent,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            '''),
            {
                'student_id': student_id,
                'skill_id': skill_id,
                'completed': 1 if completed else 0,
                'score': float(score),
                'proficiency': proficiency,
                'completion_percent': completion_percent,
            }
        )
        db.session.commit()


def ensure_project(title, slug, short_description, description, problem_statement,
                  difficulty='Beginner', max_score=100, time_limit_seconds=1800,
                  company_relevance='', objectives='', requirements='',
                  expected_input='', expected_output='', evaluation_criteria='',
                  reference_solution='', reference_approach='', status='active', created_by=None):
    project_id = fetch_one(
        'SELECT id FROM projects WHERE slug = :slug LIMIT 1',
        {'slug': slug}
    )
    if project_id is None:
        project_id = db.session.execute(
            text('''
                INSERT INTO projects (
                    title, slug, short_description, description, problem_statement,
                    difficulty, max_score, time_limit_seconds, company_relevance,
                    objectives, requirements, expected_input, expected_output,
                    evaluation_criteria, reference_solution, reference_approach,
                    status, created_by
                )
                VALUES (
                    :title, :slug, :short_description, :description, :problem_statement,
                    :difficulty, :max_score, :time_limit_seconds, :company_relevance,
                    :objectives, :requirements, :expected_input, :expected_output,
                    :evaluation_criteria, :reference_solution, :reference_approach,
                    :status, :created_by
                )
            '''),
            {
                'title': title,
                'slug': slug,
                'short_description': short_description,
                'description': description,
                'problem_statement': problem_statement,
                'difficulty': difficulty,
                'max_score': max_score,
                'time_limit_seconds': time_limit_seconds,
                'company_relevance': company_relevance,
                'objectives': objectives,
                'requirements': requirements,
                'expected_input': expected_input,
                'expected_output': expected_output,
                'evaluation_criteria': evaluation_criteria,
                'reference_solution': reference_solution,
                'reference_approach': reference_approach,
                'status': status,
                'created_by': created_by,
            }
        ).lastrowid
        db.session.commit()
    return project_id


def ensure_project_company(project_id, company_id):
    exists = fetch_one(
        'SELECT id FROM project_companies WHERE project_id = :project_id AND company_id = :company_id LIMIT 1',
        {'project_id': project_id, 'company_id': company_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO project_companies (project_id, company_id)
                VALUES (:project_id, :company_id)
            '''),
            {'project_id': project_id, 'company_id': company_id}
        )
        db.session.commit()


def ensure_project_skill(project_id, skill_id, importance=5):
    exists = fetch_one(
        'SELECT id FROM project_skills WHERE project_id = :project_id AND skill_id = :skill_id LIMIT 1',
        {'project_id': project_id, 'skill_id': skill_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO project_skills (project_id, skill_id, importance)
                VALUES (:project_id, :skill_id, :importance)
            '''),
            {'project_id': project_id, 'skill_id': skill_id, 'importance': importance}
        )
        db.session.commit()


def ensure_project_test_case(project_id, test_input, expected_output, points=10, is_hidden=0):
    exists = fetch_one(
        'SELECT id FROM project_test_cases WHERE project_id = :project_id AND input = :input AND expected_output = :expected_output LIMIT 1',
        {'project_id': project_id, 'input': test_input, 'expected_output': expected_output}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO project_test_cases (project_id, input, expected_output, points, is_hidden)
                VALUES (:project_id, :input, :expected_output, :points, :is_hidden)
            '''),
            {
                'project_id': project_id,
                'input': test_input,
                'expected_output': expected_output,
                'points': points,
                'is_hidden': 1 if is_hidden else 0,
            }
        )
        db.session.commit()


def ensure_project_hint(project_id, hint_order, hint):
    exists = fetch_one(
        'SELECT id FROM project_hints WHERE project_id = :project_id AND hint_order = :hint_order LIMIT 1',
        {'project_id': project_id, 'hint_order': hint_order}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO project_hints (project_id, hint_order, hint)
                VALUES (:project_id, :hint_order, :hint)
            '''),
            {'project_id': project_id, 'hint_order': hint_order, 'hint': hint}
        )
        db.session.commit()


def ensure_learning_plan(title, skill_id, duration_days=30, details=''):
    plan_id = fetch_one(
        'SELECT id FROM learning_plans WHERE title = :title AND skill_id = :skill_id LIMIT 1',
        {'title': title, 'skill_id': skill_id}
    )
    if plan_id is None:
        plan_id = db.session.execute(
            text('''
                INSERT INTO learning_plans (title, skill_id, duration_days, details)
                VALUES (:title, :skill_id, :duration_days, :details)
            '''),
            {'title': title, 'skill_id': skill_id, 'duration_days': duration_days, 'details': details}
        ).lastrowid
        db.session.commit()
    return plan_id


def ensure_task(plan_id, day_number, title, description, is_optional=0):
    task_id = fetch_one(
        'SELECT id FROM tasks WHERE plan_id = :plan_id AND day_number = :day_number AND title = :title LIMIT 1',
        {'plan_id': plan_id, 'day_number': day_number, 'title': title}
    )
    if task_id is None:
        task_id = db.session.execute(
            text('''
                INSERT INTO tasks (plan_id, day_number, title, description, is_optional)
                VALUES (:plan_id, :day_number, :title, :description, :is_optional)
            '''),
            {'plan_id': plan_id, 'day_number': day_number, 'title': title, 'description': description, 'is_optional': 1 if is_optional else 0}
        ).lastrowid
        db.session.commit()
    return task_id


def ensure_student_task(student_id, task_id, completed=1, status='completed'):
    exists = fetch_one(
        'SELECT id FROM student_tasks WHERE student_id = :student_id AND task_id = :task_id LIMIT 1',
        {'student_id': student_id, 'task_id': task_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO student_tasks (student_id, task_id, completed, status, completed_at)
                VALUES (:student_id, :task_id, :completed, :status, CURRENT_TIMESTAMP)
            '''),
            {
                'student_id': student_id,
                'task_id': task_id,
                'completed': 1 if completed else 0,
                'status': status,
            }
        )
        db.session.commit()


def ensure_progress(student_id, skill_completion=78.00, task_completion=70.00,
                   test_performance=80.00, aptitude_performance=75.00,
                   discussion_performance=85.00, overall_progress=77.00):
    exists = fetch_one(
        'SELECT id FROM progress WHERE student_id = :student_id LIMIT 1',
        {'student_id': student_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO progress (
                    student_id, project_completion_percent, project_performance_percent,
                    skill_completion_percent, task_completion_percent,
                    challenge_performance_percent, overall_progress_percent,
                    skill_completion, task_completion, test_performance,
                    aptitude_performance, discussion_performance, overall_progress
                )
                VALUES (
                    :student_id, 75.00, 80.00,
                    :skill_completion, :task_completion,
                    82.00, 77.00,
                    :skill_completion, :task_completion, :test_performance,
                    :aptitude_performance, :discussion_performance, :overall_progress
                )
            '''),
            {
                'student_id': student_id,
                'skill_completion': float(skill_completion),
                'task_completion': float(task_completion),
                'test_performance': float(test_performance),
                'aptitude_performance': float(aptitude_performance),
                'discussion_performance': float(discussion_performance),
                'overall_progress': float(overall_progress),
            }
        )
        db.session.commit()


def ensure_mock_interview(student_id, category='technical', question='Explain your final year project.',
                         student_answer='I explained my role and contributions in the project.',
                         score=84.50, feedback='Strong explanation and communication.'):
    exists = fetch_one(
        'SELECT id FROM mock_interviews WHERE student_id = :student_id AND question = :question LIMIT 1',
        {'student_id': student_id, 'question': question}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO mock_interviews (student_id, category, question, student_answer, score, feedback)
                VALUES (:student_id, :category, :question, :student_answer, :score, :feedback)
            '''),
            {
                'student_id': student_id,
                'category': category,
                'question': question,
                'student_answer': student_answer,
                'score': float(score),
                'feedback': feedback,
            }
        )
        db.session.commit()


def ensure_resume(student_id, content='Sample resume content.', pdf_path='uploads/resume.pdf', completed=1):
    exists = fetch_one(
        'SELECT id FROM resumes WHERE student_id = :student_id LIMIT 1',
        {'student_id': student_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO resumes (student_id, content, pdf_path, completed)
                VALUES (:student_id, :content, :pdf_path, :completed)
            '''),
            {'student_id': student_id, 'content': content, 'pdf_path': pdf_path, 'completed': 1 if completed else 0}
        )
        db.session.commit()


def ensure_certificate(student_id, name, issuer, issue_date, link='', status='active'):
    exists = fetch_one(
        'SELECT id FROM certificates WHERE student_id = :student_id AND name = :name LIMIT 1',
        {'student_id': student_id, 'name': name}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO certificates (student_id, name, issuer, issue_date, link, status)
                VALUES (:student_id, :name, :issuer, :issue_date, :link, :status)
            '''),
            {'student_id': student_id, 'name': name, 'issuer': issuer, 'issue_date': issue_date, 'link': link, 'status': status}
        )
        db.session.commit()


def ensure_weekly_challenge(title, description, weight_percent=5.00):
    challenge_id = fetch_one(
        'SELECT id FROM weekly_challenges WHERE title = :title LIMIT 1',
        {'title': title}
    )
    if challenge_id is None:
        challenge_id = db.session.execute(
            text('''
                INSERT INTO weekly_challenges (title, description, weight_percent)
                VALUES (:title, :description, :weight_percent)
            '''),
            {'title': title, 'description': description, 'weight_percent': float(weight_percent)}
        ).lastrowid
        db.session.commit()
    return challenge_id


def ensure_challenge_result(challenge_id, student_id, score=88.00, feedback='Good effort.'):
    exists = fetch_one(
        'SELECT id FROM challenge_results WHERE challenge_id = :challenge_id AND student_id = :student_id LIMIT 1',
        {'challenge_id': challenge_id, 'student_id': student_id}
    )
    if exists is None:
        db.session.execute(
            text('''
                INSERT INTO challenge_results (challenge_id, student_id, score, feedback)
                VALUES (:challenge_id, :student_id, :score, :feedback)
            '''),
            {'challenge_id': challenge_id, 'student_id': student_id, 'score': float(score), 'feedback': feedback}
        )
        db.session.commit()


app = create_app()

with app.app_context():
    db.create_all()

    admin_id = ensure_admin()

    company_names = ['Infosys', 'TCS', 'Wipro', 'Accenture', 'HCL', 'Zoho', 'Cognizant', 'Capgemini']
    company_map = {name: ensure_company(name, f'{name} campus placement preparation track') for name in company_names}

    skill_config = {
        'Aptitude': 'Core',
        'Logical Reasoning': 'Core',
        'Verbal Ability': 'Core',
        'Programming': 'Core',
        'SQL': 'Core',
        'Communication': 'Communication',
        'Interview Skills': 'Communication',
        'DSA': 'Core',
        'OOP': 'Core',
        'DBMS': 'Core',
        'Problem Solving': 'Core',
        'Technical Interview': 'Communication',
        'Data Structures': 'Core',
        'Web Development': 'Core',
        'Group Discussion': 'Communication',
    }
    skill_map = {
        name: ensure_skill(name, category=category, description=f'{name} preparation and assessment')
        for name, category in skill_config.items()
    }

    company_skill_map = {
        'Infosys': ['Aptitude', 'Logical Reasoning', 'Verbal Ability', 'Programming', 'SQL', 'Communication', 'Interview Skills'],
        'TCS': ['Aptitude', 'Logical Reasoning', 'Programming', 'SQL', 'Communication'],
        'Wipro': ['Aptitude', 'Programming', 'DBMS', 'Communication', 'Interview Skills'],
        'Accenture': ['Aptitude', 'Verbal Ability', 'Programming', 'SQL', 'Communication'],
        'HCL': ['Logical Reasoning', 'Programming', 'SQL', 'Communication'],
        'Zoho': ['Programming', 'DSA', 'OOP', 'DBMS', 'SQL', 'Problem Solving', 'Technical Interview'],
        'Cognizant': ['Aptitude', 'Programming', 'SQL', 'Communication'],
        'Capgemini': ['Programming', 'Logical Reasoning', 'SQL', 'Communication', 'Interview Skills'],
    }

    for company_name, skills_for_company in company_skill_map.items():
        for idx, skill_name in enumerate(skills_for_company, start=1):
            ensure_company_skill(company_map[company_name], skill_map[skill_name], priority=idx, required=True)

    student_rows = [
        ('Rahul Sharma', 'rahul@student.com', 'Student@123', 'CSE', 2025, 8.70, 0, 0, '9876543210', 'ABC College', company_map['Infosys']),
        ('Priya Nair', 'priya@student.com', 'Student@123', 'ECE', 2025, 8.40, 1, 1, '9123456780', 'XYZ College', company_map['TCS']),
        ('Arjun Kumar', 'arjun@student.com', 'Student@123', 'IT', 2024, 7.90, 0, 0, '9988776655', 'PQR College', company_map['Wipro']),
    ]

    student_map = {}
    for name, email, password, department, year, cgpa, backlog_count, backlogs, phone, college_name, dream_company_id in student_rows:
        student_id = ensure_student(name, email, password, department, year, cgpa, backlog_count, backlogs, phone, college_name, dream_company_id)
        student_map[email] = student_id
        ensure_student_company(student_id, dream_company_id, status='selected')

    for student_id in student_map.values():
        for skill_name in ['Aptitude', 'Programming', 'SQL', 'Communication']:
            ensure_student_skill(student_id, skill_map[skill_name], completed=True, score=80.00, proficiency=80, completion_percent=80)

    project_rows = [
        (
            'Smart Resume Analyzer',
            'smart-resume-analyzer',
            'Analyze candidate resumes and rank skills',
            'Build a system that reads resume text and extracts structured information for hiring teams.',
            'Develop a program that reads resume content and extracts structured information for recruitment teams.',
            'Beginner',
            100,
            1800,
            'Useful for Infosys and TCS recruitment screening.',
            'Extract skills, education, and experience; generate a resume summary.',
            'Python, regex, string processing, structured output.',
            'Resume text',
            'Structured skill summary',
            'Use pattern matching and text parsing to extract relevant information.',
            'Create a parser that produces a clean summary with skills and experience.',
            'active',
            ['Infosys', 'TCS'],
            ['Programming', 'SQL', 'Communication'],
        ),
        (
            'Placement Dashboard',
            'placement-dashboard',
            'Track company requirements and student readiness',
            'Create a dashboard to display the strengths and gaps of students against placement company requirements.',
            'Design a dashboard that shows required skills and the matching skill scores for a candidate.',
            'Intermediate',
            100,
            1800,
            'Useful for Wipro, Capgemini, and Cognizant hiring workflows.',
            'Display skill scores, company filters, and readiness metrics.',
            'Web app, filtering, reporting, data presentation.',
            'Student details and company filter input',
            'Dashboard metrics and readiness output',
            'Use a company-to-skill matrix and compare it with student skill scores.',
            'Create a visual dashboard with filters and summary metrics.',
            'active',
            ['Wipro', 'Capgemini'],
            ['Programming', 'SQL', 'Data Structures', 'Communication'],
        ),
    ]

    project_map = {}
    for row in project_rows:
        title, slug, short_description, description, problem_statement, difficulty, max_score, time_limit_seconds, company_relevance, objectives, requirements, expected_input, expected_output, evaluation_criteria, reference_solution, reference_approach, status, company_names, skill_names = row
        project_id = ensure_project(
            title=title,
            slug=slug,
            short_description=short_description,
            description=description,
            problem_statement=problem_statement,
            difficulty=difficulty,
            max_score=max_score,
            time_limit_seconds=time_limit_seconds,
            company_relevance=company_relevance,
            objectives=objectives,
            requirements=requirements,
            expected_input=expected_input,
            expected_output=expected_output,
            evaluation_criteria=evaluation_criteria,
            reference_solution=reference_solution,
            reference_approach=reference_approach,
            status=status,
            created_by=admin_id,
        )
        project_map[title] = project_id

        for company_name in company_names:
            ensure_project_company(project_id, company_map[company_name])

        for skill_name in skill_names:
            ensure_project_skill(project_id, skill_map[skill_name], importance=5)

        test_cases = [
            ('resume text', 'skills: python, sql, communication', 10, 0),
            ('candidate experience', 'experience: 2 years', 10, 0),
        ] if title == 'Smart Resume Analyzer' else [
            ('company filter', 'selected company data', 10, 0),
            ('skill summary', 'readiness percentage', 10, 0),
        ]

        for test_input, expected_output, points, is_hidden in test_cases:
            ensure_project_test_case(project_id, test_input, expected_output, points, is_hidden)

        hints = [
            (1, 'Start by splitting the resume into sections.'),
            (2, 'Use keyword matching for skills and experience.'),
        ] if title == 'Smart Resume Analyzer' else [
            (1, 'Map the company required skills to student skill scores.'),
            (2, 'Use a readable summary table with filters.'),
        ]

        for hint_order, hint in hints:
            ensure_project_hint(project_id, hint_order, hint)

    learning_plan_map = {
        'Aptitude': 'Aptitude Plan',
        'Programming': 'Programming Plan',
        'SQL': 'SQL Plan',
    }

    for skill_name, plan_title in learning_plan_map.items():
        plan_id = ensure_learning_plan(plan_title, skill_map[skill_name], duration_days=30, details=f'{skill_name} daily training plan')
        if skill_name == 'Aptitude':
            ensure_task(plan_id, 1, 'Percentage Basics', 'Learn basic percentage concepts and formulas.', is_optional=False)
            ensure_task(plan_id, 2, 'Profit and Loss', 'Practice profit and loss questions.', is_optional=False)
        elif skill_name == 'Programming':
            ensure_task(plan_id, 1, 'Programming Basics', 'Learn variables, data types and operators.', is_optional=False)
            ensure_task(plan_id, 2, 'Conditional Statements', 'Practice if/else logic.', is_optional=False)
        elif skill_name == 'SQL':
            ensure_task(plan_id, 1, 'SQL SELECT', 'Learn SELECT queries and WHERE clauses.', is_optional=False)
            ensure_task(plan_id, 2, 'SQL JOIN', 'Practice INNER JOIN and LEFT JOIN.', is_optional=False)

    for student_id in student_map.values():
        programming_plan_id = fetch_one('SELECT id FROM learning_plans WHERE title = :title LIMIT 1', {'title': 'Programming Plan'})
        if programming_plan_id is not None:
            basics_task_id = fetch_one(
                'SELECT id FROM tasks WHERE plan_id = :plan_id AND title = :title LIMIT 1',
                {'plan_id': programming_plan_id, 'title': 'Programming Basics'}
            )
            if basics_task_id is not None:
                ensure_student_task(student_id, basics_task_id, completed=True, status='completed')

        ensure_progress(student_id)
        ensure_mock_interview(student_id)
        ensure_resume(student_id)
        ensure_certificate(student_id, 'Python Fundamentals', 'SkillForge', '2025-01-15', 'https://example.com/certificate/python', 'active')

    challenge_rows = [
        ('Weekly Coding Challenge', 'Solve coding and algorithmic tasks designed for placement preparation.', 10.00),
        ('Communication Sprint', 'Practice verbal communication and interview delivery.', 8.50),
    ]
    challenge_map = {}
    for title, description, weight_percent in challenge_rows:
        challenge_map[title] = ensure_weekly_challenge(title, description, weight_percent)

    for student_id in student_map.values():
        for title, challenge_id in challenge_map.items():
            score = 90.00 if 'Coding' in title else 85.00
            feedback = 'Strong performance and good improvement.' if 'Coding' in title else 'Solid communication and clarity.'
            ensure_challenge_result(challenge_id, student_id, score=score, feedback=feedback)

    db.session.commit()
    print('Seed data inserted successfully using the existing schema and config settings.')
