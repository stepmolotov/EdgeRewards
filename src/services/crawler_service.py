import time

from bs4 import BeautifulSoup
from injector import inject
from selenium.webdriver.edge.webdriver import WebDriver

from config import REWARDS_HOMEPAGE, SLEEP_TIME
from src.helpers.string_remove_space_newline import string_remove_space_newline
from src.search.homepage_data import HomepageData


@inject
class CrawlerService:

    def __init__(self) -> None:
        # TODO fill with info
        pass

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

    def get_details(self, driver: WebDriver) -> HomepageData:
        tries = 1
        max_tries = 3
        homepage_data = HomepageData()

        while tries <= 3:
            try:
                driver.get(REWARDS_HOMEPAGE)
                time.sleep(3 * SLEEP_TIME)
                page_source = self.__driver.page_source
                homepage_data = self.__get_homepage_data(page_source)
                return homepage_data
            except Exception:
                print(f"[{tries}/{max_tries}] Error while loading {REWARDS_HOMEPAGE}")
                tries += 1
                time.sleep(3 * SLEEP_TIME)
        return homepage_data

