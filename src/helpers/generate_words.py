import random
import string
from typing import List, Optional

from config import WORD_LENGTH


def generate_words(
    n_words: int = 10, min_length: int = 4, file_path: Optional[str] = None
) -> List[str]:
    if file_path:
        return generate_words_from_file(
            file_path=file_path, n_words=n_words, min_length=min_length
        )
    else:
        return generate_random_chars(n_words=n_words, length=min_length)


def generate_random_chars(n_words: int = 10, length: int = WORD_LENGTH) -> List[str]:
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


def generate_words_from_file(
    file_path: str, n_words: int = 10, min_length: int = 4
) -> List[str]:
    """
    Generate random words from a file.
    :param min_length: Minimum length of each word.
    :param n_words: Number of words to generate.
    :param file_path: Path of the file containing the words.
    :return: List of strings.
    """
    words: List[str] = []
    try:
        # read all the words in one go
        with open(file_path, "r", encoding="utf-8") as file:
            words = file.read().splitlines()
        long_words = [word for word in words if len(word) >= min_length]
        words = random.sample(long_words, n_words)
    except Exception as e:
        print(f"[GEN] Could not read words list: {e}")
    return words
