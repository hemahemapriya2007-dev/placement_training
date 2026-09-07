from datetime import datetime
import random
import subprocess
import sys
import tempfile
import time

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user

from placement_training import db
from placement_training.models import Company, Skill, StudentSkill, StudentCompany, StudentCompanySkill, LearningPlan, Task, StudentTask, Test, TestResult, Progress, Resume, Certificate, MockInterview, CompanySkill, GroupDiscussionResult
from placement_training.services.progress_service import calculate_student_progress, get_leaderboard
from placement_training.services.recommendation_service import recommend_skills
from placement_training.services.aptitude_practice_service import COMPANY_TOPICS, company_bank, extra_questions
from sqlalchemy.orm import joinedload
import re

student_bp = Blueprint('student', __name__)


APTITUDE_QUESTION_BANK = [
    {'question': 'A train travels 360 km in 4 hours. How far will it travel in 45 minutes at the same speed?', 'options': ['60 km', '67.5 km', '72 km', '80 km'], 'answer': 1},
    {'question': 'The ratio of boys to girls in a group is 3:5. If the group has forty students, how many are girls?', 'options': ['15', '20', '25', '30'], 'answer': 2},
    {'question': 'A product marked at Rs 1,500 is sold after a 20% discount. What is its selling price?', 'options': ['Rs 1,100', 'Rs 1,200', 'Rs 1,250', 'Rs 1,300'], 'answer': 1},
    {'question': 'If 5 workers finish a task in 12 days, how many days will 8 workers take at the same rate?', 'options': ['6.5 days', '7 days', '7.5 days', '8 days'], 'answer': 2},
    {'question': 'Find the next number in the series: 3, 8, 15, 24, 35, ?', 'options': ['46', '48', '49', '50'], 'answer': 1},
    {'question': 'A person walks 6 km north, then 8 km east. What is the shortest distance from the starting point?', 'options': ['10 km', '12 km', '14 km', '16 km'], 'answer': 0},
    {'question': 'If CODE is written as DPEF by shifting each letter one place, how is DATA written?', 'options': ['EBUB', 'EBUA', 'DBSZ', 'FCVC'], 'answer': 0},
    {'question': 'A can complete a job in 10 days and B in 15 days. How long do they take together?', 'options': ['5 days', '6 days', '7.5 days', '8 days'], 'answer': 1},
    {'question': 'The average of five numbers is 24. If one number is removed, the average becomes 22. What was removed?', 'options': ['28', '30', '32', '34'], 'answer': 2},
    {'question': 'A clock gains 5 minutes every hour. If it is set correctly at noon, what will it show at 6 PM?', 'options': ['6:05 PM', '6:20 PM', '6:25 PM', '6:30 PM'], 'answer': 3},
    {'question': 'In a row, Maya is 12th from the left and 9th from the right. How many people are in the row?', 'options': ['19', '20', '21', '22'], 'answer': 1},
    {'question': 'What is the probability of drawing a red card from a standard deck of 52 cards?', 'options': ['1/4', '1/3', '1/2', '2/3'], 'answer': 2},
    {'question': 'If x + 1/x = 5, what is x squared + 1/x squared?', 'options': ['21', '23', '25', '27'], 'answer': 1},
    {'question': 'Find the odd one out: 16, 25, 36, 48, 64.', 'options': ['16', '25', '48', '64'], 'answer': 2},
]
SKILL_QUESTION_BANKS = {
    'Logical Reasoning': [
        ('Find the next number: 2, 6, 12, 20, ?', ['28', '30', '32', '36'], 1),
        ('If CAT is coded as DBU, how is DOG coded?', ['EPH', 'EOH', 'DPH', 'FPH'], 0),
        ('A is B\'s sister. C is B\'s mother. How is A related to C?', ['Sister', 'Daughter', 'Mother', 'Aunt'], 1),
        ('All roses are flowers. Some flowers fade quickly. Which statement follows?', ['All roses fade', 'Some roses may fade', 'No rose fades', 'All flowers are roses'], 1),
        ('A man walks east, turns right, then right again. Which direction is he facing?', ['North', 'South', 'East', 'West'], 3),
        ('Find the odd pair.', ['Book : Read', 'Food : Eat', 'Pen : Write', 'Chair : Run'], 3),
        ('If today is Wednesday, what day will it be 45 days later?', ['Friday', 'Saturday', 'Sunday', 'Monday'], 1),
        ('Complete the pattern: AZ, BY, CX, ?', ['DW', 'DX', 'EV', 'EW'], 0),
        ('In a queue, Ravi is 8th from the front and 13th from the end. How many people are there?', ['19', '20', '21', '22'], 1),
        ('Which number replaces ?: 4, 9, 19, 39, ?', ['69', '79', '89', '99'], 1),
    ],
    'Verbal Ability': [
        ('Choose the synonym of concise.', ['Brief', 'Rigid', 'Loud', 'Exact'], 0),
        ('Choose the antonym of scarce.', ['Rare', 'Limited', 'Abundant', 'Small'], 2),
        ('Select the correct sentence.', ['She do her work.', 'She does her work.', 'She doing her work.', 'She done her work.'], 1),
        ('Identify the error: He is senior than me.', ['He', 'is', 'senior than', 'No error'], 2),
        ('Complete: Neither the manager nor the employees ___ available.', ['was', 'is', 'were', 'be'], 2),
        ('Choose the correctly spelt word.', ['Accomodate', 'Acommodate', 'Accommodate', 'Acomodate'], 2),
        ('A persuasive proposal should primarily be ___.', ['unclear', 'evidence-based', 'repetitive', 'informal'], 1),
        ('Choose the meaning of pragmatic.', ['Idealistic', 'Practical', 'Emotional', 'Doubtful'], 1),
        ('Complete: If I had known, I ___ earlier.', ['will arrive', 'would arrive', 'would have arrived', 'arrived'], 2),
        ('Which is most appropriate in a formal email?', ['Hey there', 'Dear Hiring Manager', 'Yo team', 'Hi buddy'], 1),
    ],
    'Programming': [
        ('What is the time complexity of binary search on a sorted array?', ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], 1),
        ('Which structure follows LIFO?', ['Queue', 'Stack', 'Heap', 'Graph'], 1),
        ('In Python, which type is immutable?', ['List', 'Set', 'Dictionary', 'Tuple'], 3),
        ('Which C++ feature enables one interface with different implementations?', ['Encapsulation', 'Polymorphism', 'Compilation', 'Tokenization'], 1),
        ('What does JVM execute?', ['HTML', 'Bytecode', 'SQL', 'Machine drawings'], 1),
        ('Which algorithm is stable and divide-and-conquer?', ['Merge sort', 'Selection sort', 'Linear search', 'Hashing'], 0),
        ('What is a collision in hashing?', ['Duplicate key', 'Same hash for different keys', 'Empty bucket', 'Sorted bucket'], 1),
        ('Which traversal visits root between left and right subtrees?', ['Preorder', 'Inorder', 'Postorder', 'Level order'], 1),
        ('Which principle hides implementation details?', ['Inheritance', 'Abstraction', 'Recursion', 'Iteration'], 1),
        ('What does SQL JOIN primarily do?', ['Deletes rows', 'Combines related rows', 'Creates indexes', 'Renames tables'], 1),
    ],
    'SQL': [
        ('Which clause filters grouped results?', ['WHERE', 'HAVING', 'ORDER BY', 'GROUP BY'], 1),
        ('Which JOIN returns matching rows from both tables?', ['INNER JOIN', 'LEFT JOIN', 'CROSS JOIN', 'FULL JOIN'], 0),
        ('Which function counts rows?', ['SUM()', 'TOTAL()', 'COUNT()', 'ROWS()'], 2),
        ('A primary key must be ___.', ['duplicated', 'nullable', 'unique and non-null', 'text only'], 2),
        ('Which normal form removes repeating groups?', ['1NF', '2NF', '3NF', 'BCNF'], 0),
        ('Which command changes existing rows?', ['ALTER', 'UPDATE', 'CREATE', 'GRANT'], 1),
        ('A query inside another query is called a ___.', ['view', 'subquery', 'trigger', 'cursor'], 1),
        ('Which index is commonly used for range searches?', ['B-tree', 'Bitmap only', 'Text file', 'Queue'], 0),
        ('What does COMMIT do?', ['Undo changes', 'Save transaction changes', 'Drop a table', 'Lock a column'], 1),
        ('Which constraint prevents duplicate values?', ['CHECK', 'DEFAULT', 'UNIQUE', 'FOREIGN KEY'], 2),
    ],
}
TEXT_SKILL_PROMPTS = {
    'Communication': ['Tell me about yourself.', 'Why should we hire you?', 'What are your strengths?', 'Describe a challenging situation.', 'Explain your final year project.', 'Where do you see yourself in five years?', 'How do you handle feedback?'],
    'Interview Skills': ['Introduce yourself professionally.', 'Why do you want to join our company?', 'What are your career goals?', 'Describe your strengths and weaknesses.', 'Explain a difficult situation you handled.', 'Why should we hire you?', 'What achievement are you proud of?'],
}
COMMUNICATION_COMPANY_PROMPTS = {
    'Infosys': ['Your manager rejects a well-researched automation idea. How would you respond?', 'A teammate takes credit for your contribution in a client meeting. What would you do?', 'You discover a mistake in a report just before a review. How do you handle it?', 'You are asked to learn a new tool in two days for a delivery. What is your plan?', 'Two colleagues disagree and both ask you to take sides. How would you help?'],
    'TCS': ['An important task may miss its deadline because of a dependency. What would you communicate?', 'A senior disagrees with your technical suggestion. How would you present your view?', 'You receive negative feedback despite strong effort. How do you respond?', 'Your team is remote and a message is misunderstood. How would you repair the situation?', 'You have two competing priorities from different stakeholders. What would you do?'],
    'Wipro': ['A customer changes requirements halfway through delivery. How would you adapt?', 'You are stuck on a problem while the team depends on you. What is your next step?', 'A colleague makes an error that affects your work. How would you address it?', 'You must explain a complex issue to a non-technical client. How would you proceed?', 'You disagree with a process but must meet the deadline. What would you do?'],
    'Cognizant': ['You are given an unfamiliar task with a short deadline. How would you approach it?', 'A meeting becomes tense after your proposal is challenged. How would you stay constructive?', 'You notice a privacy risk in a proposed shortcut. What action would you take?', 'Your manager is unavailable during an urgent decision. How would you proceed?', 'A teammate is struggling and the deadline is near. How would you support them?'],
    'Capgemini': ['A client rejects your first solution without explaining why. How would you clarify and improve it?', 'You make a mistake nobody notices before release. Would you report it? Why?', 'A project has unclear ownership for an urgent task. What would you do?', 'You must balance quality with a very short delivery window. How would you decide?', 'A teammate prefers a risky approach you do not support. How would you communicate?'],
    'Accenture': ['A stakeholder asks for a result that conflicts with a project constraint. How would you respond?', 'You are asked to lead a discussion outside your comfort zone. How would you prepare?', 'Your first analysis contradicts the team assumption. How would you raise it?', 'A deadline moves forward and the scope stays the same. What would you negotiate?', 'A teammate is silent during a key decision. How would you bring them into the discussion?'],
}
PROGRAMMING_POOLS = {
    'Infosys': [('Normalize a name', 'Read one line and print it with words reversed.', 'Input: placement training\nOutput: training placement', 'easy', 'print(" ".join(input().split()[::-1]))', 'Use split to create words, then reverse the list.'), ('Count vowels', 'Read one line and print the number of vowels.', 'Input: Developer\nOutput: 4', 'easy', 'text=input().lower(); print(sum(ch in "aeiou" for ch in text))', 'Check each character against the vowel set.'), ('Unique characters', 'Read a word and print the first character that appears only once, or -1.', 'Input: swiss\nOutput: w', 'medium', 's=input(); print(next((ch for ch in s if s.count(ch)==1), -1))', 'Count occurrences before choosing a character.'), ('Running total', 'Read space-separated integers and print the largest running total.', 'Input: 2 -1 5\nOutput: 6', 'medium', 'total=best=0\nfor value in map(int,input().split()):\n total+=value; best=max(best,total)\nprint(best)', 'Update the total before comparing it with the best value.'), ('Common prefix', 'Read two words and print their longest common prefix.', 'Input: flower flow\nOutput: flow', 'medium', 'a,b=input().split(); i=0\nwhile i<min(len(a),len(b)) and a[i]==b[i]: i+=1\nprint(a[:i])', 'Compare matching positions until the first mismatch.')],
    'TCS': [('Rotate list', 'Read integers and a rotation k. Print the list rotated left by k.', 'Input: 1 2 3 4; 1\nOutput: 2 3 4 1', 'medium', 'values=list(map(int,input().split())); k=int(input()); k%=len(values); print(*(values[k:]+values[:k]))', 'Reduce k with modulo before slicing.'), ('Digit product', 'Read a positive integer and print the product of its non-zero digits.', 'Input: 1052\nOutput: 10', 'easy', 'n=input(); product=1\nfor digit in n:\n if digit!="0": product*=int(digit)\nprint(product)', 'Skip zero digits but keep the product initialized.'), ('Balanced brackets', 'Read a bracket string and print YES if it is balanced, otherwise NO.', 'Input: ([{}])\nOutput: YES', 'medium', 's=input(); stack=[]; pairs={")":"(","]":"[","}":"{"}\nfor ch in s:\n if ch in "([{": stack.append(ch)\n elif not stack or stack.pop()!=pairs[ch]: print("NO"); break\nelse: print("YES" if not stack else "NO")', 'Use a stack and reject a closing bracket with the wrong opener.'), ('Second largest', 'Read distinct integers and print the second largest without sorting.', 'Input: 4 9 2 7\nOutput: 7', 'medium', 'values=list(map(int,input().split())); first=second=float("-inf")\nfor value in values:\n if value>first: second,first=first,value\n elif value>second: second=value\nprint(second)', 'Maintain first and second values as you scan.'), ('Word frequency', 'Read a sentence and print the most frequent word; ties use first appearance.', 'Input: red blue red\nOutput: red', 'medium', 'words=input().split(); print(max(words,key=lambda word: words.count(word)))', 'Count each word and preserve the original order for ties.')],
    'Wipro': [('Compress runs', 'Read a string and print each character followed by its consecutive count.', 'Input: aaabbc\nOutput: a3b2c1', 'medium', 's=input(); out=""; i=0\nwhile i<len(s):\n j=i\n while j<len(s) and s[j]==s[i]: j+=1\n out+=s[i]+str(j-i); i=j\nprint(out)', 'Advance the second pointer across one run at a time.'), ('Perfect square sum', 'Read n and print the sum of squares from 1 through n.', 'Input: 3\nOutput: 14', 'easy', 'n=int(input()); print(sum(i*i for i in range(1,n+1)))', 'Include both endpoints in the range.'), ('Missing value', 'Read n-1 values from 1..n and print the missing value.', 'Input: 5\n1 2 3 5\nOutput: 4', 'medium', 'n=int(input()); values=list(map(int,input().split())); print(n*(n+1)//2-sum(values))', 'Compare the expected arithmetic sum with the observed sum.'), ('Alternate case', 'Read a word and print letters at even positions uppercase and odd positions lowercase.', 'Input: coding\nOutput: CoDiNg', 'easy', 's=input(); print("".join(ch.upper() if i%2==0 else ch.lower() for i,ch in enumerate(s)))', 'Use the index parity, not the character value.'), ('Longest token', 'Read a sentence and print its longest word; ties use the first word.', 'Input: learn Python daily\nOutput: Python', 'easy', 'words=input().split(); print(max(words,key=len))', 'Compare words by length while keeping their order.')],
    'Cognizant': [('Two sum indexes', 'Read integers and a target; print indexes of the first pair adding to target.', 'Input: 2 7 11 15\n9\nOutput: 0 1', 'medium', 'values=list(map(int,input().split())); target=int(input()); seen={}\nfor i,value in enumerate(values):\n if target-value in seen: print(seen[target-value],i); break\n seen[value]=i', 'Store earlier values and look for the complement.'), ('Leap year', 'Read a year and print YES if it is a leap year, otherwise NO.', 'Input: 2024\nOutput: YES', 'easy', 'year=int(input()); print("YES" if year%400==0 or year%4==0 and year%100!=0 else "NO")', 'Check the century exception as well as divisibility by four.'), ('Matrix diagonal', 'Read n rows of n integers and print the absolute diagonal difference.', 'Input: 2\n1 2\n3 4\nOutput: 0', 'medium', 'n=int(input()); rows=[list(map(int,input().split())) for _ in range(n)]; print(abs(sum(rows[i][i] for i in range(n))-sum(rows[i][n-1-i] for i in range(n))))', 'Use opposite column indexes for the second diagonal.'), ('Anagram test', 'Read two words and print YES if they contain the same letters.', 'Input: listen silent\nOutput: YES', 'easy', 'a,b=input().split(); print("YES" if sorted(a)==sorted(b) else "NO")', 'Compare normalized character collections.'), ('Climb steps', 'Count ways to climb n steps using one or two steps at a time.', 'Input: 4\nOutput: 5', 'medium', 'n=int(input()); a,b=1,1\nfor _ in range(n): a,b=b,a+b\nprint(a)', 'Build each answer from the previous two answers.')],
    'Capgemini': [('Filter duplicates', 'Read integers and print them once each in first-seen order.', 'Input: 3 1 3 2 1\nOutput: 3 1 2', 'easy', 'values=list(map(int,input().split())); seen=set(); out=[]\nfor value in values:\n if value not in seen: out.append(value); seen.add(value)\nprint(*out)', 'Use a set for membership and a list for order.'), ('GCD pairs', 'Read two positive integers and print their greatest common divisor.', 'Input: 48 18\nOutput: 6', 'easy', 'a,b=map(int,input().split())\nwhile b: a,b=b,a%b\nprint(a)', 'Replace the pair with the remainder until it is zero.'), ('Peak element', 'Read integers and print the first element greater than both neighbors, or -1.', 'Input: 1 3 2 4\nOutput: 3', 'medium', 'a=list(map(int,input().split())); print(next((a[i] for i in range(1,len(a)-1) if a[i]>a[i-1] and a[i]>a[i+1]),-1))', 'Only interior elements can be peaks.'), ('Binary count', 'Read a positive integer and print the number of one bits in binary.', 'Input: 13\nOutput: 3', 'easy', 'n=int(input()); count=0\nwhile n: count+=n&1; n>>=1\nprint(count)', 'Inspect the lowest bit before shifting.'), ('Merge intervals', 'Read intervals as start end pairs and print the number of merged intervals.', 'Input: 1 3 2 4 6 8\nOutput: 2', 'medium', 'v=list(map(int,input().split())); pairs=sorted(zip(v[::2],v[1::2])); total=0; end=-1\nfor start,stop in pairs:\n if start>end: total+=1\n end=max(end,stop)\nprint(total)', 'Sort by start and extend the current end.')],
    'Accenture': [('Fibonacci filter', 'Read n and print Fibonacci numbers up to n that are even.', 'Input: 10\nOutput: 0 2 8', 'easy', 'n=int(input()); a,b=0,1; out=[]\nwhile a<=n:\n if a%2==0: out.append(a)\n a,b=b,a+b\nprint(*out)', 'Advance both Fibonacci variables every iteration.'), ('Run length', 'Read a string and print the length of its longest consecutive run.', 'Input: abbccc\nOutput: 3', 'medium', 's=input(); best=current=1\nfor i in range(1,len(s)):\n current=current+1 if s[i]==s[i-1] else 1; best=max(best,current)\nprint(best)', 'Reset the current run when adjacent characters differ.'), ('Nearest value', 'Read integers and target; print the value with smallest absolute difference.', 'Input: 8 2 5\n6\nOutput: 5', 'easy', 'values=list(map(int,input().split())); target=int(input()); print(min(values,key=lambda value: abs(value-target)))', 'Compare absolute distance to the target.'), ('Triangle validity', 'Read three sides and print YES if they form a triangle.', 'Input: 3 4 5\nOutput: YES', 'easy', 'a,b,c=map(int,input().split()); print("YES" if a+b>c and a+c>b and b+c>a else "NO")', 'Every pair sum must exceed the remaining side.'), ('Subarray maximum', 'Read integers and print the maximum contiguous subarray sum.', 'Input: -2 3 -1 4 -5\nOutput: 6', 'medium', 'values=list(map(int,input().split())); current=best=values[0]\nfor value in values[1:]: current=max(value,current+value); best=max(best,current)\nprint(best)', 'At each value choose a new segment or extend the current one.')],
}
TECHNICAL_QUESTION_BANK = {
    'Programming': ['What is OOP?', 'What is the difference between C and C++?', 'What is inheritance?', 'What is polymorphism?', 'What is encapsulation?', 'What is a virtual function?'],
    'Data Structures': ['What is a stack?', 'What is the difference between a stack and a queue?', 'What is a linked list?', 'What is a binary tree?', 'What is a hash table?', 'When would you use a heap?'],
    'DBMS': ['What is normalization?', 'What is a primary key?', 'What is the difference between DELETE and TRUNCATE?', 'What is indexing?', 'What is a transaction?', 'What is a foreign key?'],
    'SQL': ['What are the types of joins?', 'What is the difference between WHERE and HAVING?', 'What is GROUP BY?', 'What is a subquery?', 'What is a view?', 'What is a composite key?'],
    'Operating Systems': ['What is a process?', 'What is a thread?', 'What is the difference between a process and a thread?', 'What is deadlock?', 'What is virtual memory?', 'What is context switching?'],
    'Computer Networks': ['What is DNS?', 'What is an IP address?', 'What is the difference between TCP and UDP?', 'What is HTTP and HTTPS?', 'What is a subnet?', 'What is the purpose of a firewall?'],
}
COMPANY_QUESTION_POOLS = {}


def _get_company_pool(company_name):
    """Build a stable, separate pool for each company without database changes."""
    if company_name not in COMPANY_QUESTION_POOLS:
        pool = []
        for index, item in enumerate(APTITUDE_QUESTION_BANK):
            question = dict(item)
            question['id'] = index
            question['question'] = f"{company_name} pattern | {question['question']}"
            pool.append(question)
        # Different company banks have distinct scenarios and a stable ordering.
        company_seed = sum(ord(character) for character in company_name)
        variant_bank = [
            ('A placement test has {a} questions and a candidate solves {b}. What percentage is solved?', ['40%', '50%', '60%', '75%'], 2),
            ('A recruiter schedules {a} interviews over {b} hours. What is the average time per interview?', ['15 minutes', '20 minutes', '25 minutes', '30 minutes'], 1),
            ('A team reduces processing time from {a} minutes to {b} minutes. What is the reduction?', ['20%', '25%', '30%', '35%'], 1),
            ('A data set has {a} values with an average of {b}. What is the total of all values?', ['{c}', '{d}', '{e}', '{f}'], 2),
            ('A candidate scores {a}, {b}, and {c} in three rounds. What score is needed in round four for an average of {d}?', ['{e}', '{f}', '{g}', '{h}'], 0),
            ('A project has {a} tasks. If {b}% are complete, how many tasks remain?', ['{c}', '{d}', '{e}', '{f}'], 1),
            ('A salary of Rs {a} receives a {b}% increment. What is the new salary?', ['Rs {c}', 'Rs {d}', 'Rs {e}', 'Rs {f}'], 2),
            ('A coding team has {a} members. If each pair reviews one another, how many review relationships exist?', ['{c}', '{d}', '{e}', '{f}'], 0),
            ('A bus covers {a} km in {b} hours. How many kilometres does it cover in {c} minutes?', ['{d}', '{e}', '{f}', '{g}'], 3),
            ('A box contains {a} blue and {b} green tokens. What is the probability of choosing blue?', ['{c}', '{d}', '{e}', '{f}'], 1),
            ('A number is divided by {a} and then increased by {b}. The result is {c}. What was the number?', ['{d}', '{e}', '{f}', '{g}'], 2),
            ('Five consecutive integers have a sum of {a}. What is the middle integer?', ['{b}', '{c}', '{d}', '{e}'], 1),
            ('A placement batch grows from {a} to {b} students. What is the percentage increase?', ['{c}%', '{d}%', '{e}%', '{f}%'], 0),
            ('A machine makes {a} units in {b} minutes. How many units in {c} minutes?', ['{d}', '{e}', '{f}', '{g}'], 2),
            ('A candidate travels {a} km at {b} km/h and returns at {c} km/h. What is the total travel time?', ['{d} hours', '{e} hours', '{f} hours', '{g} hours'], 3),
        ]
        for variant_index, (text, options, answer) in enumerate(variant_bank, start=len(pool)):
            values = [
                40 + (company_seed + variant_index * 7) % 61,
                2 + (company_seed + variant_index) % 5,
                12 + (company_seed + variant_index * 3) % 30,
                24 + (company_seed + variant_index * 5) % 50,
                36 + (company_seed + variant_index * 7) % 70,
                48 + (company_seed + variant_index * 9) % 90,
                60 + (company_seed + variant_index * 11) % 100,
                72 + (company_seed + variant_index * 13) % 110,
            ]
            question = {'id': variant_index, 'question': f'{company_name} pattern | {text.format(a=values[0], b=values[1], c=values[2], d=values[3], e=values[4], f=values[5], g=values[6], h=values[7])}', 'options': [option.format(a=values[0], b=values[1], c=values[2], d=values[3], e=values[4], f=values[5], g=values[6], h=values[7]) for option in options], 'answer': answer}
            pool.append(question)
        # Keep the legacy pool intact and add the company/topic bank beside it.
        for question in company_bank(company_name):
            question['id'] = f"company-bank:{question['id']}"
            pool.append(question)
        for question in pool:
            correct_answer = question['options'][question['answer']]
            question.setdefault('correct_answer', correct_answer)
            question.setdefault('why_wrong', f"The selected option does not equal the result required by the values in this question; the correct result is {correct_answer}.")
            question.setdefault('logic', f"Use the operation described in the question with its supplied values, then compare the result with the four options.")
            question.setdefault('formula', f"Result = option {question['answer'] + 1}: {correct_answer}")
            question.setdefault('steps', f"1. Read the values and condition in the question. 2. Apply the stated operation. 3. The calculation gives {correct_answer}.")
            question.setdefault('final_answer', correct_answer)
        COMPANY_QUESTION_POOLS[company_name] = pool
    return COMPANY_QUESTION_POOLS[company_name]


def _company_questions(company_id, company_name, limit=10):
    pool = _get_company_pool(company_name)
    history_key = f'{current_user.id}:{company_id}'
    history = set(session.get('aptitude_history', {}).get(history_key, []))
    available = [item for item in pool if item['id'] not in history]
    if len(available) < limit:
        history = set()
        available = list(pool)
    selected = random.SystemRandom().sample(available, limit)
    history.update(item['id'] for item in selected)
    aptitude_history = dict(session.get('aptitude_history', {}))
    aptitude_history[history_key] = list(history)
    session['aptitude_history'] = aptitude_history
    session.modified = True

    questions = []
    for item in selected:
        question = dict(item)
        options = list(question['options'])
        correct_option = options[question['answer']]
        random.SystemRandom().shuffle(options)
        question['options'] = options
        question['answer'] = options.index(correct_option)
        questions.append(question)
    return questions


def _skill_questions(company_id, company_name, skill_name, limit=10):
    bank = SKILL_QUESTION_BANKS.get(skill_name, [])
    if not bank:
        return []
    pool = [{'id': index, 'question': f'{company_name} pattern | {text}', 'options': options, 'answer': answer} for index, (text, options, answer) in enumerate(bank)]
    history_key = f'{current_user.id}:{company_id}:{skill_name}'
    history = set(session.get('skill_assessment_history', {}).get(history_key, []))
    available = [item for item in pool if item['id'] not in history]
    if len(available) < limit:
        history = set()
        available = pool
    selected = random.SystemRandom().sample(available, min(limit, len(available)))
    history.update(item['id'] for item in selected)
    histories = dict(session.get('skill_assessment_history', {}))
    histories[history_key] = list(history)
    session['skill_assessment_history'] = histories
    session.modified = True
    result = []
    for item in selected:
        question = dict(item)
        options = list(question['options'])
        correct_option = options[question['answer']]
        random.SystemRandom().shuffle(options)
        question['options'] = options
        question['answer'] = options.index(correct_option)
        result.append(question)
    return result


def _technical_questions(company_id, company_name):
    history_key = f'{current_user.id}:{company_id}:Technical Interview'
    history = set(session.get('technical_interview_history', {}).get(history_key, []))
    questions = []
    for category, bank in TECHNICAL_QUESTION_BANK.items():
        for index, text in enumerate(bank):
            questions.append({'id': f'{category}:{index}', 'category': category, 'question': f'{company_name} interview pattern | {text}'})
    available = [item for item in questions if item['id'] not in history]
    if len(available) < 10:
        history = set()
        available = questions
    selected = random.SystemRandom().sample(available, min(18, len(available)))
    history.update(item['id'] for item in selected)
    histories = dict(session.get('technical_interview_history', {}))
    histories[history_key] = list(history)
    session['technical_interview_history'] = histories
    session.modified = True
    grouped = {}
    for item in selected:
        grouped.setdefault(item['category'], []).append(item['question'])
    return grouped


def _programming_questions(company_id, company_name):
    bank = PROGRAMMING_POOLS.get(company_name, PROGRAMMING_POOLS['Infosys'])
    history_key = f'{current_user.id}:{company_id}:Programming'
    history = set(session.get('programming_history', {}).get(history_key, []))
    available = [item for index, item in enumerate(bank) if index not in history]
    if len(available) < 3:
        history = set()
        available = list(bank)
    selected = random.SystemRandom().sample(available, 3)
    histories = dict(session.get('programming_history', {}))
    histories[history_key] = list(history | {bank.index(item) for item in selected})
    session['programming_history'] = histories
    session['programming_attempt'] = {
        str(index): {'attempts': 0, 'hints': 0, 'errors': []}
        for index in range(3)
    }
    session.modified = True
    difficulties = ['Easy', 'Medium', 'Hard']
    return [{'id': index, 'title': item[0], 'problem': item[1], 'expected': item[2], 'difficulty': difficulties[index], 'hint': item[5]} for index, item in enumerate(selected)]


def _execute_python(code, test_input, expected_output):
    blocked = ('import ', '__import__', 'open(', 'os.', 'sys.', 'subprocess', 'socket', 'shutil', 'eval(', 'exec(')
    if any(token in code.lower() for token in blocked):
        return {'passed': False, 'error_type': 'security', 'error': 'Restricted operation detected.', 'output': '', 'hint': 'Use only basic Python logic, input, and output for this exercise.'}
    started = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-I', '-S', '-c', code], input=test_input, text=True, capture_output=True, timeout=2, cwd=directory)
        output = result.stdout.strip()
        if result.returncode != 0:
            error = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'Program failed.'
            if 'IndentationError' in error:
                error_type = 'indentation'
            elif 'SyntaxError' in error:
                error_type = 'syntax'
            elif 'NameError' in error:
                error_type = 'name'
            elif 'TypeError' in error:
                error_type = 'type'
            else:
                error_type = 'runtime'
            return {'passed': False, 'error_type': error_type, 'error': error, 'output': output, 'hint': 'Check the highlighted syntax or verify your variables before running again.'}
        expected = expected_output.split('Output:', 1)[-1].strip()
        passed = output == expected
        return {'passed': passed, 'error_type': None if passed else 'logic', 'error': None if passed else 'Output does not match the expected result.', 'output': output, 'hint': None if passed else 'Compare your output with the expected output and check your loop or condition.'}
    except subprocess.TimeoutExpired:
        return {'passed': False, 'error_type': 'runtime', 'error': 'Execution timed out.', 'output': '', 'hint': 'Check your loop condition so the program eventually stops.'}
    finally:
        elapsed = round(time.perf_counter() - started, 3)


@student_bp.route('/student/programming/<int:company_id>')
@login_required
def programming_assessment(company_id):
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('student.company_selection'))
    return render_template('programming_assessment.html', company=company, questions=_programming_questions(company.id, company.name))


@student_bp.route('/student/programming/<int:company_id>/execute', methods=['POST'])
@login_required
def execute_programming(company_id):
    data = request.get_json() or {}
    started = time.perf_counter()
    result = _execute_python(data.get('code', ''), data.get('input', ''), data.get('expected', ''))
    attempt = dict(session.get('programming_attempt', {}))
    question_id = str(data.get('question_id', '0'))
    details = dict(attempt.get(question_id, {'attempts': 0, 'hints': 0, 'errors': []}))
    details['attempts'] += 1
    if not result['passed']:
        details['hints'] += 1
        details['errors'] = details['errors'] + [result['error_type']]
    attempt[question_id] = details
    session['programming_attempt'] = attempt
    session.modified = True
    result.update({'attempts': details['attempts'], 'hints': details['hints'], 'errors': details['errors'], 'execution_time': round(time.perf_counter() - started, 3)})
    return jsonify(result)


@student_bp.route('/student/dashboard')
@login_required
def dashboard():
    companies = Company.query.all()
    progress = Progress.query.filter_by(student_id=current_user.id).first()
    leaderboard = get_leaderboard()[:5]
    from placement_training.models import AptitudeAttempt, GeneralAptitudeTest
    completed_tasks = sum(1 for task in current_user.task_records if task.completed)
    completed_tasks += AptitudeAttempt.query.filter_by(student_id=current_user.id).count()
    completed_tasks += GeneralAptitudeTest.query.filter_by(student_id=current_user.id, status='completed').count()
    return render_template('student_dashboard.html', companies=companies, progress=progress, leaderboard=leaderboard, completed_tasks=completed_tasks)


@student_bp.route('/student/company-selection', methods=['GET', 'POST'])
@login_required
def company_selection():
    # Load companies with their skills to avoid N+1
    companies = Company.query.options(joinedload(Company.company_skills).joinedload(CompanySkill.skill)).all()

    # Fetch already selected company ids for current student
    student_company_records = StudentCompany.query.filter_by(student_id=current_user.id).all()
    selected_company_ids = [sc.company_id for sc in student_company_records]

    # Build mapping of company_id -> set of selected skill ids for this student
    selected_skills_by_company = {}
    for sc in student_company_records:
        skills = [s.skill_id for s in StudentCompanySkill.query.filter_by(student_company_id=sc.id).all()]
        selected_skills_by_company[sc.company_id] = skills

    def parse_eligibility(text):
        # Simple parser: look for 'CGPA >= X' or a number after 'CGPA' and 'backlog' numbers
        required_cgpa = None
        max_backlogs = None
        if not text:
            return required_cgpa, max_backlogs
        cgpa_match = re.search(r'CGPA\s*(?:>=|>|:|is)?\s*([0-9]+\.?[0-9]*)', text, re.IGNORECASE)
        if cgpa_match:
            try:
                required_cgpa = float(cgpa_match.group(1))
            except Exception:
                required_cgpa = None
        backlog_match = re.search(r'backlog[s]?\s*(?:<=|<=|:|is)?\s*([0-9]+)', text, re.IGNORECASE)
        if backlog_match:
            try:
                max_backlogs = int(backlog_match.group(1))
            except Exception:
                max_backlogs = None
        return required_cgpa, max_backlogs

    if request.method == 'POST':
        company_id = request.form.get('company_id')
        set_dream = request.form.get('set_dream') == 'on'
        company = Company.query.get(company_id)
        if not company:
            flash('Selected company not found.', 'danger')
            return redirect(url_for('student.company_selection'))

        # eligibility check
        required_cgpa, max_backlogs = parse_eligibility(company.eligibility_criteria or '')
        eligible = True
        if required_cgpa is not None and current_user.cgpa < required_cgpa:
            eligible = False
        if max_backlogs is not None and current_user.backlog_count > max_backlogs:
            eligible = False

        if not eligible:
            flash('You do not meet the basic eligibility criteria for this company.', 'warning')
            return redirect(url_for('student.company_selection'))

        existing = StudentCompany.query.filter_by(student_id=current_user.id, company_id=company.id).first()
        if existing:
            flash('You have already selected this company.', 'info')
        else:
            record = StudentCompany(student_id=current_user.id, company_id=company.id, status='selected')
            db.session.add(record)
            db.session.commit()
            flash(f'Company {company.name} selected.', 'success')

        # update selected_company_ids and selected_skills_by_company for immediate render
        selected_company_ids.append(company.id)
        if company.id not in selected_skills_by_company:
            selected_skills_by_company[company.id] = []

        if set_dream:
            current_user.dream_company_id = company.id
            db.session.commit()
            flash(f'{company.name} set as your dream company.', 'success')

        return redirect(url_for('student.company_selection'))

    return render_template('company_selection.html', companies=companies, selected_company_ids=selected_company_ids, selected_skills_by_company=selected_skills_by_company)



@student_bp.route('/student/aptitude/<int:company_id>')
@login_required
def aptitude_assessment(company_id):
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('student.company_selection'))
    return render_template('aptitude_assessment.html', company=company, questions=_company_questions(company.id, company.name))


@student_bp.route('/student/aptitude/<int:company_id>/generate', methods=['POST'])
@login_required
def generate_aptitude_questions(company_id):
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'success': False, 'message': 'Company not found.'}), 404
    return jsonify({'success': True, 'questions': _company_questions(company.id, company.name, limit=5)})


@student_bp.route('/student/aptitude-practice/<int:company_id>')
@login_required
def aptitude_practice(company_id):
    company = Company.query.get(company_id)
    if not company:
        flash('Company not found.', 'danger')
        return redirect(url_for('student.company_selection'))
    topic = request.args.get('topic')
    questions = extra_questions(company.name, topic) if topic else []
    return render_template('aptitude_practice.html', company=company, topics=COMPANY_TOPICS.get(company.name, ()), topic=topic, questions=questions)


@student_bp.route('/student/skill/<int:company_id>/<int:skill_id>')
@login_required
def skill_assessment(company_id, skill_id):
    company = Company.query.get(company_id)
    skill = Skill.query.get(skill_id)
    if not company or not skill:
        flash('Assessment not found.', 'danger')
        return redirect(url_for('student.company_selection'))
    if skill.name == 'Aptitude':
        return redirect(url_for('student.aptitude_topics_list', company_id=company.id))
    if skill.name == 'Group Discussion':
        return redirect(url_for('student.group_discussion_list'))
    if skill.name == 'Programming':
        return redirect(url_for('student.programming_assessment', company_id=company_id))
    if skill.name in TEXT_SKILL_PROMPTS:
        prompts = COMMUNICATION_COMPANY_PROMPTS.get(company.name, TEXT_SKILL_PROMPTS[skill.name])
        return render_template('communication_assessment.html', company=company, skill=skill, prompts=prompts)
    if skill.name == 'Technical Interview':
        return render_template('technical_interview.html', company=company, skill=skill, questions=_technical_questions(company.id, company.name))
    questions = _skill_questions(company.id, company.name, skill.name)
    return render_template('skill_assessment.html', company=company, skill=skill, questions=questions)


@student_bp.route('/student/company/<int:company_id>/deselect', methods=['POST'])
@login_required
def deselect_company(company_id):
    record = StudentCompany.query.filter_by(student_id=current_user.id, company_id=company_id).first()
    if record:
        db.session.delete(record)
        if current_user.dream_company_id == company_id:
            current_user.dream_company_id = None
        db.session.commit()
        flash('Company removed from your selections.', 'success')
    else:
        flash('Company is not selected.', 'info')
    return redirect(url_for('student.company_selection'))


@student_bp.route('/student/toggle-skill', methods=['POST'])
@login_required
def toggle_skill():
    data = request.get_json() or request.form
    company_id = int(data.get('company_id')) if data.get('company_id') else None
    skill_id = int(data.get('skill_id')) if data.get('skill_id') else None
    if not company_id or not skill_id:
        return {'success': False, 'message': 'company_id and skill_id required'}, 400

    # ensure company exists
    company = Company.query.get(company_id)
    if not company:
        return {'success': False, 'message': 'Company not found'}, 404

    # find or create StudentCompany record
    sc = StudentCompany.query.filter_by(student_id=current_user.id, company_id=company_id).first()
    if not sc:
        sc = StudentCompany(student_id=current_user.id, company_id=company_id, status='selected')
        db.session.add(sc)
        db.session.commit()

    # check existing selection
    existing = StudentCompanySkill.query.filter_by(student_company_id=sc.id, skill_id=skill_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return {'success': True, 'selected': False}
    else:
        new = StudentCompanySkill(student_company_id=sc.id, skill_id=skill_id)
        db.session.add(new)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return {'success': False, 'message': 'Could not save selection'}, 500
        return {'success': True, 'selected': True}


@student_bp.route('/student/skills')
@login_required
def skills():
    company = current_user.dream_company
    selected_skills = [item.skill for item in current_user.student_skills]
    company_skills = company.company_skills if company else []
    return render_template('skills.html', company=company, company_skills=company_skills, selected_skills=selected_skills)


@student_bp.route('/student/add-skill/<int:skill_id>', methods=['POST'])
@login_required
def add_skill(skill_id):
    skill = Skill.query.get(skill_id)
    if not skill:
        flash('Skill not found.', 'danger')
        return redirect(url_for('student.skills'))

    existing = [item for item in current_user.student_skills if item.skill_id == skill_id]
    if not existing:
        record = StudentSkill(student_id=current_user.id, skill_id=skill.id, completed=False, score=0.0)
        db.session.add(record)
        db.session.commit()
        flash(f'{skill.name} added to your learning track.', 'success')
    else:
        flash('This skill is already selected.', 'info')

    return redirect(url_for('student.skills'))


@student_bp.route('/student/skill/<int:skill_id>/complete', methods=['POST'])
@login_required
def complete_skill(skill_id):
    """Mark a student's selected skill complete and refresh stored progress."""
    record = StudentSkill.query.filter_by(student_id=current_user.id, skill_id=skill_id).first()
    if not record:
        return jsonify({'success': False, 'message': 'Skill is not in your learning track.'}), 404

    record.completed = True
    record.completed_at = datetime.utcnow()
    try:
        db.session.flush()
        calculate_student_progress(current_user.id)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Could not save skill completion.'}), 500
    return jsonify({'success': True, 'completed': True})


@student_bp.route('/student/learning-plan')
@login_required
def learning_plan():
    plans = LearningPlan.query.filter_by(student_id=current_user.id).all()
    return render_template('learning_plan.html', plans=plans)


@student_bp.route('/student/tasks')
@login_required
def tasks():
    tasks = Task.query.all()
    student_tasks = {item.task_id: item for item in current_user.task_records}
    return render_template('tasks.html', tasks=tasks, student_tasks=student_tasks)


@student_bp.route('/student/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    student_task = StudentTask.query.filter_by(student_id=current_user.id, task_id=task_id).first()
    if not student_task:
        task = Task.query.get(task_id)
        if task:
            student_task = StudentTask(student_id=current_user.id, task_id=task.id, completed=False)
            db.session.add(student_task)
    student_task.completed = not student_task.completed
    student_task.completed_at = datetime.utcnow() if student_task.completed else None
    db.session.commit()
    calculate_student_progress(current_user.id)
    flash('Task status updated.', 'success')
    return redirect(url_for('student.tasks'))


@student_bp.route('/student/tests')
@login_required
def tests():
    all_tests = Test.query.all()
    return render_template('tests.html', tests=all_tests)


@student_bp.route('/student/test/<int:test_id>')
@login_required
def take_test(test_id):
    test = Test.query.get_or_404(test_id)
    return render_template('test_detail.html', test=test)


@student_bp.route('/student/test/<int:test_id>/submit', methods=['POST'])
@login_required
def submit_test(test_id):
    test = Test.query.get_or_404(test_id)
    questions = test.questions
    total = len(questions)
    score = 0

    for question in questions:
        selected = request.form.get(f'question_{question.id}')
        if selected == question.correct_option:
            score += 1

    percentage = round((score / total) * 100, 2) if total else 0
    result = TestResult(student_id=current_user.id, test_id=test.id, score=score, percentage=percentage, passed=percentage >= 50)
    db.session.add(result)
    db.session.commit()
    calculate_student_progress(current_user.id)
    flash(f'Your test score is {percentage}%.', 'success')
    return redirect(url_for('student.progress'))


@student_bp.route('/student/progress')
@login_required
def progress():
    record = calculate_student_progress(current_user.id)
    from placement_training.models import AptitudeAttempt, GeneralAptitudeTest

    aptitude_history = AptitudeAttempt.query.filter_by(student_id=current_user.id).order_by(AptitudeAttempt.completed_at.desc()).all()
    general_history = GeneralAptitudeTest.query.filter_by(student_id=current_user.id).order_by(GeneralAptitudeTest.completed_at.desc()).all()
    aptitude_scores = [attempt.percentage for attempt in aptitude_history]
    aptitude_scores.extend(test.percentage for test in general_history if test.status == 'completed')
    aptitude_performance = sum(aptitude_scores) / len(aptitude_scores) if aptitude_scores else 0
    discussion_results = GroupDiscussionResult.query.filter_by(student_id=current_user.id).all()
    discussion_performance = sum(item.overall_score for item in discussion_results) / len(discussion_results) if discussion_results else 0
    completed_tasks = sum(1 for task in current_user.task_records if task.completed)
    completed_activities = completed_tasks + len(aptitude_history) + sum(1 for test in general_history if test.status == 'completed')
    from placement_training.services.aptitude_topics_service import APTITUDE_TOPICS
    total_available_tasks = Task.query.count() + len(APTITUDE_TOPICS) + 1
    total_available_tasks = max(total_available_tasks, completed_activities)
    return render_template(
        'progress.html',
        record=record,
        aptitude_history=aptitude_history,
        general_history=general_history,
        completed_tasks=completed_activities,
        remaining_tasks=max(total_available_tasks - completed_activities, 0),
        total_available_tasks=total_available_tasks,
        aptitude_performance=aptitude_performance,
        discussion_performance=discussion_performance,
    )


@student_bp.route('/student/leaderboard')
@login_required
def leaderboard():
    leaderboard = get_leaderboard()
    return render_template('leaderboard.html', leaderboard=leaderboard)


@student_bp.route('/student/mock-interview')
@login_required
def mock_interview():
    questions = ['Explain your project in detail.', 'What is polymorphism?', 'Describe a time you solved a problem under pressure.']
    return render_template('mock_interview.html', questions=questions)


@student_bp.route('/student/resume')
@login_required
def resume():
    resume = Resume.query.filter_by(student_id=current_user.id).first()
    return render_template('resume_builder.html', resume=resume)


@student_bp.route('/student/resume/save', methods=['POST'])
@login_required
def save_resume():
    resume = Resume.query.filter_by(student_id=current_user.id).first()
    if not resume:
        resume = Resume(student_id=current_user.id)
        db.session.add(resume)
    resume.full_name = request.form.get('full_name') or current_user.name
    resume.email = request.form.get('email') or current_user.email
    resume.phone = request.form.get('phone', '')
    resume.summary = request.form.get('summary', '')
    resume.education = request.form.get('education', '')
    resume.skills = request.form.get('skills', '')
    resume.projects = request.form.get('projects', '')
    resume.certifications = request.form.get('certifications', '')
    db.session.commit()
    flash('Resume saved successfully.', 'success')
    return redirect(url_for('student.resume'))


@student_bp.route('/student/certificates')
@login_required
def certificates():
    certs = Certificate.query.filter_by(student_id=current_user.id).all()
    return render_template('certificate_tracker.html', certificates=certs)


@student_bp.route('/student/eligibility')
@login_required
def eligibility():
    company = current_user.dream_company
    score = 0
    if company:
        company_skill_names = [item.skill.name for item in company.company_skills]
        selected_skills = [item.skill.name for item in current_user.student_skills]
        matched = set(company_skill_names).intersection(selected_skills)
        score = len(matched)
        if current_user.cgpa >= 7.0 and current_user.backlog_count == 0 and score >= 3:
            status = f'{company.name} -> Eligible'
        else:
            status = f'{company.name} -> Improve {", ".join(sorted(set(company_skill_names) - set(selected_skills))[:3])}'
    else:
        status = 'Please select a dream company first.'
    return render_template('eligibility.html', company=company, status=status)


# ==================== NEW APTITUDE TOPICS ROUTES ====================

@student_bp.route('/student/aptitude-topics')
@login_required
def aptitude_topics_list():
    """Display all aptitude topics for selection"""
    from placement_training.services.aptitude_topics_service import get_all_topics, APTITUDE_TOPICS
    topics = get_all_topics()
    topic_data = [(topic, APTITUDE_TOPICS[topic]['description']) for topic in topics]
    company_id = request.args.get('company_id', type=int)
    company = Company.query.get(company_id) if company_id else None
    return render_template('aptitude_topics.html', topics=topic_data, company=company)


@student_bp.route('/student/aptitude-topic-test/<topic_name>')
@login_required
def aptitude_topic_test(topic_name):
    """Start a topic-based aptitude test with 5 questions"""
    from placement_training.services.aptitude_topics_service import get_topic_questions, APTITUDE_TOPICS
    
    if topic_name not in APTITUDE_TOPICS:
        flash('Topic not found.', 'danger')
        return redirect(url_for('student.aptitude_topics_list'))
    
    company_id = request.args.get('company_id', type=int)
    company = Company.query.get(company_id) if company_id else None
    questions = get_topic_questions(topic_name)[:5]
    if company:
        from placement_training.models import AptitudeQuestionAttempt
        session_key = f'aptitude_session:{current_user.id}:{company.id}:{topic_name}'
        attempted = set()
        from placement_training.models import AptitudeTopic
        topic_record = AptitudeTopic.query.filter_by(name=topic_name).first()
        if topic_record:
            attempted = {item.question_key for item in AptitudeQuestionAttempt.query.filter_by(
                student_id=current_user.id, company_id=company.id, topic_id=topic_record.id
            ).all()}
        available = [item for item in get_topic_questions(topic_name) if item.get('question_key') not in attempted]
        questions = (available if len(available) >= 5 else get_topic_questions(topic_name))[:5]
        session[session_key] = [item.get('question_key') for item in questions]
        session.modified = True
    return render_template('aptitude_topic_test.html', topic_name=topic_name, questions=questions[:5], total_questions=5, company=company)


@student_bp.route('/student/aptitude-topic-submit/<topic_name>', methods=['POST'])
@login_required
def submit_aptitude_topic(topic_name):
    """Submit topic test answers and save results"""
    from placement_training.services.aptitude_topics_service import APTITUDE_TOPICS
    from placement_training.models import AptitudeAttempt, AptitudeTopic, AptitudeQuestionAttempt
    
    if topic_name not in APTITUDE_TOPICS:
        return jsonify({'success': False, 'message': 'Topic not found.'}), 404
    
    data = request.get_json(silent=True) or {}
    answers = data.get('answers', {})
    questions = get_topic_questions(topic_name)[:5]
    company_id = data.get('company_id') or request.args.get('company_id', type=int)
    company_id = int(company_id) if company_id else 0
    if company_id:
        session_key = f'aptitude_session:{current_user.id}:{company_id}:{topic_name}'
        question_keys = session.get(session_key, [])
        questions = [item for item in get_topic_questions(topic_name) if item.get('question_key') in question_keys]
        if len(questions) != 5:
            return jsonify({'success': False, 'message': 'This test session has expired. Please start the topic again.'}), 400

    topic = AptitudeTopic.query.filter_by(name=topic_name).first()
    if not topic:
        topic = AptitudeTopic(name=topic_name, description=APTITUDE_TOPICS[topic_name]['description'])
        db.session.add(topic)
        db.session.flush()
    
    correct_count = 0
    wrong_count = 0
    
    for idx, question in enumerate(questions):
        selected_answer = answers.get(str(idx))
        correct_answer = question['correct_answer']
        
        if selected_answer == correct_answer:
            correct_count += 1
        else:
            wrong_count += 1
        if company_id:
            db.session.add(AptitudeQuestionAttempt(
                student_id=current_user.id,
                company_id=company_id,
                topic_id=topic.id,
                question_key=question.get('question_key', f'{topic_name}:{idx}'),
                selected_answer=selected_answer or '',
                correct=selected_answer == correct_answer,
            ))
    
    percentage = (correct_count / len(questions)) * 100 if questions else 0
    
    # Save to database
    attempt = AptitudeAttempt(
        student_id=current_user.id,
        topic_id=topic.id,
        total_questions=len(questions),
        correct_answers=correct_count,
        wrong_answers=wrong_count,
        score=correct_count,
        percentage=percentage
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Update student progress
    calculate_student_progress(current_user.id)
    
    return jsonify({
        'success': True,
        'total': len(questions),
        'correct': correct_count,
        'wrong': wrong_count,
        'score': correct_count,
        'percentage': round(percentage, 2),
        'performance': 'HIGH' if percentage >= 80 else 'MEDIUM' if percentage >= 60 else 'LOW',
        'status': 'Completed'
    })


@student_bp.route('/student/general-aptitude-test')
@login_required
def general_aptitude_test():
    """Display 10-question general aptitude test"""
    from placement_training.services.aptitude_topics_service import get_general_aptitude_questions
    questions = get_general_aptitude_questions()
    return render_template('general_aptitude_test.html', questions=questions, total_questions=len(questions))


@student_bp.route('/student/general-aptitude-submit', methods=['POST'])
@login_required
def submit_general_aptitude():
    """Submit general aptitude test and save results"""
    from placement_training.models import GeneralAptitudeTest
    
    data = request.get_json() or {}
    answers = data.get('answers', {})
    questions_data = data.get('questions', [])
    
    correct_count = 0
    wrong_count = 0
    
    for idx in range(len(questions_data)):
        selected_answer = answers.get(str(idx))
        # The selected_answer would be the option letter (A, B, C, D)
        # We need to match it with correct answer
        # This requires the questions to be passed from frontend
        if selected_answer:  # Placeholder validation
            # In real implementation, verify against stored questions
            pass
    
    # For now, count from available data
    total = len(questions_data)
    for idx, question in enumerate(questions_data):
        selected = answers.get(str(idx))
        correct = question.get('correct_answer')
        if selected == correct:
            correct_count += 1
        else:
            wrong_count += 1
    
    percentage = (correct_count / total) * 100 if total else 0
    
    # Save to database
    test_result = GeneralAptitudeTest(
        student_id=current_user.id,
        total_questions=total,
        correct_answers=correct_count,
        wrong_answers=wrong_count,
        score=correct_count,
        percentage=percentage,
        status='completed'
    )
    db.session.add(test_result)
    db.session.commit()
    
    # Update student progress
    calculate_student_progress(current_user.id)
    
    return jsonify({
        'success': True,
        'total': total,
        'correct': correct_count,
        'wrong': wrong_count,
        'unanswered': total - correct_count - wrong_count,
        'score': correct_count,
        'percentage': round(percentage, 2),
        'performance': 'HIGH' if percentage >= 80 else 'MEDIUM' if percentage >= 60 else 'LOW',
        'status': 'Completed'
    })


@student_bp.route('/student/group-discussion')
@login_required
def group_discussion_list():
    """Display available group discussion sessions"""
    from placement_training.models import GroupDiscussionSession
    sessions = GroupDiscussionSession.query.filter(GroupDiscussionSession.status.in_(['scheduled', 'in_progress'])).all()
    return render_template('group_discussion_list.html', sessions=sessions)


@student_bp.route('/student/group-discussion/join/<int:session_id>')
@login_required
def join_group_discussion(session_id):
    """Join a group discussion session"""
    from placement_training.models import GroupDiscussionSession, GroupDiscussionParticipant
    
    session = GroupDiscussionSession.query.get_or_404(session_id)
    
    # Check if already joined
    existing = GroupDiscussionParticipant.query.filter_by(
        session_id=session_id,
        student_id=current_user.id
    ).first()
    
    if existing:
        flash('You are already participating in this session.', 'info')
    else:
        participant = GroupDiscussionParticipant(
            session_id=session_id,
            student_id=current_user.id
        )
        db.session.add(participant)
        db.session.commit()
        flash('Joined the discussion session.', 'success')
    
    return redirect(url_for('student.group_discussion_room', session_id=session_id))


@student_bp.route('/student/group-discussion/room/<int:session_id>')
@login_required
def group_discussion_room(session_id):
    """Group discussion room with voice features"""
    from placement_training.models import GroupDiscussionSession, GroupDiscussionParticipant
    
    session = GroupDiscussionSession.query.get_or_404(session_id)
    
    # Check if student is a participant
    is_participant = GroupDiscussionParticipant.query.filter_by(
        session_id=session_id,
        student_id=current_user.id
    ).first()
    
    if not is_participant:
        flash('You must join the session first.', 'warning')
        return redirect(url_for('student.group_discussion_list'))
    
    # Get all participants
    participants = GroupDiscussionParticipant.query.filter_by(session_id=session_id).all()
    participant_students = [p.student for p in participants]
    
    return render_template('group_discussion_room.html', 
                         session=session, 
                         participants=participant_students,
                         is_participant=True)


@student_bp.route('/student/group-discussion/<int:session_id>/leave', methods=['POST'])
@login_required
def leave_group_discussion(session_id):
    """Leave a group discussion session"""
    from placement_training.models import GroupDiscussionParticipant
    from datetime import datetime
    
    participant = GroupDiscussionParticipant.query.filter_by(
        session_id=session_id,
        student_id=current_user.id
    ).first()
    
    if participant:
        participant.left_at = datetime.utcnow()
        db.session.commit()
        flash('You have left the discussion.', 'info')
    
    return redirect(url_for('student.group_discussion_list'))


@student_bp.route('/student/group-discussion/<int:session_id>/evaluate', methods=['POST'])
@login_required
def submit_discussion_evaluation(session_id):
    """Submit evaluation results for group discussion"""
    from placement_training.models import GroupDiscussionSession, GroupDiscussionResult
    
    data = request.get_json() or {}
    
    session = GroupDiscussionSession.query.get_or_404(session_id)
    
    # Calculate overall score from individual criteria
    communication = float(data.get('communication', 0))
    participation = float(data.get('participation', 0))
    relevance = float(data.get('relevance', 0))
    confidence = float(data.get('confidence', 0))
    listening = float(data.get('listening', 0))
    team_interaction = float(data.get('team_interaction', 0))
    
    overall = (communication + participation + relevance + confidence + listening + team_interaction) / 6
    
    result = GroupDiscussionResult(
        session_id=session_id,
        student_id=current_user.id,
        communication_score=communication,
        participation_score=participation,
        relevance_score=relevance,
        confidence_score=confidence,
        listening_score=listening,
        team_interaction_score=team_interaction,
        overall_score=overall,
        feedback=data.get('feedback', '')
    )
    
    db.session.add(result)
    db.session.commit()
    
    # Update student progress
    calculate_student_progress(current_user.id)
    
    return jsonify({
        'success': True,
        'message': 'Evaluation saved successfully',
        'overall_score': round(overall, 2)
    })


# Helper function for checking question answers
def get_topic_questions(topic_name):
    """Get questions for a topic (helper function)"""
    from placement_training.services.aptitude_topics_service import get_topic_questions as get_questions
    return get_questions(topic_name)


@student_bp.route('/student/recommendations')
@login_required
def recommendations():
    skill_data = {'Programming': 90, 'Aptitude': 82, 'SQL': 45, 'Communication': 50}
    suggestions = recommend_skills(skill_data)
    return render_template('recommendation.html', suggestions=suggestions)
