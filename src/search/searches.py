from config import PROFILES, N_DESKTOP_SEARCHES, N_MOBILE_SEARCHES
from src.search.session import SearchSession
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
        session = SearchSession(profile=profile, headless=True)
        details = session.get_details()
        print(details)
        session.run(words=desktop_search_words, is_mobile=False)
        session.run(words=mobile_search_words, is_mobile=True)
