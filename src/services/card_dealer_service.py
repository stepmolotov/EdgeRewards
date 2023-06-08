import time
from typing import List, Optional

from injector import inject
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from config import SLEEP_TIME
from src.card import Card
from src.card_type_enum import CardTypeEnumeration
from src.helpers.xpath_finder import xpath_finder


@inject
class CardDealerService:
    def __init__(self, driver: WebDriver) -> None:
        self.__driver = driver

    def __get_card_element(self, card: Card) -> Optional[WebElement]:
        xpath = xpath_finder(card.soup)
        element = self.__driver.find_element(by=By.XPATH, value=xpath)
        return element

    def __card_click(self, card: Card) -> None:
        element = self.__get_card_element(card)
        if element:
            element.click()

    def __card_poll(self, card: Card) -> None:
        element = self.__get_card_element(card)
        if not element:
            return
        element.click()
        time.sleep(3 * SLEEP_TIME)
        # always select first option
        self.__driver


    def __card_quiz(self, card: Card) -> None:
        pass

    def run(self, cards: List[Card]) -> None:
        '''
        Run through the list of Cards and collect the points.
        :param cards:
        :return:
        '''
        for card in cards:
            # if not card.is_daily:
            #     continue
            print(card)
            if card.type == CardTypeEnumeration.click:
                print('CLICK!')
                self.__card_click(card)
            elif card.type == CardTypeEnumeration.poll:
                self.__card_poll(card)
            elif card.type == CardTypeEnumeration.quiz:
                self.__card_quiz(card)
            else:
                raise Exception(f"Unknown card type: {card.type}")