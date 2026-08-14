import sys
import os
from pathlib import Path
import random
import time

loaded_words = False

word_length = 5
words = []

letters = []
excluded_letters = []
excluded_indices = {}
max_occurences = {}
min_occurences = {}

word_frame = []

non_words = []

wordle_allowed_words = []

training_mode = False
answer = ''
guess_round = 0


def reset():
    global letters
    global excluded_letters
    global excluded_indices
    global max_occurences
    global min_occurences
    global loaded_words
    global words
    global non_words
    global word_frame
    global word_length
    global wordle_allowed_words
    global guess_round

    loaded_words = False
    word_length = 5
    letters = []
    excluded_letters = []
    excluded_indices = {}
    max_occurences = {}
    min_occurences = {}
    word_frame = []
    guess_round = 0

    if not training_mode:
        non_words = []
        wordle_allowed_words = []
        words = []

    print('Reset memory')


def load_words():
    global loaded_words

    base_path = f'{os.path.realpath(os.path.dirname(__file__))}/'

    with open(f'{base_path}words_alpha.txt', 'r') as words_file:
        for line in words_file:
            if len(line.strip()) == word_length: 
                words.append(line.strip())

    non_words_path = f'{base_path}non_words.txt'
    if Path(non_words_path).exists():
        with open(non_words_path, 'r') as non_words_file:
            for line in non_words_file:
                line_replaced = line
                if '$' in line_replaced:
                    line_replaced = line.replace('$', '')
                if len(line_replaced.strip()) == word_length:
                    non_words.append(line_replaced.strip())

    if training_mode:
        with open(f'{base_path}wordle-allowed-guesses.txt', 'r') as wordle_file:
            for line in wordle_file:
                wordle_allowed_words.append(line.strip())

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


def process_user_guess():
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


def add_non_word(word):
    non_words.append(word)
    with open(f'{os.path.realpath(os.path.dirname(__file__))}/non_words.txt', 'a') as non_words_file:
        non_words_file.write(f'{word}\n')


def auto_play():
    global word_length
    global word_frame

    if not loaded_words:
        word_length = int(input('Enter word length: '))
        print()
        word_frame = ['' for i in range(0, word_length)]
        load_words()

    candidates = gather_candidates()
    for non_word in non_words:
        if non_word in candidates:
            candidates.pop(candidates.index(non_word))

    if not candidates:
        print('Ran out of guesses!')
        return False

    guess = random.choice(candidates)
    print(f'Guess: {guess} ({len(candidates)} possible word' + ('s)' if len(candidates) != 1 else ')'))

    result = input('Enter results: ')

    if result.strip().lower() == 'exit':
        return True
    elif result.strip().lower() == 'reset':
        reset()
        return False
    elif result.strip().lower() == 'nonword':
        add_non_word(guess)
        return False

    if len(result) != word_length:
        print(f'Need results with {word_length} numbers!')
        return False

    for entry in result:
        if entry != '0' and entry != '1' and entry != '2':
            print(f"Invalid results! '{entry}' is not a valid result")
            return False

    analyze_data(guess, result)

    calculate_min_occurences(guess, result)

    return False


def train():
    global word_length
    global word_frame
    global answer
    global guess_round
    global loaded_words

    word_length = 5

    max_rounds = 6

    if guess_round == max_rounds:
        print(f'Failed! Answer was {answer}')
        reset()
        return False

    if not loaded_words:
        word_frame = ['' for i in range(0, word_length)]
        answer = random.choice(wordle_allowed_words)
        loaded_words = True

    candidates = gather_candidates()
    for non_word in non_words:
        if non_word in candidates:
            candidates.pop(candidates.index(non_word))

    if not candidates:
        print(f'Ran out of candidates! Answer was: {answer}')
        input('Press enter to exit: ')
        return True

    guess = random.choice(candidates)
    print(f'Guess: {guess} ({len(candidates)} possible word' + ('s)' if len(candidates) != 1 else ')'))

    if guess == answer:
        print(f'Solved in {guess_round + 1} guess' + ('es' if guess_round != 1 else '!'))
        reset()
        return False

    if guess not in wordle_allowed_words:
        print('Word not allowed!')
        add_non_word(f'{guess}$')
        return False

    results = ''
    for i in range(0, word_length):
        guess_letter = guess[i]
        answer_letter = answer[i]

        if guess_letter == answer_letter:
            results += '2'
        elif guess_letter not in answer:
            results += '0'
        elif guess_letter in answer:
            count_answer = 0
            for j in range(0, word_length):
                if answer[j] == guess_letter and answer[j] != guess[j]:
                    count_answer += 1

            count_guess = 0
            for j in range(0, i):
                if guess[j] == guess_letter:
                    count_guess += 1

            if count_guess < count_answer:
                results += '1'
            else:
                results += '0'

    print(f'Results: {results}')

    analyze_data(guess, results)

    calculate_min_occurences(guess, results)

    guess_round += 1

    time.sleep(1)

    return False


def print_debug():
    if debug:
        print(f'letters: {letters}')
        print(f'excluded_letters: {excluded_letters}')
        print(f'excluded_indices: {excluded_indices}')
        print(f'max_occurences: {max_occurences}')
        print(f'min_occurences: {min_occurences}')
        print(f'word_frame: {word_frame}')
        print()


if __name__ == '__main__':
    load_words()
    print(non_words)
    exit()


    debug = len(sys.argv) > 1 and sys.argv[1] == '-d' or len(sys.argv) > 2 and (sys.argv[1] == '-d' or sys.argv[2] == '-d')

    full_play_mode = len(sys.argv) > 2 and (sys.argv[1] == '-fp' or sys.argv[2] == '-fp') or len(sys.argv) > 1 and sys.argv[1] == '-fp'

    training_mode = len(sys.argv) > 1 and sys.argv[1] == '-t'
    if training_mode:
        debug = True
        load_words()
        loaded_words = False

    exit = False

    while not exit:
        if full_play_mode:
            exit = auto_play()
        elif training_mode:
            exit = train()
        else:
            exit = process_user_guess()

        print()
        print_debug()

        