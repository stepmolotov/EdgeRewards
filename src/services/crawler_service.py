import json
import time
from typing import Any, List

from bs4 import BeautifulSoup
from injector import inject
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.webdriver import WebDriver

from config import REWARDS_HOMEPAGE, SLEEP_TIME
from src.card import Card
from src.card_type_enum import CardTypeEnumeration
from src.helpers.string_remove_space_newline import string_remove_space_newline
from src.helpers.xpath_finder import xpath_finder
from src.search.homepage_data import HomepageData
import itertools


@inject
class CrawlerService:
    def __init__(self, driver: WebDriver) -> None:
        self.__max_retries = 3
        self.__driver = driver
        self.__homepage_soup = self.__get_homepage_soup(download_page=True)

    def __get_homepage_soup(self, download_page: bool = False) -> BeautifulSoup:
        try:
            time.sleep(2 * SLEEP_TIME)
            self.__driver.get(REWARDS_HOMEPAGE)
            time.sleep(3 * SLEEP_TIME)
            page_source = self.__driver.page_source
            if download_page:
                self.__download_page_source()
            soup = BeautifulSoup(page_source, "html5lib")
        except Exception as e:
            print(e)
            soup = BeautifulSoup("", "html5lib")
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

    def get_detailed_cards(self) -> List[Card]:
        cards: List[Card] = []
        cards_items = self.__homepage_soup.find_all("div", class_="c-card-content")
        print(f"cards_items: {len(cards_items)}")
        for card_item in cards_items:
            points = card_item.find("div", class_="points clearfix")
            if not points:
                continue
            points_quantity = points.find(
                "span", class_="c-heading pointsString ng-binding ng-scope"
            )
            if not points_quantity:
                continue
            points_quantity_val = string_remove_space_newline(
                points.find(
                    "span", class_="c-heading pointsString ng-binding ng-scope"
                ).get_text()
            )
            already_collected = points.find(
                "span", class_="mee-icon mee-icon-SkypeCircleCheck"
            )
            daily_description = card_item.find(
                "h3", class_="c-heading ellipsis ng-binding"
            )
            general_description = card_item.find("h3", class_="c-heading ng-binding")
            description_item = (
                daily_description
                if daily_description
                else general_description
            )
            description = description_item.get_text()
            points_val = int(points_quantity_val)
            is_daily = daily_description is not None
            already_collected = already_collected is not None
            if points_val <= 10:
                if CardTypeEnumeration.poll.value in str(description).lower():
                    card_type = CardTypeEnumeration.poll
                else:
                    card_type = CardTypeEnumeration.click
            else:
                card_type = CardTypeEnumeration.quiz
            card = Card(
                description=description,
                points=points_val,
                is_daily=is_daily,
                already_collected=already_collected,
                type=card_type,
                soup=description_item,
            )
            cards.append(card)
        return cards

    def print_cards(self, cards: List[Card]) -> None:
        print(f"cards: {len(cards)}")
        for card in cards:
            print(card)

    def elaborate_cards(self, cards: List[Card]) -> None:
        print(f"cards: {len(cards)}")
        for card in cards:
            if (
                    card.type == CardTypeEnumeration.click
                    and card.is_daily
                    and not card.already_collected
            ):
                xpath = xpath_finder(card.soup)
                print(xpath)
                time.sleep(2 * SLEEP_TIME)
                self.__driver.find_element(by=By.XPATH, value=xpath).click()
                time.sleep(2 * SLEEP_TIME)
                print(f"Clicked on: {card.description} [{card.points} points]")

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

    def find_all_cards(self) -> None:
        all_cards = self.__driver.find_elements(By.CLASS_NAME, "rewards-card-container")
        # print(all_cards)
        for card in all_cards:
            data_m = card.get_attribute("data-m")
            if data_m:
                print(data_m)
                print(json.loads(data_m).keys())
