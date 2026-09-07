from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from placement_training import db
from placement_training.models import Student, Company, Skill, LearningPlan, Task, Test, Question, Progress, StudentTask, TestResult, AptitudeAttempt, GeneralAptitudeTest, GroupDiscussionResult

admin_bp = Blueprint('admin', __name__)


def admin_required(func):
    from functools import wraps
    from flask_login import current_user

    @wraps(func)
    @login_required
    def decorated(*args, **kwargs):
        if not hasattr(current_user, 'username'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.admin_login'))
        return func(*args, **kwargs)

    return decorated


@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    students = Student.query.all()
    companies = Company.query.count()
    tests = Test.query.count()
    avg_progress = round(sum((p.overall_progress or 0) for p in Progress.query.all()) / len(Progress.query.all()), 2) if Progress.query.count() else 0
    return render_template('admin_dashboard.html', students=students, companies=companies, tests=tests, avg_progress=avg_progress)


@admin_bp.route('/admin/student/<int:student_id>')
@admin_required
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    from placement_training.services.progress_service import calculate_student_progress
    progress = calculate_student_progress(student.id)
    selected_skills = student.student_skills
    completed_skills = [item for item in selected_skills if item.completed]
    pending_skills = [item for item in selected_skills if not item.completed]
    completed_tasks = [item for item in student.task_records if item.completed]
    pending_tasks = [item for item in student.task_records if not item.completed]
    test_results = TestResult.query.filter_by(student_id=student.id).order_by(TestResult.submitted_at.desc()).all()
    aptitude_attempts = AptitudeAttempt.query.filter_by(student_id=student.id).order_by(AptitudeAttempt.completed_at.desc()).all()
    general_tests = GeneralAptitudeTest.query.filter_by(student_id=student.id).order_by(GeneralAptitudeTest.completed_at.desc()).all()
    discussions = GroupDiscussionResult.query.filter_by(student_id=student.id).all()
    aptitude_scores = [item.percentage for item in aptitude_attempts] + [item.percentage for item in general_tests]
    test_scores = [item.percentage for item in test_results]
    return render_template(
        'admin_student_detail.html',
        student=student,
        progress=progress,
        selected_skills=selected_skills,
        completed_skills=completed_skills,
        pending_skills=pending_skills,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        test_results=test_results,
        aptitude_attempts=aptitude_attempts,
        general_tests=general_tests,
        discussions=discussions,
        aptitude_scores=aptitude_scores,
        test_scores=test_scores,
    )


@admin_bp.route('/admin/students')
@admin_required
def students():
    students = Student.query.all()
    return render_template('admin_students.html', students=students)


@admin_bp.route('/admin/companies')
@admin_required
def companies():
    companies = Company.query.all()
    return render_template('admin_companies.html', companies=companies)


@admin_bp.route('/admin/company/create', methods=['GET', 'POST'])
@admin_required
def create_company():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        eligibility = request.form.get('eligibility_criteria')
        if Company.query.filter_by(name=name).first():
            flash('Company with that name already exists.', 'warning')
            return redirect(url_for('admin.companies'))
        company = Company(name=name, description=description, eligibility_criteria=eligibility)
        db.session.add(company)
        db.session.commit()
        flash('Company created.', 'success')
        return redirect(url_for('admin.companies'))
    return render_template('admin_company_form.html')


@admin_bp.route('/admin/company/edit/<int:company_id>', methods=['GET', 'POST'])
@admin_required
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == 'POST':
        company.name = request.form.get('name')
        company.description = request.form.get('description')
        company.eligibility_criteria = request.form.get('eligibility_criteria')
        db.session.commit()
        flash('Company updated.', 'success')
        return redirect(url_for('admin.companies'))
    return render_template('admin_company_form.html', company=company)


@admin_bp.route('/admin/company/delete/<int:company_id>', methods=['POST'])
@admin_required
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash('Company deleted.', 'success')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/admin/skills')
@admin_required
def skills():
    skills = Skill.query.all()
    return render_template('admin_skills.html', skills=skills)


@admin_bp.route('/admin/skill/create', methods=['GET', 'POST'])
@admin_required
def create_skill():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        if Skill.query.filter_by(name=name).first():
            flash('Skill already exists.', 'warning')
            return redirect(url_for('admin.skills'))
        skill = Skill(name=name, category=category, description=description)
        db.session.add(skill)
        db.session.commit()
        flash('Skill created.', 'success')
        return redirect(url_for('admin.skills'))
    return render_template('admin_skill_form.html')


@admin_bp.route('/admin/skill/edit/<int:skill_id>', methods=['GET', 'POST'])
@admin_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if request.method == 'POST':
        skill.name = request.form.get('name')
        skill.category = request.form.get('category')
        skill.description = request.form.get('description')
        db.session.commit()
        flash('Skill updated.', 'success')
        return redirect(url_for('admin.skills'))
    return render_template('admin_skill_form.html', skill=skill)


@admin_bp.route('/admin/skill/delete/<int:skill_id>', methods=['POST'])
@admin_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted.', 'success')
    return redirect(url_for('admin.skills'))


@admin_bp.route('/admin/tests')
@admin_required
def tests():
    tests = Test.query.all()
    return render_template('admin_tests.html', tests=tests)


@admin_bp.route('/admin/test/create', methods=['GET', 'POST'])
@admin_required
def create_test():
    if request.method == 'POST':
        title = request.form.get('title')
        test_type = request.form.get('test_type', 'weekly')
        duration_minutes = int(request.form.get('duration_minutes') or 30)
        company_id = request.form.get('company_id')
        test = Test(title=title, test_type=test_type, company_id=int(company_id) if company_id else None, duration_minutes=duration_minutes)
        db.session.add(test)
        db.session.commit()
        flash('Test created successfully.', 'success')
        return redirect(url_for('admin.tests'))
    companies = Company.query.all()
    return render_template('admin_test_form.html', companies=companies)


@admin_bp.route('/admin/leaderboard')
@admin_required
def leaderboard():
    from placement_training.services.progress_service import get_leaderboard
    return render_template('admin_leaderboard.html', leaderboard=get_leaderboard())


# ==================== INITIALIZATION ROUTES ====================

@admin_bp.route('/admin/init-group-discussion')
@admin_required
def init_group_discussion():
    """Initialize Group Discussion skill and add to all companies"""
    from placement_training.models import CompanySkill
    
    # Check if Group Discussion skill exists
    gd_skill = Skill.query.filter_by(name='Group Discussion').first()
    
    if not gd_skill:
        # Create the skill
        gd_skill = Skill(
            name='Group Discussion',
            category='Communication',
            description='Develop skills in group discussions, team communication, and collaborative problem-solving.'
        )
        db.session.add(gd_skill)
        db.session.commit()
        message = 'Group Discussion skill created successfully. '
    else:
        message = 'Group Discussion skill already exists. '
    
    # Add to all companies if not already present
    companies = Company.query.all()
    added_count = 0
    
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
            added_count += 1
    
    db.session.commit()
    message += f'Added to {added_count} companies.'
    flash(message, 'success')
    return redirect(url_for('admin.companies'))
