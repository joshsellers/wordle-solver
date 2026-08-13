import sys
import os

loaded_words = False

word_length = 5
words = []

letters = []
excluded_letters = []
excluded_indices = {}
max_occurences = {}
min_occurences = {}

word_frame = []


def reset():
    global letters
    global excluded_letters
    global excluded_indices
    global max_occurences
    global min_occurences
    global loaded_words
    global words

    loaded_words = False
    word_length = 5
    words = []
    letters = []
    excluded_letters = []
    excluded_indices = {}
    max_occurences = {}
    min_occurences = {}
    word_frame = []

    print('Reset memory')


def load_words():
    global loaded_words

    base_path = f'{os.path.realpath(os.path.dirname(__file__))}/'

    with open(f'{base_path}words_alpha.txt', 'r') as words_file:
        for line in words_file:
            if len(line.strip()) == word_length: 
                words.append(line.strip())

    loaded_words = True


def add_excluded_index(letter, index):
    if letter not in excluded_indices:
        excluded_indices[letter] = []

    if index not in excluded_indices[letter]:
        excluded_indices[letter].append(index)


def add_allowed_letter(letter):
    if letter not in letters:
        letters.append(letter)


def analyze_data(input_word, data):
    for i in range(0, len(input_word)):
        if data[i] == '0':
            found_legal_occurence = False
            max_occurences[input_word[i]] = 0

            for j in range(0, word_length):
                if input_word[j] == input_word[i] and data[j] != '0':
                    found_legal_occurence = True
                    add_excluded_index(input_word[i], i)
                    max_occurences[input_word[i]] += 1

            if not found_legal_occurence:
                max_occurences.pop(input_word[i])

                if input_word[i] not in excluded_letters:
                    excluded_letters.append(input_word[i])

        elif data[i] == '1':
            add_excluded_index(input_word[i], i)
            add_allowed_letter(input_word[i])

        elif data[i] == '2':
            word_frame[i] = input_word[i]
            add_allowed_letter(input_word[i])


def calculate_min_occurences(input_word, data):
    checked_letters = []
    for i in range(word_length):
        datum = data[i]
        letter = input_word[i]
        if datum == '1' and letter not in checked_letters:
            min_occurences[letter] = 0
            for j in range(word_length):
                if input_word[j] == letter and data[j] != '0':
                    min_occurences[letter] += 1
            checked_letters.append(letter)


def count_occurences(letter, word):
    occurences = 0
    for character in word:
        if character == letter:
            occurences +=1

    return occurences


def test_word(word):
    for char, indices in excluded_indices.items():
        if char in word:
            for index in indices:
                if word[index] == char:
                    return False

    for letter in excluded_letters:
        if letter in word:
            return False

    for letter in letters:
        if letter not in word:
            return False

    for i in range(0, word_length):
        letter = word_frame[i]
        if letter != '' and word[i] != letter:
            return False

    for letter in max_occurences.keys():
        if count_occurences(letter, word) > max_occurences[letter]:
            return False

    for letter in min_occurences.keys():
        if count_occurences(letter, word) < min_occurences[letter]:
            return False

    return True


def gather_candidates():
    candidate_words = []
    for word in words:
        if test_word(word) and word not in candidate_words:
            candidate_words.append(word)

    return candidate_words


def make_guess():
    global word_length
    global word_frame

    result = input('Enter word and results: ')
    if result.strip().lower() == 'exit':
        return True
    elif result.strip().lower() == 'reset':
        reset()
        return False

    results_split = result.split(' ')
    if len(results_split) != 2:
        print('Invalid results! Input the word you guessed and the results for each letter.')
        return False

    input_word = results_split[0]
    data = results_split[1]

    if len(input_word) != len(data):
        print('Input word and results are of different lengths!')
        return False
    elif loaded_words and (len(input_word) != word_length or len(data) != word_length):
        print(f'Need a word with {word_length} letters!')
        return False

    for entry in data:
        if entry != '0' and entry != '1' and entry != '2':
            print(f"Invalid results! '{entry}' is not a valid result")
            return False

    if not loaded_words:
        word_length = len(input_word)
        word_frame = ['' for i in range(0, word_length)]
        load_words()

    analyze_data(input_word, data)

    calculate_min_occurences(input_word, data)

    print(gather_candidates())

    return False


if __name__ == '__main__':
    debug = len(sys.argv) > 1 and sys.argv[1] == '-d'
    exit = False
    while not exit:
        exit = make_guess()
        print()
        if debug:
            print(f'letters: {letters}')
            print(f'excluded_letters: {excluded_letters}')
            print(f'excluded_indices: {excluded_indices}')
            print(f'max_occurences: {max_occurences}')
            print(f'min_occurences: {min_occurences}')
            print(f'word_frame: {word_frame}')
            print()