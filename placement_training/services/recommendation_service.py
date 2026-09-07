def recommend_skills(student_data):
    """student_data is a dictionary with scores per skill."""
    scores = dict(student_data)
    sorted_skills = sorted(scores.items(), key=lambda item: item[1])
    weak_skills = [name for name, value in sorted_skills if value < 70]

    recommendations = []
    for skill_name in weak_skills:
        recommendations.append(f'Improve {skill_name}')

    if not recommendations:
        return ['Keep practicing core fundamentals and revise weekly tests']

    if 'SQL' in scores and scores['SQL'] < 70:
        recommendations.append('Practice SQL queries daily')
    if 'Communication' in scores and scores['Communication'] < 70:
        recommendations.append('Improve communication by speaking daily and solving mock HR questions')
    if 'Programming' in scores and scores['Programming'] < 70:
        recommendations.append('Solve more coding problems on arrays, loops, and functions')

    return recommendations[:5]
