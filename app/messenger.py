class Messenger:
    '''
    Selects Brief Motivational Intervention (BMI) messages to send to a user.
    '''
    def __init__(self):
        """
        Populate attributes on initialisation.

        Args:
            config (json): Client specific configuration file that contains
            the questions to send to the user.
        """
        from database import Database
        self.db = Database()
        self.config = self.__load_responses()

    def initial_message(self):
        '''
        Select an initial question at random from pre-defined list.
        The aim is to set the scene, and attempt to elicit a response from user.

        Args:
            questions (list): all initial questions to select from.

        Returns:
            str: opening message and question to send to the user.
        '''
        import random
        message = random.choice(self.config['initialQuestions'])
        return ('I would like to take a few minutes to learn about your '
                'current diet and exercise routines. ' + message)

    def open_ended_question(self, user_message):
        '''
        Select a context appropriate open-ended question to send to user.

        To achieve this we currently:
            1. Detect most frequent concept based on terms in user's message.
            2. Select pre-defined list of OEQ for that concept.
            3. Randomly select and return an OEQ from list (2.).

        Args:
            questions (dict): concept (key), and list of OEQs (values).
            user_message (str): the message sent to the client by the user.

        Returns:
            str: the OEQ response to send to the user.
        '''
        from app import models

        import random
        terms_in_message = self.__concept_frequency(user_message)
        if terms_in_message:
            most_freq_concept = terms_in_message.most_common()[0][0]
            # TODO: can highest rating group be obtained via SQL?
            # Obtain all rows and order by rating.
            questions = (models.Question.query.filter_by(
                concept=most_freq_concept).order_by(
                    models.Question.rating.desc()))
            # Select all questions that are of highest rating.
            questions = [i.question for i in questions
                         if i.rating == questions[0].rating]
            return random.choice(questions)
        else:
            # NOTE: no terms detected in response send clarification question.
            return 'Can you clarify what you meant by that?'

    def reflective_summary(self, user_message):
        '''
        A short restatement of a users thoughts and feelings to build rapport,
        and to ensure effective communication between system and user.

        To select an appropriate (context dependent) summary:
            1. Detect most common concept in user message.
            2. Select list of pre-defined summaries for concept from config.
            3. String replace a random summary from 2. with the concept of 1.

        Args:
            user_message (str): The message to parse and detect concepts from.

        Returns:
            str: reflective summary of users message.

        '''
        return 0

    def __load_responses(self):
        '''
        Reads Open-Ended-Questions (OEQ) from a json file to a dictionary.
        Note: these are stored in a file as they will only change manually.

        Returns:
            dict: contains responses to send to the user.
        '''
        import json
        path = '/Users/jawrainey/Dropbox/uni/04/CM3203/fyp/data/questions.json'
        with open(path) as f:
            return json.load(f)

    def __concept_frequency(self, message):
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
            concept = self.db.concept_id(term)
            if concept:
                parent_id = self.db.get_subtree_of_concept(concept)[0][1]
                concepts_in_user_message[self.db.parent_name(parent_id)] += 1
        return concepts_in_user_message
