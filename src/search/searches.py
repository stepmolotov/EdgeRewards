import time

from injector import Injector

from config import PROFILES, N_DESKTOP_SEARCHES, N_MOBILE_SEARCHES, SLEEP_TIME
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
        # injector = Injector()
        # session = injector.get(WebSession)
        session = WebSession(profile=profile, headless=False)
        details = session.get_details()
        print(details)

        # wip clicks and stuff
        # cards = session.get_available_cards()
        # session.print_cards(cards)
        # session.collect_cards(cards)
        # time.sleep(10 * SLEEP_TIME)
        # session.quit()

        session.search(words=desktop_search_words, is_mobile=False)
        session.search(words=mobile_search_words, is_mobile=True)
