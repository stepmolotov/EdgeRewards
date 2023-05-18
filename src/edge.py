from typing import List

from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time

from tqdm.auto import tqdm

from config import PROFILES, N_DESKTOP_SEARCHES, N_MOBILE_SEARCHES, EDGE_EXE_PATH, \
    EDGE_USER_DATA_PATH, BING_SEARCH_LINK, SLEEP_TIME
from src.helpers.print_progression import print_progression
from src.helpers.generate_words import generate_words
from src.helpers.kill_edge_process import kill_edge_processes


class SearchSession:
    def __init__(
        self,
        profile: str,
        is_mobile: bool
    ) -> None:
        self.__profile = profile
        self.__is_mobile = is_mobile
        self.__options = self.__options_setup()

    def __options_setup(self) -> Options:
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.binary_location = EDGE_EXE_PATH
        options.add_argument("user-data-dir=" + EDGE_USER_DATA_PATH)
        options.add_argument('--profile-directory=' + self.__profile)
        # options.add_argument("headless")
        # options.add_argument('--remote-debugging-port=' + str(PORT))
        if self.__is_mobile:
            mobile_emulation = {
                "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 "
                             "(KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        return options

    def run(self, words: List[str]) -> None:
        driver = webdriver.Edge(options=self.__options)
        prefix = f"[{self.__profile} - Mobile]" if self.__is_mobile else f"[{self.__profile} - Desktop]"
        with tqdm(words, total=len(words), position=0, leave=True) as pbar:
            for word in pbar:
                pbar.set_description(f"{prefix} Searched for: {word}")
                driver.get(BING_SEARCH_LINK + word)
                time.sleep(SLEEP_TIME)
                pbar.update()

        time.sleep(2 * SLEEP_TIME)
        driver.quit()



def do_searches() -> None:
    kill_edge_processes()
    for i, profile in enumerate(PROFILES):
        print("\n* Profile: " + profile + " [" + str(i + 1) + "/" + str(len(PROFILES)) + "]")
        # Generating random words
        desktop_search_words = generate_words(n_words=N_DESKTOP_SEARCHES)
        mobile_search_words = generate_words(n_words=N_MOBILE_SEARCHES)

        # Desktop Searches
        desktop = SearchSession(profile=profile, is_mobile=False)
        desktop.run(words=desktop_search_words)

        # Mobile Searches
        mobile = SearchSession(profile=profile, is_mobile=True)
        mobile.run(words=mobile_search_words)


if __name__ == '__main__':
    print("Starting process...")
    # run_searches()
    try:
        do_searches()
    except KeyboardInterrupt:
        print("\n\n ** Process interrupted by user. **\n")
        kill_edge_processes()
        exit()