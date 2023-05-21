from injector import Injector

from config import PROFILES, N_DESKTOP_SEARCHES, N_MOBILE_SEARCHES
from src.search.web_session import WebSession
from src.helpers.generate_words import generate_words
from src.helpers.kill_edge_process import kill_edge_processes


def run_searches() -> None:
    kill_edge_processes()
    for i, profile in enumerate(PROFILES):
        print(f"\n* Profile: {profile} [{i + 1}/{len(PROFILES)}]")
        # Generating random words
        desktop_search_words = generate_words(n_words=N_DESKTOP_SEARCHES)
        mobile_search_words = generate_words(n_words=N_MOBILE_SEARCHES)


        # Desktop and Mobile searches
        # session = WebSession(profile=profile, headless=True)
        session = Injector().get(WebSession)
        details = session.get_details()
        print(details)
        session.search(words=desktop_search_words, is_mobile=False)
        session.search(words=mobile_search_words, is_mobile=True)
