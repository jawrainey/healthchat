def get_concept_id(obo_content, user_concept):
    '''
    Obtains the ID from the ontology for a given concept.

    Args:
        obo_content (list): The current ontology
        user_concept (str): The user defined concept (likely a word from file).

    Returns:
        An int containing the ID of the given concept.
    '''
    for stanza in obo_content:
        concept = str(stanza.tags['name'][0])
        if concept == user_concept:
            return int(str(stanza.tags['id'][0]).split(':')[1])
    raise RuntimeError("Concept provided (%s) does not exist." % user_concept)

if __name__ == "__main__":
    import fileinput  # Gosh, I do love Python!
    import obo

    # NEW concepts, well, words related to concepts, i.e. melon IS A fruit.
    files = ['../data/10-02-14/final/after/new_frequency_for_diet.txt',
             '../data/10-02-14/final/after/new_frequency_for_exercise.txt']
    obo_file = '../data/structure.obo'

    content = [line for line in fileinput.input(files)]
    obo_content = [i for i in obo.Parser(obo_file)]

    all_concepts = [str(i.tags['name'][0]) for i in obo_content]
    core_concepts = all_concepts[2:18]  # Only display core concepts to user.

    # The term to insert into the OBO file later.
    term = ('\n[Term]\n'
            'id: ID:%s\n'
            'name: %s\n'
            'is_a: ID:%s ! %s\n')

    # Used to increment the ID
    last_id = int(str(obo_content[-1].tags['id'][0]).split(':')[1])

    # add each word to the OBO file for the related concept.
    with open(obo_file, 'a') as f:
        for word in content:
            word = word.strip()
            if word not in all_concepts:  # Do not add concept twice.
                # What if the word should belong to multiple concepts?
                # Do we want to add a healthy/unhealthy property?
                last_id += 1
                concept = raw_input('Select a concept for %s from:\n%s\n'
                                    % (word, ', '.join(core_concepts)))
                if 'skip' not in concept:
                    is_a_id = get_concept_id(obo_content, concept)
                    f.write(term % (last_id, word, is_a_id, concept))
            else:
                print ('%s already exists in ontology.' % word)
