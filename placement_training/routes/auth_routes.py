import uuid

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func

from placement_training import db, login_manager
from placement_training.models import Student, Admin, User
from sqlalchemy import text


auth_bp = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    if str(user_id).startswith('admin:'):
        return Admin.query.filter_by(id=str(user_id).split(':', 1)[1]).first()
    user = Student.query.filter_by(id=user_id).first()
    if user:
        return user
    return Admin.query.filter_by(id=user_id).first()


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if hasattr(current_user, 'dream_company_id'):
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.student_login'))


@auth_bp.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        department = request.form.get('department', '').strip() or None
        year_value = request.form.get('year', '').strip()
        year = int(year_value) if year_value.isdigit() else None
        cgpa_value = request.form.get('cgpa', '').strip()
        cgpa = float(cgpa_value) if cgpa_value else 0.0
        backlog_value = request.form.get('backlog_count', '').strip()
        backlog_count = int(backlog_value) if backlog_value else 0
        phone = request.form.get('phone', '').strip() or None

        if not name:
            flash('Name is required.', 'danger')
            return render_template('register.html')
        if not email:
            flash('Email is required.', 'danger')
            return render_template('register.html')
        if not password:
            flash('Password is required.', 'danger')
            return render_template('register.html')
        if not year or year < 1 or year > 8:
            flash('Please enter a valid academic year.', 'danger')
            return render_template('register.html')
        if cgpa < 0 or cgpa > 10:
            flash('Please enter a valid CGPA between 0 and 10.', 'danger')
            return render_template('register.html')

        if Student.query.filter_by(email=email).first():
            flash('A student with this email already exists.', 'warning')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'warning')
            return render_template('register.html')

        try:
            user = User(name=name, email=email)
            user.password = password
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                student_id=f'STUDENT-{uuid.uuid4().hex[:10].upper()}',
                name=name,
                email=email,
                department=department,
                year=year,
                cgpa=cgpa,
                backlog_count=backlog_count,
                phone=phone,
            )
            student.password = password
            db.session.add(student)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            flash(f'Registration failed: {exc}', 'danger')
            return render_template('register.html')

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.student_login'))

    return render_template('register.html')


@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        student = Student.query.filter_by(email=email).first()

        if student and student.verify_password(password):
            login_user(student)
            flash('Welcome back!', 'success')
            return redirect(url_for('student.dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        admin = Admin.query.filter(
            (func.lower(Admin.username) == username.lower()) |
            (func.lower(Admin.email) == username.lower())
        ).first()

        try:
            valid_password = bool(admin and admin.password_hash and admin.verify_password(password))
        except (TypeError, ValueError):
            valid_password = False

        if valid_password:
            login_user(admin)
            flash('Admin login successful.', 'success')
            return redirect(url_for('admin.dashboard'))

        flash('Invalid administrator credentials.', 'danger')

    return render_template('admin_login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.student_login'))


@auth_bp.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Administrator logged out.', 'info')
    return redirect(url_for('auth.admin_login'))

@auth_bp.route('/test-db')
def test_db():
    try:
        db.session.execute(text("SELECT 1"))
        return """
        <h1>MySQL Connected Successfully! ✅</h1>
        <p>Placement Training database connection is working.</p>
        """
    except Exception as e:
        return f"""
        <h1>MySQL Connection Failed ❌</h1>
        <p>{e}</p>
        """
