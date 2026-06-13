import random

from config import (
    SEARCH_COUNT_MAX,
    SEARCH_COUNT_MIN,
    SEARCH_PHRASE_CHANCE,
    SEARCH_QUERY_MIN_LENGTH,
    SEARCH_USE_PHRASES,
    WORD_LIST_PATH,
)
from src.helpers.generate_words import generate_words

_PHRASE_TEMPLATES: list[str] = [
    "come {word}",
    "{word} ricetta",
    "{word} significato",
    "migliori {word}",
    "cosa significa {word}",
]


def _maybe_enrich(word: str) -> str:
    if not SEARCH_USE_PHRASES or random.random() > SEARCH_PHRASE_CHANCE:
        return word
    template = random.choice(_PHRASE_TEMPLATES)
    return template.format(word=word)


def generate_search_queries() -> list[str]:
    """
    Pick a random daily search count and build queries from the Italian word list.
    Some queries are lightly enriched so they read more like natural Bing searches.
    """
    count = random.randint(SEARCH_COUNT_MIN, SEARCH_COUNT_MAX)
    words = generate_words(
        n_words=count,
        min_length=SEARCH_QUERY_MIN_LENGTH,
        file_path=WORD_LIST_PATH,
    )
    return [_maybe_enrich(word) for word in words]
