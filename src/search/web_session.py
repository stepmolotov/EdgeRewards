from typing import List

from injector import inject
from selenium import webdriver
from selenium.webdriver.edge.options import Options

from config import (
    EDGE_EXE_PATH,
    EDGE_USER_DATA_PATH,
)
from src.search.homepage_data import HomepageData
from src.services.crawler_service import CrawlerService
from src.services.search_service import SearchService


@inject
class WebSession:
    def __init__(
            self,
            profile: str,
            headless: bool,
            crawler: CrawlerService,
            search: SearchService
    ) -> None:
        self.__profile = profile
        self.__headless = headless
        self.__crawler = crawler
        self.__search = search
        self.__options = self.__options_setup()
        self.__driver = webdriver.Edge(options=self.__options)

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
        return self.__crawler.get_details(driver=self.__driver)
