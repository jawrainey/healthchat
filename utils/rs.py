from collections import Counter
from operator import itemgetter
import os


def __frequency_for_file(filename):
    '''
    Given a filename, open the file and perform a word-frequency count.

    Args:
        filename (str): The name of the file to open.

    Returns:
        list: a list containing the word-frequency of the given file.
    '''
    import re
    from nltk.corpus import stopwords

    stopwords = stopwords.words("english")

    with open(filename, 'r') as f:
        data = f.read()

    data = data.replace('-', ' ')  # Markdown URLs
    data = re.sub(r'[^a-zA-Z&^\s]', '', data)  # Spaces left untouched.
    data = [word for word in data.split() if word not in stopwords]
    data = Counter(data)
    return sorted(data.items(), key=itemgetter(1), reverse=True)


def download_comments_for_subreddit(concept, subreddit):
    '''
    Save 1000 most recent comments on a subreddit for a specific concept.

    Args:
        concept (str): Used to save output file in the correct directory.
        subreddit (str): The name of subreddit to download comments from.
    '''
    import praw

    r = praw.Reddit('Ontological data collection -- @jawrainey.')

    # Required to bypass unauthorised download limit of 25 comments.
    r.login('username', 'password')

    if not os.path.exists(concept):
        os.makedirs(concept)

    comments = r.get_subreddit(subreddit).get_comments(limit=None)

    for comment in comments:
        with open(os.path.join(concept, subreddit), 'a') as f:
            # Required as reddit comments may contain foreign characters.
            f.write(comment.body.encode('ascii', 'ignore'))


def save_frequency_by_concept(concept, subs):
    '''
    Generates a word frequency for all files related to a concept.

    Args:
        concept (str): The concept (class) of the ontology, e.g. food, diet etc.
        subs (list): A list of subreddits related to the concept.
    '''
    # Could write individual frequency to file at this point...
    data = [__frequency_for_file(os.path.join(concept, sub)) for sub in subs]
    # merge dictionaries by value (frequency).
    data = sum((Counter(dict(i)) for i in data), Counter())
    # sort by most frequent first.
    data = sorted(data.items(), key=itemgetter(1), reverse=True)

    if not os.path.exists('output'):
        os.makedirs('output')

    with open('output/frequency_for_' + concept + '.txt', 'w') as f:
        for item in data:
            f.write("%s\n" % (item,))


if __name__ == "__main__":
    # The subreddits I am using in my project. Five for each associated concept.
    subreddits = {'exercise': ['bicycling', 'bodyweightfitness',
                               'fitness', 'loseit', 'running'],
                  'diet': ['cooking', 'eatcheapandhealthy',
                           'food', 'keto', 'slowcooking']}

    for concept, subs in subreddits.iteritems():
        for sub in subs:
            download_comments_for_subreddit(concept, sub)
        save_frequency_by_concept(concept, subs)
