from placement_training import db
from placement_training.models import (
    AptitudeAttempt,
    Company,
    GeneralAptitudeTest,
    GroupDiscussionResult,
    HRInterviewAttempt,
    LearningPlan,
    Progress,
    Student,
    StudentSkill,
    TestResult,
)


def _bounded(value):
    return round(min(max(float(value or 0), 0), 100), 2)


def _test_matches_skill(result, skill_name):
    label = f'{result.test.title} {result.test.test_type}'.lower()
    skill_words = [word for word in skill_name.lower().split() if len(word) > 2]
    return any(word in label for word in skill_words)


def ensure_company_skills(student_id, company_id):
    """Create missing student skill rows for a company's required skills."""
    company = Company.query.get(company_id)
    if not company:
        return []
    records = []
    for company_skill in company.company_skills:
        record = StudentSkill.query.filter_by(
            student_id=student_id, skill_id=company_skill.skill_id
        ).first()
        if not record:
            record = StudentSkill(student_id=student_id, skill_id=company_skill.skill_id)
            db.session.add(record)
        records.append(record)
    return records


def get_skill_progress(student_id, company_id=None):
    """Return required company skills and their evidence-based percentages."""
    student = Student.query.get(student_id)
    if not student:
        return []
    company_id = company_id or student.dream_company_id
    student_skills = (
        ensure_company_skills(student_id, company_id)
        if company_id else list(student.student_skills)
    )

    test_results = TestResult.query.filter_by(student_id=student_id).all()
    aptitude_results = AptitudeAttempt.query.filter_by(student_id=student_id).all()
    aptitude_results += GeneralAptitudeTest.query.filter_by(
        student_id=student_id, status='completed'
    ).all()
    progress_items = []
    for student_skill in student_skills:
        skill_name = student_skill.skill.name
        evidence = []
        if 'aptitude' in skill_name.lower():
            evidence.extend(item.percentage for item in aptitude_results)
        evidence.extend(
            result.percentage for result in test_results
            if _test_matches_skill(result, skill_name)
        )

        if 'interview' in skill_name.lower():
            interview_query = HRInterviewAttempt.query.filter_by(student_id=student_id)
            if company_id:
                interview_query = interview_query.filter_by(company_id=company_id)
            attempted_questions = {
                attempt.question_number for attempt in interview_query.all()
            }
            evidence.append(
                len(attempted_questions) / 10 * 100
                if attempted_questions else 0
            )

        skill_tasks = [
            task for task in student.task_records
            if task.task and task.task.skill_id == student_skill.skill_id
        ]
        if skill_tasks:
            evidence.append(
                sum(1 for task in skill_tasks if task.completed) / len(skill_tasks) * 100
            )

        plans = LearningPlan.query.filter_by(
            student_id=student_id, skill_id=student_skill.skill_id
        ).all()
        evidence.extend(plan.completion_percentage for plan in plans)
        if not evidence and student_skill.score:
            evidence.append(student_skill.score)

        percentage = _bounded(sum(evidence) / len(evidence)) if evidence else 0
        student_skill.completion_percent = percentage
        progress_items.append({
            'skill_id': student_skill.skill_id,
            'skill_name': skill_name,
            'percentage': percentage,
        })
    return progress_items


def calculate_student_progress(student_id, company_id=None):
    student = Student.query.get(student_id)
    if not student:
        return None

    skill_progress = get_skill_progress(student_id, company_id)
    skill_completion = (
        sum(item['percentage'] for item in skill_progress) / len(skill_progress)
        if skill_progress else 0
    )
    total_tasks = len(student.task_records)
    completed_tasks = sum(1 for task in student.task_records if task.completed)
    task_completion = (completed_tasks / total_tasks * 100) if total_tasks else 0
    test_results = TestResult.query.filter_by(student_id=student_id).all()
    test_performance = (
        sum(result.percentage for result in test_results) / len(test_results)
        if test_results else 0
    )
    aptitude_results = AptitudeAttempt.query.filter_by(student_id=student_id).all()
    aptitude_results += GeneralAptitudeTest.query.filter_by(
        student_id=student_id, status='completed'
    ).all()
    aptitude_performance = (
        sum(item.percentage for item in aptitude_results) / len(aptitude_results)
        if aptitude_results else 0
    )
    discussion_results = GroupDiscussionResult.query.filter_by(student_id=student_id).all()
    discussion_performance = (
        sum(item.overall_score for item in discussion_results) / len(discussion_results)
        if discussion_results else 0
    )

    progress = Progress.query.filter_by(student_id=student_id).first()
    if not progress:
        progress = Progress(student_id=student_id)
        db.session.add(progress)
    progress.skill_completion_percent = _bounded(skill_completion)
    progress.task_completion_percent = _bounded(task_completion)
    progress.overall_progress_percent = _bounded(skill_completion)
    progress.skill_completion = _bounded(skill_completion)
    progress.task_completion = _bounded(task_completion)
    progress.test_performance = _bounded(test_performance)
    progress.aptitude_performance = _bounded(aptitude_performance)
    progress.discussion_performance = _bounded(discussion_performance)
    progress.overall_progress = _bounded(skill_completion)
    db.session.commit()
    return progress


def get_leaderboard():
    records = Progress.query.order_by(Progress.overall_progress.desc()).all()
    return [
        {
            'rank': index,
            'student_name': record.student.name,
            'progress': round(record.overall_progress, 2),
            'student_id': record.student_id,
        }
        for index, record in enumerate(records, start=1)
        if record.student
    ]
