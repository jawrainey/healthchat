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


def add_terms_to_obo_ontology(output_file, known_concepts, obo_content):
    '''
    Reads a list of words (ontology terms, e.g. watermelon). For each term,
    an input dialogues provided to allow the user to associate a concept
    for this term. This relationship is written to an OBO file.

    Note: this method works on the assumption that there exists an OBO file with
    the basic structure and relationships to which terms should be added.

    Args:
        output_file (str): Location of
        known_concepts (list): Ensures same concepts are not added again.
        obo_content (list): Used to lookup ID of current and related concept.
    '''
    # The term to insert into the OBO file later.
    term = ('\n[Term]\n'
            'id: ID:%s\n'
            'name: %s\n')

    # Used to increment the ID
    last_id = int(str(obo_content[-1].tags['id'][0]).split(':')[1])

    # add each word to the OBO file for the related concept.
    with open(output_file, 'a') as f:
        for word in content:
            if word not in known_concepts:  # Do not add concept twice.
                concepts = raw_input('Select a concept for %s from:\n%s\n'
                                     % (word, ', '.join(known_concepts[2:18])))
                if 'skip' not in concepts:
                    concepts = [item.strip() for item in concepts.split(',')]
                    last_id += 1
                    f.write(term % (last_id, word))
                    # Add relationship, which may consist of be many concepts.
                    for concept in concepts:
                        is_a_id = get_concept_id(obo_content, concept)
                        print is_a_id, concept
                        f.write(('is_a: ID:%s ! %s\n') % (is_a_id, concept))
            else:
                print ('%s already exists in ontology.' % word)


if __name__ == "__main__":
    import fileinput
    import obo

    # NEW concepts, well, words related to concepts, i.e. melon IS A fruit.
    files = ['../data/10-02-14/final/after/new_frequency_for_diet.txt',
             '../data/10-02-14/final/after/new_frequency_for_exercise.txt']
    output_file = '../data/structure.obo'

    content = [line.strip() for line in fileinput.input(files)]
    obo_content = [i for i in obo.Parser(output_file)]
    known_concepts = [str(i.tags['name'][0]) for i in obo_content]

    add_terms_to_obo_ontology(output_file, known_concepts, obo_content)
