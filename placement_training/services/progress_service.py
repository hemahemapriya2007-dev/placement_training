from placement_training.models import Progress, Student, StudentTask, TestResult, StudentSkill, AptitudeAttempt, GeneralAptitudeTest, GroupDiscussionResult
from placement_training import db


def calculate_student_progress(student_id):
    student = Student.query.get(student_id)
    if not student:
        return None

    # Existing skill completion calculation
    skill_completion = 0
    if student.student_skills:
        completed = sum(1 for item in student.student_skills if item.completed)
        skill_completion = (completed / len(student.student_skills)) * 100 if student.student_skills else 0

    # Existing task completion calculation
    total_tasks = len(student.task_records)
    completed_tasks = sum(1 for task in student.task_records if task.completed)
    task_completion = (completed_tasks / total_tasks * 100) if total_tasks else 0

    # Existing test performance calculation
    test_results = TestResult.query.filter_by(student_id=student_id).all()
    test_performance = 0
    if test_results:
        test_performance = sum(result.percentage for result in test_results) / len(test_results)

    # NEW: Aptitude performance calculation
    aptitude_performance = 0
    aptitude_attempts = AptitudeAttempt.query.filter_by(student_id=student_id).all()
    general_tests = GeneralAptitudeTest.query.filter_by(student_id=student_id).all()
    
    all_aptitude = aptitude_attempts + general_tests
    if all_aptitude:
        aptitude_performance = sum(item.percentage for item in all_aptitude) / len(all_aptitude)

    # NEW: Group Discussion performance calculation
    discussion_performance = 0
    discussion_results = GroupDiscussionResult.query.filter_by(student_id=student_id).all()
    if discussion_results:
        discussion_performance = sum(item.overall_score for item in discussion_results) / len(discussion_results)

    # Extended progress formula: include aptitude and discussion
    # Old formula: (0.4 * skill) + (0.3 * task) + (0.3 * test)
    # New formula: (0.3 * skill) + (0.2 * task) + (0.2 * test) + (0.15 * aptitude) + (0.15 * discussion)
    overall_progress = (0.3 * skill_completion) + (0.2 * task_completion) + (0.2 * test_performance) + (0.15 * aptitude_performance) + (0.15 * discussion_performance)

    progress = Progress.query.filter_by(student_id=student_id).first()
    if not progress:
        progress = Progress(student_id=student_id)
        db.session.add(progress)

    progress.skill_completion = skill_completion
    progress.task_completion = task_completion
    progress.test_performance = test_performance
    progress.aptitude_performance = aptitude_performance
    progress.discussion_performance = discussion_performance
    progress.overall_progress = overall_progress
    db.session.commit()
    return progress


def get_leaderboard():
    """Get leaderboard sorted by overall progress"""
    records = Progress.query.order_by(Progress.overall_progress.desc()).all()
    leaderboard = []
    for index, record in enumerate(records, start=1):
        student = Student.query.get(record.student_id)
        if student:
            leaderboard.append({
                'rank': index,
                'student_name': student.name,
                'progress': round(record.overall_progress, 2),
                'student_id': student.id
            })
    return leaderboard
