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
            2. Select pre-defined OEQ from database for that concept.
            3. Group OEQ's by rating.
            4. Randomly select and return one of the highest rating questions.

        Args:
            user_message (str): the message sent to the client by the user.

        Returns:
            str: the OEQ response to send to the user.
        '''
        from app import models
        from flask import request
        import random

        terms_in_message = self.__concept_frequency(user_message)

        if terms_in_message:
            most_freq_concept = terms_in_message.most_common()[0][0]
            all_questions = (models.Question.query.filter_by(
                             concept=most_freq_concept).order_by(
                             models.Question.rating.desc()))

            # Rounding for distinction, e.g. .6 vs .600000000
            highest_rated_questions = [i.question for i in all_questions
                                       if round(i.rating, 1) ==
                                       round(all_questions[0].rating, 1)]

            # Made a set as we do not want to know many times each was sent.
            all_sent = [i.content for i in set(models.Message.query.filter_by(
                conversation_id=request.namespace.socket.sessid,
                status='service').all())]

            # Send all highest rated questions, then those not sent, then any.
            unsent_hrq = list(set(highest_rated_questions).difference(all_sent))
            all_questions = [i.question for i in all_questions]
            unsent_question = list(set(all_questions).difference(all_sent))

            if unsent_hrq:
                return random.choice(unsent_hrq)
            elif unsent_question:
                return random.choice(unsent_question)
            else:
                return random.choice(all_questions)
        else:
            # NOTE: no terms detected in response send clarification question.
            # TODO: re-factor to questions.json then load/save to db like OEQ.
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
        from app import models
        import collections
        import re

        # Remove none English characters besides spaces.
        terms = re.sub(r'[^a-zA-Z\s]', '', message).lower().split(' ')
        # Remove white spaces from replace above, and short (I) # words
        terms = [term for term in terms if len(term) > 1]
        concepts_in_user_message = collections.Counter()

        for term in terms:
            concept = self.db.concept_id(term)
            if concept:
                parent_id = self.db.get_subtree_of_concept(concept)[0][1]
                parent_name = self.db.parent_name(parent_id)
                # Prevents issue of detecting concepts without related questions
                # e.g. without 'parent' concept (health, diet, exercise, etc.)
                concepts = set([i.concept for i in models.Question.query.all()])
                if parent_name in concepts:
                    concepts_in_user_message[parent_name] += 1
        return concepts_in_user_message
