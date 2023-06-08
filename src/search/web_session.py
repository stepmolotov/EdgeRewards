from typing import List

from selenium import webdriver
from selenium.webdriver.edge.options import Options

from config import (
    EDGE_EXE_PATH,
    EDGE_USER_DATA_PATH,
)
from src.card import Card
from src.search.homepage_data import HomepageData
from src.services.card_dealer_service import CardDealerService
from src.services.crawler_service import CrawlerService
from src.services.search_service import SearchService


class WebSession:
    def __init__(
        self,
        profile: str,
        headless: bool,
        # crawler: CrawlerService,
        # search: SearchService
        # card_dealer: CardDealverService,
    ) -> None:
        self.__profile = profile
        self.__headless = headless
        self.__options = self.__options_setup()
        self.__driver = webdriver.Edge(options=self.__options)
        self.__crawler = CrawlerService(driver=self.__driver)
        self.__search = SearchService(profile=self.__profile)
        self.__card_dealer = CardDealerService(driver=self.__driver)

    def __options_setup(self) -> Options:
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.binary_location = EDGE_EXE_PATH
        options.add_argument("user-data-dir=" + EDGE_USER_DATA_PATH)
        options.add_argument("--profile-directory=" + self.__profile)

        if self.__headless:
            options.add_argument("headless")
        # options.add_argument('--remote-debugging-port=' + str(PORT))
        return options

    def __add_mobile_options(self) -> None:
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 "
            "(KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
        }
        self.__options.add_experimental_option("mobileEmulation", mobile_emulation)
        self.__driver = webdriver.Edge(options=self.__options)

    def search(self, words: List[str], is_mobile: bool = False) -> None:
        if is_mobile:
            self.__add_mobile_options()
        self.__search.run(driver=self.__driver, words=words, is_mobile=is_mobile)
        self.__driver.quit()

    def get_details(self) -> HomepageData:
        return self.__crawler.get_details()

    def get_available_cards(self) -> List[Card]:
        cards = self.__crawler.get_detailed_cards()
        return cards

    def collect_cards(self, cards: List[Card]) -> None:
        self.__card_dealer.run(cards)

    def print_cards(self, cards: List[Card]) -> None:
        self.__crawler.print_cards(cards)

    def quit(self) -> None:
        self.__driver.quit()
