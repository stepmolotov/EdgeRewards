from config import PROFILES, N_DESKTOP_SEARCHES, N_MOBILE_SEARCHES
from src.edge import SearchSession
from src.helpers.generate_words import generate_words
from src.helpers.kill_edge_process import kill_edge_processes


def do_searches() -> None:
    kill_edge_processes()
    for i, profile in enumerate(PROFILES):
        print(
            "\n* Profile: "
            + profile
            + " ["
            + str(i + 1)
            + "/"
            + str(len(PROFILES))
            + "]"
        )
        # Generating random words
        desktop_search_words = generate_words(n_words=N_DESKTOP_SEARCHES)
        mobile_search_words = generate_words(n_words=N_MOBILE_SEARCHES)

        # Desktop Searches
        desktop = SearchSession(profile=profile, is_mobile=False)
        desktop.run(words=desktop_search_words)

        # Mobile Searches
        mobile = SearchSession(profile=profile, is_mobile=True)
        mobile.run(words=mobile_search_words)
