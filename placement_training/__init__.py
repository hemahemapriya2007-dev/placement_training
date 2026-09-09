import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name=None):
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)

    from placement_training.models import Student, Admin
    from placement_training.routes.auth_routes import auth_bp
    from placement_training.routes.student_routes import student_bp
    from placement_training.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            user_columns = {column['name'] for column in inspector.get_columns('users')}
            if 'password_hash' not in user_columns:
                db.session.execute(text('ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NULL'))
                db.session.commit()
            migrations = {
                'student_skills': {
                    'completion_percent': 'FLOAT DEFAULT 0',
                },
                'learning_plans': {
                    'title': "VARCHAR(255) DEFAULT 'Learning Plan'",
                    'completed_days': 'INT DEFAULT 0',
                    'total_days': 'INT DEFAULT 30',
                    'completion_percentage': 'FLOAT DEFAULT 0',
                },
                'group_discussion_participants': {
                    'attendance_status': "VARCHAR(20) DEFAULT 'active'",
                },
                'progress': {
                    'project_completion_percent': 'FLOAT DEFAULT 0',
                    'project_performance_percent': 'FLOAT DEFAULT 0',
                    'skill_completion_percent': 'FLOAT DEFAULT 0',
                    'task_completion_percent': 'FLOAT DEFAULT 0',
                    'challenge_performance_percent': 'FLOAT DEFAULT 0',
                    'overall_progress_percent': 'FLOAT DEFAULT 0',
                },
                'aptitude_questions': {
                    'company_id': 'INT NULL',
                    'question_code': 'VARCHAR(64) NULL',
                },
                'aptitude_attempts': {
                    'company_id': 'INT NULL',
                },
                'aptitude_question_attempts': {
                    'explanation': 'TEXT NULL',
                    'concept_definition': 'TEXT NULL',
                },
            }
            for table_name, columns in migrations.items():
                existing_columns = {column['name'] for column in inspect(db.engine).get_columns(table_name)}
                for column_name, definition in columns.items():
                    if column_name not in existing_columns:
                        db.session.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}'))
            db.session.commit()
            if 'progress' in inspect(db.engine).get_table_names():
                progress_indexes = {
                    index['name'] for index in inspect(db.engine).get_indexes('progress')
                }
                if 'uq_progress_student' not in progress_indexes:
                    db.session.execute(text(
                        'CREATE UNIQUE INDEX uq_progress_student ON progress (student_id)'
                    ))
                    db.session.commit()
        except Exception:
            db.session.rollback()

        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin', email='admin@placement.com')
            admin.password = 'admin123'
            db.session.add(admin)
            db.session.commit()
        elif admin.email == 'admin@placement.com':
            try:
                password_valid = admin.verify_password('admin123')
            except (TypeError, ValueError):
                password_valid = False
            if not password_valid:
                admin.password = 'admin123'
                db.session.commit()
        
        # Initialize Group Discussion skill and add to companies
        from placement_training.models import Skill, Company, CompanySkill
        
        gd_skill = Skill.query.filter_by(name='Group Discussion').first()
        if not gd_skill:
            gd_skill = Skill(
                name='Group Discussion',
                category='Communication',
                description='Develop skills in group discussions, team communication, and collaborative problem-solving.'
            )
            db.session.add(gd_skill)
            db.session.commit()

            # Add to all companies
            companies = Company.query.all()
            for company in companies:
                existing = CompanySkill.query.filter_by(
                    company_id=company.id,
                    skill_id=gd_skill.id
                ).first()
                if not existing:
                    cs = CompanySkill(
                        company_id=company.id,
                        skill_id=gd_skill.id,
                        required=True,
                        priority=8
                    )
                    db.session.add(cs)
            db.session.commit()

        # Seed the database-backed company/topic bank once. Existing attempts
        # remain immutable when new questions are added later by an admin.
        from placement_training.models import AptitudeTopic, AptitudeQuestion
        from placement_training.services.aptitude_topics_service import APTITUDE_TOPICS
        import hashlib

        companies = Company.query.all()
        for company in companies:
            for topic_name, topic_data in APTITUDE_TOPICS.items():
                topic = AptitudeTopic.query.filter_by(name=topic_name).first()
                if not topic:
                    topic = AptitudeTopic(name=topic_name, description=topic_data['description'])
                    db.session.add(topic)
                    db.session.flush()
                if AptitudeQuestion.query.filter_by(company_id=company.id, topic_id=topic.id).count() >= 5:
                    continue
                for index, item in enumerate(topic_data['questions'][:5]):
                    question_code = hashlib.sha256(
                        f'{company.id}:{topic_name}:{index}:{item["question"]}'.encode()
                    ).hexdigest()[:64]
                    if AptitudeQuestion.query.filter_by(question_code=question_code).first():
                        continue
                    db.session.add(AptitudeQuestion(
                        company_id=company.id,
                        topic_id=topic.id,
                        question_text=f'{company.name} pattern: {item["question"]}',
                        option_a=item['options'][0], option_b=item['options'][1],
                        option_c=item['options'][2], option_d=item['options'][3],
                        correct_answer=item['correct_answer'],
                        explanation=item['explanation'],
                        concept_definition=item['concept'],
                        question_code=question_code,
                    ))
        db.session.commit()

    return app
