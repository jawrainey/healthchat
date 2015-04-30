from settings import Config


class Utils:
    def scrape_reddit(self, username, password):
        '''
        Step 1: scraped the 1000 most recent comments for each reddit sub.

        Args:
            username (str): the username to authenticated with reddit.
            password (str): the password to authenticated with reddit.

        Returns:
            Writes a file to data folder for each main subreddit category that
            contains the 1000 most recent comments for each subreddit listed.
        '''
        import praw
        import datetime

        # The sub-reddits where we obtain our primary data. Keys are concepts.
        subreddits = {'exercise': ['bicycling', 'bodyweightfitness',
                                   'fitness', 'loseit', 'running'],
                      'diet': ['cooking', 'eatcheapandhealthy',
                               'food', 'keto', 'slowcooking']}

        r = praw.Reddit('Ontological data collection -- @jawrainey.')
        # Required to bypass unauthorised download limit of 25 comments.
        r.login(username, password)
        # Store data for each sub in a single file by date, related to concept.
        for concept, subs in subreddits.iteritems():
            for sub in subs:
                for comment in r.get_subreddit(sub).get_comments(limit=None):
                    today = datetime.datetime.now().strftime("%d-%m-%Y")
                    with open((today + '-' + concept), 'a') as f:
                        # Reddit comments may contain foreign characters.
                        f.write(comment.body.encode('ascii', 'ignore'))

    def assign_terms_to_obo_file(self):
        '''
        Step 2: manually assign each unknown word from the reddit word dataset
                to an associated concept for this term in the ontology.

        Note: this method works on the assumption that there exists an OBO file
        with the initial relationships to which terms should be added.
        '''
        # The term to insert into the OBO file later.
        term = ('\n[Term]\n'
                'id: ID:%s\n'
                'name: %s\n'
                'is_a: ID:%s ! %s\n')

        import obo
        # The words in all reddit files that does not exist in known words.
        unknown_words = self.__diff_known_words(self.__reddit_data())
        # The concepts in the current ontology.
        obo_content = [i for i in obo.Parser(Config.ONTOLOGY)]
        # Prevents re-calculated later, which would be memory/time intensive.
        known_concepts = [str(i.tags['name'][0]) for i in obo_content]
        # Used to increment the ID.
        last_id = int(str(obo_content[-1].tags['id'][0]).split(':')[1])
        # Also used to open file for writing later.
        known_words_file = Config.DATA_FOLER + 'known_words.txt'

        for word in unknown_words:
            if word not in known_concepts:
                concepts = raw_input(
                    'Select concept for %s from:\n    %s or "skip"\n'
                    % (word, ', '.join(known_concepts[2:18])))

                if 'skip' not in concepts:
                    for concept in [i.strip() for i in concepts.split(',')]:
                        with open(Config.ONTOLOGY, 'a') as f:
                            last_id += 1
                            pid = self.__get_concept_id(obo_content, concept)
                            f.write(term % (last_id, word, pid, concept))
                else:
                    with open(known_words_file, 'a') as kwf:
                        kwf.write(word + '\n')
            else:
                print ('%s exists in ontology or known words file.' % word)

    def populate_db_from_obo_file(self):
        '''
        Step 3: Inserts the contents of the obo file (concepts/terms) to a
                transitive closure RDBMS representation for querying of system.
        '''
        import obo
        from app import db
        # Note: structure.obo MUST contain the initial concepts.
        obo_content = [i for i in obo.Parser(Config.ONTOLOGY)]

        from app import models
        known_ids = [tup[0] for tup in db.session.query(models.Nodes.id).all()]

        for i in obo_content:
            _id = int(str(i.tags['id'][0]).split(':')[1])
            # The root element does not have a parent.
            # Assign it a one as PostgreSQL does not accept zero (no parent).
            _pid = (int(str(i.tags['is_a'][0]).split(':')[1])
                    if 'is_a' in str(i) else 1)
            _name = str(i.tags['name'][0])
            # Only add NEW terms to the database.
            if _id not in known_ids:
                node = models.Nodes(id=_id, parent=_pid, name=_name)
                db.session.add(node)
                db.session.commit()
                # Add ontological term to node table.
                # Collect ancestor of parent, and insert into closure table.
                values = [(i.parent, _id, i.depth + 1) for i in
                          models.Closure.query.filter_by(child=_pid).all()]
                for i in values:
                    db.session.add(
                        models.Closure(parent=i[0], child=i[1], depth=i[2]))
                    db.session.commit()
                db.session.add(
                    models.Closure(parent=node.id, child=node.id, depth=0))
                db.session.commit()

    def __reddit_data(self):
        '''
        Generates a set of words for all scraped reddit file and saves this
        into a list (memory) rather than file for simplicity.

        Returns:
            set: all unique words in the reddit scrapped data.
        '''
        import glob
        import re
        from nltk.corpus import stopwords

        # Stored here as calling within the loop would take a long time.
        stopwords = stopwords.words("english")
        data = ''
        # Prevent loading of known words, which would make it redundant!
        data_files = [i for i in glob.glob(Config.DATA_FOLER + '*.txt')
                      if 'known_words' not in i]
        # Simplifies file management by reading ALL known data to memory.
        for reddit_file in data_files:
            with open(reddit_file, 'r') as content:
                data += content.read()

        data = data.replace('-', ' ')  # Markdown URLs
        data = re.sub(r'[^a-zA-Z&^\s]', '', data)  # Spaces left untouched.
        # Convert data string to list to parse by word.
        # Convert to lower-case to prevent Issues/issues when comparing words.
        # Remove long words as they are reddit waffle.
        # Convert result to set to remove duplicate words.
        return set([word.lower() for word in data.split()
                    if len(word) <= 12 and word not in stopwords])

    def __diff_known_words(self, data):
        '''
        Removes all known words (from known_words.txt) from given argument.
        This is used to simplify the amount of words manually parsed in step 2.

        Args:
            reddit_data (set): contains all known words in reddit scrapped data.

        Returns:
            set: A new set that does not contain the known words.
        '''
        known_words = ''
        with open(Config.DATA_FOLER + 'known_words.txt', 'r') as f:
            known_words += f.read()
        return data - set(known_words.split())

    def __get_concept_id(self, obo_content, user_concept):
        '''
        Obtains the ID from the ontology for a given concept.

        Args:
            obo_content (list): The current ontology
            user_concept (str): The user defined concept.

        Returns:
            An int containing the ID of the given concept.
        '''
        for stanza in obo_content:
            concept = str(stanza.tags['name'][0])
            if concept == user_concept:
                return int(str(stanza.tags['id'][0]).split(':')[1])
        raise RuntimeError("Concept (%s) does not exist." % user_concept)
