import random
import time
from typing import List

from injector import inject
from selenium.webdriver.edge.webdriver import WebDriver
from tqdm import tqdm

from config import BING_SEARCH_LINK, SLEEP_TIME


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
        with tqdm(words, total=len(words), position=0, leave=True) as pbar:
            for word in pbar:
                pbar.set_description(f"{prefix} Searched for: {word}")
                driver.get(BING_SEARCH_LINK + word)
                self.random_sleep()
                pbar.update()

        self.random_sleep()

    @staticmethod
    def random_sleep() -> None:
        random_value = random.uniform(1.0, 5.0)
        time.sleep(random_value * SLEEP_TIME)
