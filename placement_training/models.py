from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

from placement_training import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, plain_password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(plain_password)

    def verify_password(self, plain_password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, plain_password)


class Student(db.Model, UserMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(120))
    year = db.Column(db.Integer)
    cgpa = db.Column(db.Float, default=0.0)
    backlog_count = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(30))
    dream_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])

    dream_company = db.relationship('Company', back_populates='students')
    student_skills = db.relationship('StudentSkill', back_populates='student', cascade='all, delete-orphan')
    task_records = db.relationship('StudentTask', back_populates='student', cascade='all, delete-orphan')
    test_results = db.relationship('TestResult', back_populates='student', cascade='all, delete-orphan')
    progress_records = db.relationship('Progress', back_populates='student', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', back_populates='student', cascade='all, delete-orphan')
    resumes = db.relationship('Resume', back_populates='student', cascade='all, delete-orphan')
    mock_interviews = db.relationship('MockInterview', back_populates='student', cascade='all, delete-orphan')
    student_companies = db.relationship('StudentCompany', back_populates='student', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, plain_password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(plain_password)

    def verify_password(self, plain_password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, plain_password)


class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return f'admin:{self.id}'

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, plain_password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(plain_password)

    def verify_password(self, plain_password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, plain_password)


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    eligibility_criteria = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship('Student', back_populates='dream_company')
    company_skills = db.relationship('CompanySkill', back_populates='company', cascade='all, delete-orphan')
    tests = db.relationship('Test', back_populates='company', cascade='all, delete-orphan')
    student_companies = db.relationship('StudentCompany', back_populates='company', cascade='all, delete-orphan')


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(80), default='Core')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company_skills = db.relationship('CompanySkill', back_populates='skill', cascade='all, delete-orphan')
    learning_plans = db.relationship('LearningPlan', back_populates='skill', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='skill', cascade='all, delete-orphan')
    student_skills = db.relationship('StudentSkill', back_populates='skill', cascade='all, delete-orphan')


class CompanySkill(db.Model):
    __tablename__ = 'company_skills'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    required = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)

    __table_args__ = (UniqueConstraint('company_id', 'skill_id', name='uq_company_skill'),)

    company = db.relationship('Company', back_populates='company_skills')
    skill = db.relationship('Skill', back_populates='company_skills')


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, default=0.0)
    completion_percent = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (UniqueConstraint('student_id', 'skill_id', name='uq_student_skill'),)

    student = db.relationship('Student', back_populates='student_skills')
    skill = db.relationship('Skill', back_populates='student_skills')


class StudentCompany(db.Model):
    __tablename__ = 'student_companies'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    selected_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='selected')
    __table_args__ = (UniqueConstraint('student_id', 'company_id', name='uq_student_company'),)

    student = db.relationship('Student', back_populates='student_companies')
    company = db.relationship('Company', back_populates='student_companies')


class StudentCompanySkill(db.Model):
    __tablename__ = 'student_company_skills'

    id = db.Column(db.Integer, primary_key=True)
    student_company_id = db.Column(db.Integer, db.ForeignKey('student_companies.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('student_company_id', 'skill_id', name='uq_student_company_skill'),)

    student_company = db.relationship('StudentCompany', backref=db.backref('company_skills_selected', cascade='all, delete-orphan'))
    skill = db.relationship('Skill', backref=db.backref('student_company_selections', cascade='all, delete-orphan'))


class LearningPlan(db.Model):
    __tablename__ = 'learning_plans'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    completed_days = db.Column(db.Integer, default=0)
    total_days = db.Column(db.Integer, default=30)
    completion_percentage = db.Column(db.Float, default=0.0)

    skill = db.relationship('Skill', back_populates='learning_plans')


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    day_number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    skill = db.relationship('Skill', back_populates='tasks')
    student_tasks = db.relationship('StudentTask', back_populates='task', cascade='all, delete-orphan')


class StudentTask(db.Model):
    __tablename__ = 'student_tasks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

    student = db.relationship('Student', back_populates='task_records')
    task = db.relationship('Task', back_populates='student_tasks')


class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    test_type = db.Column(db.String(80), default='weekly')
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    duration_minutes = db.Column(db.Integer, default=30)
    scheduled_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', back_populates='tests')
    questions = db.relationship('Question', back_populates='test', cascade='all, delete-orphan')
    results = db.relationship('TestResult', back_populates='test', cascade='all, delete-orphan')


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.String(10), nullable=False)
    explanation = db.Column(db.Text)

    test = db.relationship('Test', back_populates='questions')


class TestResult(db.Model):
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    passed = db.Column(db.Boolean, default=False)

    student = db.relationship('Student', back_populates='test_results')
    test = db.relationship('Test', back_populates='results')


class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    project_completion_percent = db.Column(db.Float, default=0.0)
    project_performance_percent = db.Column(db.Float, default=0.0)
    skill_completion_percent = db.Column(db.Float, default=0.0)
    task_completion_percent = db.Column(db.Float, default=0.0)
    challenge_performance_percent = db.Column(db.Float, default=0.0)
    overall_progress_percent = db.Column(db.Float, default=0.0)
    skill_completion = db.Column(db.Float, default=0.0)
    task_completion = db.Column(db.Float, default=0.0)
    test_performance = db.Column(db.Float, default=0.0)
    aptitude_performance = db.Column(db.Float, default=0.0)
    discussion_performance = db.Column(db.Float, default=0.0)
    overall_progress = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (UniqueConstraint('student_id', name='uq_progress_student'),)

    student = db.relationship('Student', back_populates='progress_records')


class MockInterview(db.Model):
    __tablename__ = 'mock_interviews'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    category = db.Column(db.String(80), default='technical')
    question = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', back_populates='mock_interviews')


class HRInterviewAttempt(db.Model):
    __tablename__ = 'hr_interview_attempts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    question_number = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False, default=0.0)
    feedback = db.Column(db.Text, nullable=False)
    improvement = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship('Student', backref=db.backref('hr_interview_attempts', cascade='all, delete-orphan'))
    company = db.relationship('Company')


class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    summary = db.Column(db.Text)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    projects = db.Column(db.Text)
    certifications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', back_populates='resumes')


class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    issuing_organization = db.Column(db.String(200), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    certificate_link = db.Column(db.String(255))
    status = db.Column(db.String(50), default='Pending')

    student = db.relationship('Student', back_populates='certificates')


class BankQuestion(db.Model):
    __tablename__ = 'bank_questions'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(512), nullable=False)
    option_b = db.Column(db.String(512), nullable=False)
    option_c = db.Column(db.String(512), nullable=False)
    option_d = db.Column(db.String(512), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    difficulty = db.Column(db.String(20), default='Easy')
    marks = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', backref=db.backref('bank_questions', cascade='all, delete-orphan'))
    skill = db.relationship('Skill', backref=db.backref('bank_questions', cascade='all, delete-orphan'))


class TestAttempt(db.Model):
    __tablename__ = 'test_attempts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    unanswered = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)

    student = db.relationship('Student', backref=db.backref('test_attempts', cascade='all, delete-orphan'))
    company = db.relationship('Company')


class StudentAnswer(db.Model):
    __tablename__ = 'student_answers'

    id = db.Column(db.Integer, primary_key=True)
    test_attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('bank_questions.id'), nullable=False)
    selected_answer = db.Column(db.String(1))
    is_correct = db.Column(db.Boolean, default=False)

    test_attempt = db.relationship('TestAttempt', backref=db.backref('answers', cascade='all, delete-orphan'))
    question = db.relationship('BankQuestion')


# ==================== NEW MODELS FOR APTITUDE FEATURES ====================

class AptitudeTopic(db.Model):
    __tablename__ = 'aptitude_topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('AptitudeQuestion', back_populates='topic', cascade='all, delete-orphan')
    attempts = db.relationship('AptitudeAttempt', back_populates='topic', cascade='all, delete-orphan')


class AptitudeQuestion(db.Model):
    __tablename__ = 'aptitude_questions'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('aptitude_topics.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(512), nullable=False)
    option_b = db.Column(db.String(512), nullable=False)
    option_c = db.Column(db.String(512), nullable=False)
    option_d = db.Column(db.String(512), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, D
    explanation = db.Column(db.Text)
    concept_definition = db.Column(db.Text)
    question_code = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('question_code', name='uq_aptitude_question_code'),)

    company = db.relationship('Company', backref=db.backref('aptitude_questions', cascade='all, delete-orphan'))
    topic = db.relationship('AptitudeTopic', back_populates='questions')


class AptitudeAttempt(db.Model):
    __tablename__ = 'aptitude_attempts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('aptitude_topics.id'), nullable=False)
    total_questions = db.Column(db.Integer, default=5)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('aptitude_attempts', cascade='all, delete-orphan'))
    company = db.relationship('Company', backref=db.backref('aptitude_attempts', cascade='all, delete-orphan'))
    topic = db.relationship('AptitudeTopic', back_populates='attempts')


class AptitudeQuestionAttempt(db.Model):
    __tablename__ = 'aptitude_question_attempts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('aptitude_topics.id'), nullable=False)
    question_key = db.Column(db.String(255), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    correct = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text)
    concept_definition = db.Column(db.Text)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint(
        'student_id', 'company_id', 'topic_id', 'question_key',
        name='uq_aptitude_question_once'
    ),)

    student = db.relationship('Student', backref=db.backref('aptitude_question_attempts', cascade='all, delete-orphan'))
    company = db.relationship('Company')
    topic = db.relationship('AptitudeTopic')


class GeneralAptitudeTest(db.Model):
    __tablename__ = 'general_aptitude_tests'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    total_questions = db.Column(db.Integer, default=10)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    unanswered = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='completed')  # pending, completed
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('general_aptitude_tests', cascade='all, delete-orphan'))


class ExtraAptitudeTest(db.Model):
    __tablename__ = 'extra_aptitude_tests'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    topic_name = db.Column(db.String(100))
    total_questions = db.Column(db.Integer, default=5)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('extra_aptitude_tests', cascade='all, delete-orphan'))


class ExtraAptitudeAnswer(db.Model):
    __tablename__ = 'extra_aptitude_answers'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('extra_aptitude_tests.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    question_key = db.Column(db.String(255), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text)
    concept = db.Column(db.Text)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    test = db.relationship('ExtraAptitudeTest', backref=db.backref('answers', cascade='all, delete-orphan'))
    student = db.relationship('Student')

    __table_args__ = (UniqueConstraint('student_id', 'question_key', name='uq_extra_aptitude_answer_once'),)


class TopicAptitudeTest(db.Model):
    __tablename__ = 'topic_aptitude_tests'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    phase = db.Column(db.String(20), nullable=False)
    total_questions = db.Column(db.Integer, default=10)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref=db.backref('topic_aptitude_tests', cascade='all, delete-orphan'))


class TopicAptitudeAnswer(db.Model):
    __tablename__ = 'topic_aptitude_answers'

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('topic_aptitude_tests.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    question_key = db.Column(db.String(255), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    selected_answer = db.Column(db.String(1), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text)
    concept = db.Column(db.Text)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    test = db.relationship('TopicAptitudeTest', backref=db.backref('answers', cascade='all, delete-orphan'))
    student = db.relationship('Student')

    __table_args__ = (UniqueConstraint('student_id', 'topic_name', 'question_key', name='uq_topic_aptitude_answer_once'),)


# ==================== NEW MODELS FOR GROUP DISCUSSION FEATURES ====================

class GroupDiscussionSession(db.Model):
    __tablename__ = 'group_discussion_sessions'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    max_participants = db.Column(db.Integer, default=8)
    duration_minutes = db.Column(db.Integer, default=30)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, in_progress, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('students.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company')
    participants = db.relationship('GroupDiscussionParticipant', back_populates='session', cascade='all, delete-orphan')
    results = db.relationship('GroupDiscussionResult', back_populates='session', cascade='all, delete-orphan')


class GroupDiscussionParticipant(db.Model):
    __tablename__ = 'group_discussion_participants'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('group_discussion_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_status = db.Column(db.String(20), default='active', nullable=False)
    left_at = db.Column(db.DateTime)
    participation_duration = db.Column(db.Integer, default=0)  # in seconds

    session = db.relationship('GroupDiscussionSession', back_populates='participants')
    student = db.relationship('Student', backref=db.backref('discussion_participations', cascade='all, delete-orphan'))


class GroupDiscussionResult(db.Model):
    __tablename__ = 'group_discussion_results'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('group_discussion_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # Evaluation criteria (0-100 scale)
    communication_score = db.Column(db.Float, default=0.0)
    participation_score = db.Column(db.Float, default=0.0)
    relevance_score = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    listening_score = db.Column(db.Float, default=0.0)
    team_interaction_score = db.Column(db.Float, default=0.0)
    
    # Overall performance
    overall_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)
    
    # Timestamps
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship('GroupDiscussionSession', back_populates='results')
    student = db.relationship('Student', backref=db.backref('discussion_results', cascade='all, delete-orphan'))
