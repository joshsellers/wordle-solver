import sys

word_length = 5
words = []

loaded_words = False
def load_words():
    with open('words_alpha.txt', 'r') as words_file:
        for line in words_file:
            if len(line.strip()) == word_length: words.append(line.strip())

    loaded_words = True


letters = []
excluded_letters = []
excluded_indices = {}
max_occurences = {}
min_occurences = {}

word_frame = []


def make_guess():
    global word_length
    global word_frame
    global letters
    global excluded_letters
    global excluded_indices
    global max_occurences
    global min_occurences
    global loaded_words
    global words

    result = input('Enter word and results: ')
    if result.strip().lower() == 'exit':
        return True
    elif result.strip().lower() == 'reset':
        word_length = 5
        words = []
        letters = []
        excluded_letters = []
        excluded_indices = {}
        max_occurences = {}
        min_occurences = {}
        word_frame = []
        return False

    input_word = result.split(' ')[0]
    if not loaded_words:
        word_length = len(input_word)
        load_words()
        word_frame = ['' for i in range(0, word_length)]

    data = result.split(' ')[1]

    for i in range(0, len(input_word)):
        if data[i] == '0':
            if input_word[i] not in letters:
                excluded_letters.append(input_word[i])
            else:
                if input_word[i] not in excluded_indices:
                    excluded_indices[input_word[i]] = []
                excluded_indices[input_word[i]].append(i)

                max_occurences[input_word[i]] = 0
                for j in range(0, len(input_word)):
                    if input_word[j] == input_word[i] and data[j] != '0':
                        max_occurences[input_word[i]] += 1

        elif data[i] == '1':
            if input_word[i] not in excluded_indices:
                excluded_indices[input_word[i]] = []
            excluded_indices[input_word[i]].append(i)
            letters.append(input_word[i])

            if input_word[i] in excluded_letters:
                excluded_letters.pop(excluded_letters.index(input_word[i]))

        elif data[i] == '2':
            word_frame[i] = input_word[i]
            letters.append(input_word[i])

            if input_word[i] in excluded_letters:
                excluded_letters.pop(excluded_letters.index(input_word[i]))

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
            occurences = 0
            for character in word:
                if character == letter:
                    occurences += 1

            if occurences > max_occurences[letter]:
                return False

        for letter in min_occurences.keys():
            occurences = 0
            for character in word:
                if character == letter:
                    occurences += 1

            if occurences < min_occurences[letter]:
                return False

        return True

    candidate_words = []
    for word in words:
        if test_word(word) and word not in candidate_words:
            candidate_words.append(word)

    print(candidate_words)

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