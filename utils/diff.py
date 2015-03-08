def diff_two_files(A, B):
    '''
    Saves the words that occur in A, but not B to a file.

    Args:
        A (list): contains a list of tuples (word, frequency).
        B (list): contains a list of tuples (word, frequency).

    '''
    import ast
    # Converting tuples to single words as frequency is not important.
    A = [ast.literal_eval('({0})'.format(i))[0] for i in A]
    B = [ast.literal_eval('({0})'.format(i))[0] for i in B]
    C = list(set(A) - set(B))  # words that occur in A and not B.

    with open('diff.txt', 'w') as f:
        for word in C:
            if len(word) <= 14:  # unnecessary words, i.e. words joined together
                f.write("%s\n" % word)

if __name__ == "__main__":
    with open('../data/12-02-14/final/before/frequency_for_exercise.txt') as f:
        diet = f.read().splitlines()
    with open('../data/12-02-14/final/before/frequency_for_diet.txt') as f:
        food = f.read().splitlines()

    diff_two_files(diet, food)
