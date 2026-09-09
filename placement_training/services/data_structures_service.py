"""Question bank and lightweight checks for the Data Structures skill module."""


DATA_STRUCTURE_MCQ = [
    {
        'topic': 'Arrays',
        'question': 'Which data structure stores elements in contiguous memory locations?',
        'options': ['Array', 'Linked List', 'Stack', 'Graph'],
        'answer': 0,
        'explanation': 'An array stores elements in adjacent memory locations, which makes indexed access fast.',
    },
    {
        'topic': 'Linked Lists',
        'question': 'What does a linked-list node normally contain besides its data?',
        'options': ['A pointer to another node', 'A sorted index table', 'A queue counter', 'A tree root only'],
        'answer': 0,
        'explanation': 'A linked-list node stores a link, or pointer/reference, to the next node.',
    },
    {
        'topic': 'Stack',
        'question': 'Which principle does a stack follow?',
        'options': ['FIFO', 'LIFO', 'Random access', 'Priority first'],
        'answer': 1,
        'explanation': 'A stack follows LIFO: the Last item In is the First item Out.',
    },
    {
        'topic': 'Queue',
        'question': 'Which operation adds an item to the back of a queue?',
        'options': ['Push', 'Pop', 'Enqueue', 'Peek'],
        'answer': 2,
        'explanation': 'Enqueue inserts an item at the rear of a queue; dequeue removes one from the front.',
    },
    {
        'topic': 'Tree',
        'question': 'What is the topmost node in a tree called?',
        'options': ['Leaf', 'Root', 'Edge', 'Sibling'],
        'answer': 1,
        'explanation': 'The root is the unique starting node from which the tree branches.',
    },
    {
        'topic': 'Binary Tree',
        'question': 'What is the maximum number of children a binary-tree node can have?',
        'options': ['1', '2', '3', 'Unlimited'],
        'answer': 1,
        'explanation': 'Each node in a binary tree has at most two children: commonly called left and right.',
    },
    {
        'topic': 'BST',
        'question': 'In a binary search tree, values in the left subtree are usually:',
        'options': ['Greater than the node', 'Less than the node', 'Always equal to the node', 'Unrelated to the node'],
        'answer': 1,
        'explanation': 'The BST ordering rule places smaller values on the left and larger values on the right.',
    },
    {
        'topic': 'Hashing',
        'question': 'What is a hash collision?',
        'options': ['A full table', 'Two keys producing the same hash index', 'A deleted key', 'A sorted bucket'],
        'answer': 1,
        'explanation': 'A collision occurs when different keys map to the same location in a hash table.',
    },
    {
        'topic': 'Graph Basics',
        'question': 'What do the edges of a graph represent?',
        'options': ['Connections between vertices', 'Only the first vertex', 'Array indexes', 'Tree heights'],
        'answer': 0,
        'explanation': 'Edges represent relationships or connections between graph vertices.',
    },
    {
        'topic': 'Time Complexity Basics',
        'question': 'What is the time complexity of reading an array element by index?',
        'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n squared)'],
        'answer': 0,
        'explanation': 'An array index directly identifies the memory position, so access takes constant time: O(1).',
    },
]

PROGRAMMING_BASICS = [
    {
        'title': 'Reverse an Array',
        'statement': 'Write code that returns an array in reverse order without changing the values.',
        'hint': 'Try using a loop to traverse the array from its last index to its first.',
        'second_hint': 'Keep an output array and append each item while moving backward through the input.',
        'explanation': 'Traverse from the final index down to zero and append each value to the result.',
    },
    {
        'title': 'Find Largest Element in Array',
        'statement': 'Write code that finds and returns the largest number in an array.',
        'hint': 'Start with the first element as the current largest, then compare every other element.',
        'second_hint': 'Update the largest value whenever the current array item is greater than it.',
        'explanation': 'A single pass keeps the largest value seen so far and runs in O(n) time.',
    },
    {
        'title': 'Implement Simple Stack Push Operation',
        'statement': 'Write code that adds one value to the top of a stack represented by an array or list.',
        'hint': 'A stack push adds the new value at the end of the existing stack.',
        'second_hint': 'Use append or push on the stack, then return the updated stack.',
        'explanation': 'Push inserts an item at the top of the stack; with an array/list, the end is a simple top.',
    },
]


def validate_programming_answer(question_index, code):
    """Give a safe beginner-level check without executing student-submitted code."""
    normalized = (code or '').lower()
    if question_index == 0:
        correct = any(token in normalized for token in ('reverse', '[::-1]', 'reversed(', 'range(')) and any(token in normalized for token in ('array', 'list', 'values', 'nums'))
    elif question_index == 1:
        correct = any(token in normalized for token in ('max(', 'largest', 'maximum')) and any(token in normalized for token in ('for ', 'while ', 'loop'))
    else:
        correct = any(token in normalized for token in ('append(', '.push(', 'push(')) and any(token in normalized for token in ('stack', 'list', 'array'))
    return correct
