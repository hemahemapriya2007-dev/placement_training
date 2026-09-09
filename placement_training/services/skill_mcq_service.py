"""Additive MCQ banks for skill assessments."""

import random


LOGICAL_REASONING_QUESTIONS = [
    ('Find the next number: 4, 9, 16, 25, ?', ['30', '36', '40', '49'], 1, 'The terms are consecutive squares: 2^2, 3^2, 4^2, 5^2, so the next term is 6^2 = 36.'),
    ('If FLOWER is coded as GMPXFS, how is GARDEN coded?', ['HBSEFO', 'HBQDEN', 'FZQCDM', 'IBTFGP'], 0, 'Each letter is shifted one position forward: G to H, A to B, and so on.'),
    ('A person walks 5 km south, then turns left and walks 3 km. Which direction is the person facing?', ['North', 'East', 'West', 'South'], 1, 'Facing south, a left turn points east.'),
    ('All analysts are graduates. Some graduates are developers. Which conclusion is valid?', ['All analysts are developers', 'Some analysts may be developers', 'No analyst is a developer', 'All developers are analysts'], 1, 'The statements allow overlap between analysts and developers but do not require it.'),
    ('A is older than B, B is older than C, and D is older than A. Who is youngest?', ['A', 'B', 'C', 'D'], 2, 'The order from oldest to youngest is D, A, B, C.'),
    ('Choose the odd one out.', ['Keyboard', 'Mouse', 'Monitor', 'Compiler'], 3, 'A compiler is software; the others are common hardware devices.'),
    ('If today is Tuesday, which day will it be 100 days from today?', ['Wednesday', 'Thursday', 'Friday', 'Saturday'], 1, '100 modulo 7 is 2, so Tuesday plus two days is Thursday.'),
    ('Complete the pattern: AZ, CX, EV, ?', ['GT', 'FU', 'HS', 'IR'], 0, 'The first letters move forward by two and the second letters move backward by two: G and T.'),
    ('In a row, Priya is 11th from the left and 14th from the right. How many people are there?', ['24', '25', '26', '27'], 0, 'Total = left position + right position - 1 = 11 + 14 - 1 = 24.'),
    ('Which number replaces ?: 3, 7, 15, 31, ?', ['47', ' Fifty-five', '63', '65'], 2, 'Each term is multiplied by two and increased by one: 31 x 2 + 1 = 63.'),
    ('A code changes RED to 27 using letter positions. How is BLUE represented?', ['35', '40', '42', '45'], 1, 'B + L + U + E = 2 + 12 + 21 + 5 = 40.'),
    ('If P > Q, Q = R, and R > S, which relation must be true?', ['P < S', 'P > S', 'S > P', 'P = S'], 1, 'P is greater than Q, Q equals R, and R is greater than S, therefore P > S.'),
    ('A meeting starts at 9:35 and lasts 2 hours 45 minutes. When does it end?', ['11:50', '12:10', '12:20', '12:30'], 2, 'Adding two hours gives 11:35; adding 45 minutes gives 12:20.'),
    ('Find the missing pair: AB, DE, GH, JK, ?', ['LM', 'MN', 'NO', 'OP'], 1, 'Each pair advances three letters: AB, DE, GH, JK, MN.'),
    ('A team has five members. Each member greets every other member once. How many greetings occur?', ['5', '10', '15', '20'], 1, 'The number of pairs is 5 x 4 / 2 = 10.'),
    ('If 8 machines produce 800 units in an hour, how many units do 12 machines produce at the same rate?', ['1,000', '1,100', '1,200', '1,400'], 2, 'Each machine produces 100 units per hour, so 12 machines produce 1,200.'),
    ('Which word cannot be formed from PLACEMENT?', ['LATE', 'TEAM', 'PLACE', 'CAMP'], 3, 'PLACEMENT contains no second C, so CAMP cannot be formed.'),
    ('A cube has all faces painted and is cut into 27 equal cubes. How many small cubes have paint on three faces?', ['4', '6', '8', '12'], 2, 'Only the eight corner cubes have paint on three faces.'),
    ('A clock shows 3:00. What is the angle between the hands?', ['0 degrees', '45 degrees', '90 degrees', '180 degrees'], 2, 'At exactly 3:00, the hands are perpendicular, making 90 degrees.'),
    ('In a class, Ravi ranks 7th from the top and 18th from the bottom. How many students are there?', ['24', '25', '26', '27'], 0, 'Total = 7 + 18 - 1 = 24.'),
]

COMMUNICATION_QUESTIONS = [
    ('Which opening is most appropriate for a formal email to a recruiter?', ['Hey buddy', 'Dear Hiring Manager', 'Yo recruiter', 'Hi dude'], 1, 'Dear Hiring Manager is professional and appropriate when the recipient name is unknown.'),
    ('What is the best response when a teammate disagrees with your proposal?', ['Interrupt them', 'Ignore the concern', 'Ask questions and discuss evidence', 'End the meeting'], 2, 'Active listening and evidence-based discussion keep disagreement constructive.'),
    ('Which sentence is grammatically correct?', ['She have completed the task.', 'She has completed the task.', 'She completing the task.', 'She complete the task yesterday.'], 1, 'The singular subject she takes has with the past participle completed.'),
    ('In an interview, what should an answer to “Tell me about yourself” emphasize?', ['Personal gossip', 'A concise professional summary', 'Unrelated hobbies only', 'Criticism of former employers'], 1, 'A concise summary connects background, skills, and relevant goals to the role.'),
    ('What is the clearest way to report a project delay?', ['Hide it until the deadline', 'Blame another team', 'State the impact, cause, and recovery plan', 'Send only “It is delayed”'], 2, 'A useful status update explains what happened and what action will address it.'),
    ('Which phrase shows that you are checking understanding?', ['That is wrong.', 'Do whatever.', 'Could you clarify what you mean?', 'I was not listening.'], 2, 'A clarification question prevents assumptions and supports accurate communication.'),
    ('Choose the most professional disagreement.', ['You are clueless.', 'I see it differently because the data suggests...', 'That idea is stupid.', 'I refuse to discuss this.'], 1, 'The phrase acknowledges a different view and supports it with evidence.'),
    ('Which is the best closing for a formal request email?', ['Reply now!!!', 'Whatever works', 'Thank you for your consideration.', 'Bye'], 2, 'Thank you for your consideration is courteous and professional.'),
    ('When presenting technical information to a non-technical client, you should:', ['Use unexplained jargon', 'Focus on outcomes and simple language', 'Speak as quickly as possible', 'Avoid confirming questions'], 1, 'Simple language and outcome-focused explanations make information accessible.'),
    ('What should you do after receiving constructive feedback?', ['Defend every decision', 'Listen, clarify, and identify an action', 'Ignore it', 'End the conversation'], 1, 'Listening and turning feedback into an action demonstrates professionalism and growth.'),
    ('Which sentence uses a confident but respectful tone?', ['I can complete this by Friday and will flag risks early.', 'This is impossible, obviously.', 'Nobody can do this.', 'I guess maybe I can try.'], 0, 'The sentence is specific about commitment while responsibly acknowledging risk.'),
    ('In a group discussion, the most effective participation is to:', ['Speak over everyone', 'Contribute relevant points and invite others', 'Remain silent throughout', 'Repeat one point'], 1, 'Strong participants add value while making space for other perspectives.'),
    ('If you do not know an interview answer, you should:', ['Invent facts', 'Pause, explain your approach, and be honest', 'Change the subject', 'Criticize the question'], 1, 'Honesty paired with a reasoned approach communicates integrity and problem-solving ability.'),
    ('Which is an example of active listening?', ['Planning your reply while they speak', 'Paraphrasing the key point before responding', 'Checking your phone', 'Interrupting immediately'], 1, 'Paraphrasing confirms that you understood the speaker correctly.'),
    ('A concise workplace update should normally include:', ['Only emotions', 'Status, blocker, and next step', 'Every historical detail', 'Unverified rumors'], 1, 'Status, blocker, and next step give the team actionable information.'),
]


def assessment_questions(skill_name, student_id, company_id, session):
    """Select an unattempted randomized set while retaining history in Flask session."""
    bank = LOGICAL_REASONING_QUESTIONS if skill_name == 'Logical Reasoning' else COMMUNICATION_QUESTIONS
    limit = 10 if skill_name == 'Logical Reasoning' else 5
    history_key = f'{student_id}:{company_id}:{skill_name}'
    histories = dict(session.get('mcq_assessment_history', {}))
    history = set(histories.get(history_key, []))
    available = [index for index in range(len(bank)) if index not in history]
    if len(available) < limit:
        history.clear()
        available = list(range(len(bank)))
    selected = random.SystemRandom().sample(available, limit)
    history.update(selected)
    histories[history_key] = list(history)
    session['mcq_assessment_history'] = histories
    if hasattr(session, 'modified'):
        session.modified = True
    result = []
    for index in selected:
        text, options, answer, explanation = bank[index]
        shuffled = list(enumerate(options))
        random.SystemRandom().shuffle(shuffled)
        result.append({
            'id': f'{skill_name}:{index}',
            'question': text,
            'options': [option for _, option in shuffled],
            'answer': next(position for position, (original, _) in enumerate(shuffled) if original == answer),
            'explanation': explanation,
        })
    return result
