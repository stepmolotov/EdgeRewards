import random
import time
from datetime import datetime
from typing import List

from injector import inject
from selenium.webdriver.edge.webdriver import WebDriver
from tqdm import tqdm

from config import BING_SEARCH_LINK, SLEEP_TIME, BING_UPDATED_SEARCH_LINK, QUERY_PLACEHOLDER


@inject
class SearchService:
    def __init__(self, profile: str) -> None:
        self.__profile = profile

    def run(self, driver: WebDriver, words: List[str], is_mobile: bool = False) -> None:
        prefix = (
            f"[{self.__profile} - Mobile]"
            if is_mobile
            else f"[{self.__profile} - Desktop]"
        )
        counter = 0
        with tqdm(words, total=len(words), position=0, leave=True) as pbar:
            for word in pbar:
                pbar.set_description(f"{prefix} Searched for: {word}")
                driver.get(self.__get_search_url(query=word))
                counter += 1
                if counter % 4 == 0:
                    time = datetime.now().strftime("%H:%M:%S")
                    print(f"[WAIT {time}] Long sleep for 15-17 minutes.")
                    self.long_sleep()
                else:
                    self.random_sleep()
                pbar.update()

        self.random_sleep()

    def __get_search_url(self, query: str) -> str:
        # return BING_SEARCH_LINK + query
        return BING_UPDATED_SEARCH_LINK.replace(QUERY_PLACEHOLDER, query)

    @staticmethod
    def random_sleep() -> None:
        random_value = random.uniform(1.0, 5.0)
        time.sleep(random_value * SLEEP_TIME)

    @staticmethod
    def long_sleep() -> None:
        random_value = random.uniform(15*60, 17*60)
        time.sleep(random_value * SLEEP_TIME)
