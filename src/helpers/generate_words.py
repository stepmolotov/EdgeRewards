import random
import string
from typing import List

from config import WORD_LENGTH


def generate_words(n_words: int = 10, length: int = WORD_LENGTH) -> List[str]:
    """
    Generate random words of given length.
    :param n_words:
    :param length:
    :return: List of strings.
    """
    words = []
    letters = string.ascii_lowercase
    for _ in range(n_words):
        random_word = "".join(random.choice(letters) for _ in range(length))
        words.append(random_word)
    return words
