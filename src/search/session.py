import time
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from tqdm import tqdm

from config import (
    EDGE_EXE_PATH,
    EDGE_USER_DATA_PATH,
    BING_SEARCH_LINK,
    SLEEP_TIME,
    REWARDS_HOMEPAGE,
)
from src.helpers.string_remove_space_newline import string_remove_space_newline
from src.search.homepage_data import HomepageData


class SearchSession:
    def __init__(self, profile: str) -> None:
        self.__profile = profile
        self.__options = self.__options_setup()
        self.__driver = webdriver.Edge(options=self.__options)

    def __options_setup(self) -> Options:
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.binary_location = EDGE_EXE_PATH
        options.add_argument("user-data-dir=" + EDGE_USER_DATA_PATH)
        options.add_argument("--profile-directory=" + self.__profile)
        # options.add_argument("headless")
        # options.add_argument('--remote-debugging-port=' + str(PORT))
        return options

    def __add_mobile_options(self) -> None:
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 "
            "(KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
        }
        self.__options.add_experimental_option("mobileEmulation", mobile_emulation)

    @staticmethod
    def __get_homepage_data(page_source: str) -> HomepageData:
        """
        Get the points from the homepage.
        :param page_source: The page source of the Microsoft Rewards homepage.
        :return: HomepageData with the username, the total points, the daily points and the streak.
        """
        soup = BeautifulSoup(page_source, "html5lib")

        # get the banner items: [Name, Points, --Donations--, Daily, Streak]
        data = HomepageData()
        banner_items = soup.find_all(
            "mee-rewards-user-status-banner-item", class_="ng-isolate-scope"
        )
        if len(banner_items) == 5:
            username = banner_items[0].find(
                "h1", class_="c-heading-2 ellipsis ng-binding c-heading"
            )
            points = banner_items[1].find(
                "p", class_="bold pointsValue margin-top-1 ellipsis"
            )
            daily = banner_items[3].find(
                "p", class_="bold pointsValue margin-top-1 ellipsis"
            )
            streak = banner_items[4].find(
                "p", class_="bold pointsValue margin-top-1 ellipsis"
            )
            if username and points and daily and streak:
                data.username = string_remove_space_newline(
                    username.get_text().split(" ")[-1]
                )
                data.points = int(string_remove_space_newline(points.get_text()))
                data.daily = int(string_remove_space_newline(daily.get_text()))
                data.streak = int(string_remove_space_newline(streak.get_text()))
        else:
            print("Error while getting soup elements")
        return data

    def get_details(self) -> HomepageData:
        tries = 1
        max_tries = 3
        homepage_data = HomepageData()

        while tries <= 3:
            try:
                self.__driver.get(REWARDS_HOMEPAGE)
                time.sleep(3 * SLEEP_TIME)
                page_source = self.__driver.page_source
                homepage_data = SearchSession.__get_homepage_data(page_source)
                return homepage_data
            except Exception:
                print(f"[{tries}/{max_tries}] Error while loading {REWARDS_HOMEPAGE}")
                tries += 1
                time.sleep(3 * SLEEP_TIME)
        return homepage_data

    def run(self, words: List[str], is_mobile: bool = False) -> None:
        prefix = (
            f"[{self.__profile} - Mobile]"
            if is_mobile
            else f"[{self.__profile} - Desktop]"
        )
        if is_mobile:
            self.__add_mobile_options()
        with tqdm(words, total=len(words), position=0, leave=True) as pbar:
            for word in pbar:
                pbar.set_description(f"{prefix} Searched for: {word}")
                self.__driver.get(BING_SEARCH_LINK + word)
                time.sleep(2 * SLEEP_TIME)
                pbar.update()

        time.sleep(2 * SLEEP_TIME)
        self.__driver.quit()
