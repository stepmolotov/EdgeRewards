import time

from bs4 import BeautifulSoup
from selenium.webdriver.edge.webdriver import WebDriver

from config import REWARDS_HOMEPAGE, SLEEP_TIME
from src.helpers.string_remove_space_newline import string_remove_space_newline
from src.search.homepage_data import HomepageData


class CrawlerService:
    def __init__(self, driver: WebDriver) -> None:
        # TODO fill with info
        self.__max_retries = 3
        self.__driver = driver
        self.__homepage_soup = self.__get_homepage_soup(download_page=False)

    def __get_homepage_soup(self, download_page: bool = False) -> BeautifulSoup:
        self.__driver.get(REWARDS_HOMEPAGE)
        time.sleep(3 * SLEEP_TIME)
        page_source = self.__driver.page_source
        if download_page:
            self.__download_page_source()
        soup = BeautifulSoup(page_source, "html5lib")
        return soup

    def __get_homepage_data(self) -> HomepageData:
        """
        Get the points from the homepage.
        :param page_source: The page source of the Microsoft Rewards homepage.
        :return: HomepageData with the username, the total points, the daily points and the streak.
        """

        # get the banner items: [Name, Points, --Donations--, Daily, Streak]
        data = HomepageData()
        banner_items = self.__homepage_soup.find_all(
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

    def __download_page_source(self) -> None:
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(self.__driver.page_source)

    def get_available_cards(self) -> None:
        cards_items = self.__homepage_soup.find_all(
            "mee-rewards-daily-set-item-content", class_="ng-isolate-scope"
        )
        print(f"Found {len(cards_items)} cards")
        for card in cards_items:
            description = card.find("h3", class_="c-heading ellipsis ng-binding")
            if description:
                print(description.get_text())

    def get_details(self) -> HomepageData:
        tries = 1
        homepage_data = HomepageData()

        while tries <= 3:
            try:
                homepage_data = self.__get_homepage_data()
                return homepage_data
            except Exception:
                print(
                    f"[{tries}/{self.__max_retries}] Error while loading {REWARDS_HOMEPAGE}"
                )
                tries += 1
                time.sleep(3 * SLEEP_TIME)
        return homepage_data
