"""Additive company-wise aptitude practice bank."""

import hashlib
import random

TOPICS = (
    'Quantitative Aptitude', 'Logical Reasoning', 'Data Interpretation',
    'Probability', 'Time and Work', 'Number Systems',
    'Permutations and Combinations', 'Profit, Loss and Percentage',
)

COMPANY_TOPICS = {
    'Infosys': TOPICS[:5],
    'TCS': (TOPICS[1], TOPICS[2], TOPICS[4], TOPICS[5], TOPICS[7]),
    'Wipro': (TOPICS[0], TOPICS[2], TOPICS[3], TOPICS[5], TOPICS[6]),
    'Accenture': (TOPICS[0], TOPICS[1], TOPICS[3], TOPICS[4], TOPICS[7]),
    'HCL': (TOPICS[1], TOPICS[2], TOPICS[4], TOPICS[6], TOPICS[7]),
    'Zoho': (TOPICS[0], TOPICS[3], TOPICS[5], TOPICS[6], TOPICS[7]),
    'Cognizant': (TOPICS[0], TOPICS[2], TOPICS[3], TOPICS[4], TOPICS[6]),
    'Capgemini': (TOPICS[1], TOPICS[2], TOPICS[4], TOPICS[5], TOPICS[7]),
}

_SCENARIOS = {
    'Infosys': 'a software release team', 'TCS': 'a banking migration team',
    'Wipro': 'a healthcare support team', 'Accenture': 'a consulting project',
    'HCL': 'a cloud operations team', 'Zoho': 'a product engineering team',
    'Cognizant': 'a retail analytics team', 'Capgemini': 'a manufacturing client team',
}

_PROMPT_FRAMES = {
    'Quantitative Aptitude': ('A planning desk tracks', 'During a shift,', 'A delivery report shows', 'For capacity planning,', 'The operations lead records', 'A forecast estimates', 'A test case contains', 'The weekly dashboard lists', 'An analyst calculates', 'A coordinator confirms'),
    'Logical Reasoning': ('A sequence used by', 'The scheduling rule for', 'A queue monitored by', 'A puzzle from', 'The alert pattern in', 'A routing system for', 'A coding exercise presents', 'The audit trail for', 'A calendar rule used by', 'The next-step rule for'),
    'Data Interpretation': ('A Monday report for', 'A dashboard used by', 'The weekly register of', 'A survey collected by', 'A stock ledger for', 'The service desk at', 'A client summary from', 'A sample table for', 'An analyst reviews', 'The monthly report for'),
    'Probability': ('A quality check at', 'A random draw for', 'A sealed kit used by', 'A selection round in', 'A sample tray at', 'A test batch for', 'A lottery exercise from', 'A validation set in', 'A card draw for', 'A screening box at'),
    'Time and Work': ('A shift plan for', 'A work allocation at', 'A delivery schedule for', 'A report deadline at', 'A staffing exercise for', 'A production plan at', 'A support rota for', 'A project estimate from', 'A workload review for', 'A completion plan at'),
    'Number Systems': ('A checksum used by', 'A coding puzzle for', 'A divisibility check in', 'A numeric audit at', 'A remainder exercise for', 'A validation rule in', 'A data import check for', 'A number theory task from', 'A test of modular arithmetic for', 'A calculation used by'),
    'Permutations and Combinations': ('A review panel at', 'A pairing exercise for', 'A committee formed by', 'A networking session for', 'A mentoring program at', 'A tournament group from', 'A peer review plan for', 'A workshop roster at', 'A matching exercise for', 'A collaboration plan at'),
    'Profit, Loss and Percentage': ('A budget forecast for', 'A procurement sheet at', 'A price revision for', 'A finance review at', 'A service quotation from', 'A sales plan for', 'A cost estimate at', 'A client invoice for', 'A revised allowance in', 'A monthly budget at'),
}


def _seed(company, topic, index):
    return int(hashlib.sha256(f'{company}:{topic}:{index}'.encode()).hexdigest()[:12], 16)


def _make_question(company, topic, index):
    seed = _seed(company, topic, index)
    scenario = _SCENARIOS.get(company, f'{company} delivery team')
    a, b = 20 + seed % 41, 2 + seed % 8
    if topic == 'Quantitative Aptitude':
        correct, text = a * b, f'{scenario.title()} processes {a} requests per hour. At {b} hours, how many requests are processed?'
        options, formula = [str(correct - b), str(correct), str(correct + b), str(correct + a)], f'{a} x {b} = {correct}'
    elif topic == 'Logical Reasoning':
        correct, text = a + b * 4, f'A queue for {scenario} follows {a}, {a + b}, {a + b * 2}, {a + b * 3}. What comes next?'
        options, formula = [str(correct - b), str(correct), str(correct + b), str(correct + b * 2)], f'Add {b} each time: {a + b * 3} + {b} = {correct}'
    elif topic == 'Data Interpretation':
        correct, text = a + b * 10, f'{scenario.title()} records {a} tickets on Monday and {b * 10} on Tuesday. What is the two-day total?'
        options, formula = [str(correct - 10), str(correct), str(correct + 10), str(correct + b)], f'{a} + {b * 10} = {correct}'
    elif topic == 'Probability':
        total, favorable = a + b, b
        correct, text = f'{favorable}/{total}', f'A test kit for {scenario} contains {favorable} validated cards and {a} other cards. What is the chance of drawing a validated card?'
        options, formula = [f'{favorable}/{total + 1}', correct, f'{a}/{total}', f'1/{favorable}'], f'Favourable outcomes / total outcomes = {favorable} / {total}'
    elif topic == 'Time and Work':
        correct, text = a + b, f'One analyst completes a {scenario} report in {a} days and another in {b} days. What is the sum of their individual times?'
        options, formula = [str(correct - b), str(correct), str(correct + b), str(a * b)], f'{a} + {b} = {correct} days'
    elif topic == 'Number Systems':
        correct, text = str(b), f'What is the remainder when {a * 2 + b} is divided by {a}?'
        options, formula = [str(b), str(a), str(a - b), '0'], f'{a * 2 + b} = {a} x 2 + {b}, so the remainder is {b}'
    elif topic == 'Permutations and Combinations':
        correct, text = a * (a - 1) // 2, f'{a} members of {scenario} must form two-person review pairs. How many distinct pairs are possible?'
        options, formula = [str(correct - a), str(correct), str(correct + a), str(a * (a - 1))], f'n(n - 1) / 2 = {a} x {a - 1} / 2 = {correct}'
    else:
        revised = a * 100 + (a * 100 * b // 100)
        correct, text = f'Rs {revised}', f'A {scenario} budget of Rs {a * 100} increases by {b}%. What is the revised budget?'
        options, formula = [f'Rs {revised - 100}', correct, f'Rs {revised + 100}', f'Rs {a * 100 - b * 10}'], f'Rs {a * 100} + ({b}% x Rs {a * 100}) = {correct}'
    correct = str(correct)
    answer = options.index(correct)
    text = f'{_PROMPT_FRAMES[topic][index % 10]} {scenario}: {text}'
    return {'id': f'{company}:{topic}:{index}', 'topic': topic, 'question': text, 'options': options, 'answer': answer, 'correct_answer': correct, 'why_wrong': f'Only option {chr(65 + answer)} satisfies the stated values and operation.', 'logic': f'Apply the {topic.lower()} rule to the values given in this question.', 'formula': formula, 'steps': f'1. Read the supplied values. 2. Apply: {formula}. 3. Match the result to the options.', 'final_answer': correct}


def company_questions(company_name, topic=None, count=10, exclude=None):
    if topic not in COMPANY_TOPICS.get(company_name, ()):
        return []
    excluded = set(exclude or [])
    questions = [_make_question(company_name, topic, index) for index in range(10)]
    available = [question for question in questions if question['id'] not in excluded]
    return random.SystemRandom().sample(available, min(count, len(available)))


def company_bank(company_name):
    return [question for topic in COMPANY_TOPICS.get(company_name, ()) for question in company_questions(company_name, topic)]


def extra_questions(company_name, topic):
    if topic not in COMPANY_TOPICS.get(company_name, ()):
        return []
    return [_make_question(company_name, topic, index) for index in range(10, 15)]