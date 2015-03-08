import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()


def concept_id(concept):
    '''
    Obtains the ID for a given ontological concept, i.e. diet.
    TODO: this query is limited as it's specific, consider 'LIKE'.

    Args:
        concept (str): the concept to obtain the ID for.

    Returns:
        str: ID of the concept, otherwise raise exception.
    '''
    query = 'SELECT id FROM nodes WHERE name = ?'
    row = cursor.execute(query, (concept,)).fetchone()
    return row[0] if row else None


def parent_name(parent_id):
    '''
    Obtains the name of a concept based on the ID.
    TODO: error checking; id may not always be valid (unlike above query).

    Args:
        parent_id (str): the ID of the parent to search for.

    Returns:
        str: name of parent concept based on ID.
    '''
    query = 'SELECT name FROM nodes WHERE id = ' + str(parent_id)
    return cursor.execute(query).fetchone()[0]


def get_subtree_of_concept(concept_id):
    '''
    Includes the concept provided, i.e. diet and all subs of tree.

    Args:
        concept_id (int): the ID of the known concept.

    Returns:
        list: sub-tree elements for the given concept ID.
    '''
    query = ('SELECT n.* FROM nodes n '
             'JOIN closure a ON (n.id = a.child) '
             'WHERE a.parent = ' + str(concept_id))
    return cursor.execute(query).fetchall()


def get_concepts_of_user_message(message):
    '''
    Obtains the frequency of concepts from words (terms) in user's message.

    Args:
        message (str): the message received by the user.

    Returns:
        dict: contains frequency (counter) of terms in user's message.
    '''
    import collections
    import re
    # Remove none English characters besides spaces.
    terms = re.sub(r'[^a-zA-Z&^\s]', '', message)
    terms = message.lower().split(' ')
    concepts_in_user_message = collections.Counter()

    for term in terms:
        concept = concept_id(term)
        if concept:
            parent_id_of_term = get_subtree_of_concept(concept)[0][1]
            concepts_in_user_message[parent_name(parent_id_of_term)] += 1
    return concepts_in_user_message


def select_response(questions, message):
    '''
    Select an open-ended question at random for the response.

    Args:
        questions (dict): concept (key), and list of associated OEQs (values).
        message (str): the message sent to the client by the user.

    Returns:
        str: response to send to the user.
    '''
    import random
    terms_in_message = get_concepts_of_user_message(message)
    if terms_in_message:
        # Determine focus of the message (based on concept).
        highest_frequency_term_in_message = terms_in_message.most_common()[0][0]
        # Select set of OEQ for the most common concept.
        concept_responses = questions[highest_frequency_term_in_message]
        return random.choice(concept_responses)
    else:
        # NOTE: If no terms detected in response send clarification question.
        return 'Can you clarify what you meant by that?'


def initial_message(questions):
    '''
    Select an initial question at random from pre-defined list.
    The aim is to set the scene, and attempt to elicit a response from user.

    Args:
        questions (list): all initial questions to select from.

    Returns:
        str: opening message and question to send to the user.
    '''
    import random
    return ('I would like to take a few minutes to learn about your current '
            'diet and exercise routines. ' + random.choice(questions))


def __load_questions():
    '''
    Reads Open-Ended-Questions (OEQ) from a json file to a dictionary.
    Note: these are stored in a file as they will only change manually.

    Returns:
        dict: contains the initial and open-ended questions.
    '''
    import json
    with open('../data/questions.json') as js:
        return json.load(js)
