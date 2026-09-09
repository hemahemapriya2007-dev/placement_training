"""Company-specific verbal ability question banks."""

import hashlib


def _seed(company, mode, index):
    return int(hashlib.sha256(f'{company}:{mode}:{index}'.encode()).hexdigest()[:8], 16)


def _question(company, mode, index):
    seed = _seed(company, mode, index)
    subject = ['The manager', 'The analysts', 'The candidate', 'The project team', 'The trainer'][index]
    verb = ['reviews', 'prepare', 'has completed', 'were discussing', 'submits'][index]
    if mode == 'verbal_mcq':
        bank = [
            (f'{subject} ___ the weekly report every Friday.', ['review', 'reviews', 'reviewing', 'reviewed'], 1, 'A singular subject takes the singular present verb.', 'Subject-verb agreement'),
            (f'Choose the correct sentence for {company}.', ['She have finished the task.', 'She has finished the task.', 'She having finished the task.', 'She finish the task.'], 1, 'The present perfect form is has + past participle.', 'Has and have'),
            ('Select the closest synonym of diligent.', ['Careless', 'Hardworking', 'Uncertain', 'Silent'], 1, 'Diligent means showing steady and careful effort.', 'Synonyms'),
            ('Choose the antonym of temporary.', ['Brief', 'Current', 'Permanent', 'Recent'], 2, 'Permanent describes something lasting indefinitely.', 'Antonyms'),
            (f'{company} expects the applicant ___ the instructions carefully.', ['read', 'to read', 'reading', 'reads'], 1, 'After expects the applicant, use the infinitive to read.', 'Infinitives'),
        ]
    else:
        bank = [
            (f'{subject} ___ the weekly report every Friday.', ['review', 'reviews', 'reviewing', 'reviewed'], 1, 'The singular subject takes reviews in the simple present.', 'Subject-verb agreement'),
            (f'The training session starts ___ 9 a.m. at {company}.', ['in', 'on', 'at', 'by'], 2, 'Use at with an exact clock time.', 'Prepositions of time'),
            ('She bought ___ umbrella before the interview.', ['a', 'an', 'the', 'no article'], 1, 'Use an before a vowel sound.', 'Articles'),
            (f'The applicants ___ preparing for the {company} assessment yesterday.', ['was', 'is', 'were', 'has'], 2, 'The plural subject applicants takes were in the past tense.', 'Was and were'),
            (f'If the candidate studies well, she ___ pass the {company} test.', ['will', 'would', 'was', 'has'], 0, 'Use will in the first conditional result clause.', 'Conditionals'),
        ]
    text, options, answer, explanation, concept = bank[index]
    mode_label = 'Verbal MCQ' if mode == 'verbal_mcq' else 'Fill in the Blanks'
    text = f'{company} {mode_label}: {text}'
    return {'id': f'{company}:{mode}:{index}', 'question': text, 'options': options, 'answer': answer, 'explanation': explanation, 'concept': concept}


def get_questions(company_name, mode):
    if mode not in {'verbal_mcq', 'fill_blanks'}:
        return []
    return [_question(company_name, mode, index) for index in range(5)]
