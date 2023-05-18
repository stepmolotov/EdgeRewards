import random
import string
from typing import List

from config import WORD_LENGTH


def generate_words(n_words: int = 10, length: int = WORD_LENGTH) -> List[str]:
    # Generates a list of N words with chosen length
    words = []
    letters = string.ascii_lowercase
    for i in range(n_words):
        random_word = ''.join(random.choice(letters) for _ in range(length))
        words.append(random_word)
    # print('\t' + str(words))
    return words
