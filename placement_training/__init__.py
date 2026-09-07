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
        except Exception:
            pass

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

    return app
