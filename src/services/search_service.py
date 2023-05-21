import time
from typing import List

from injector import inject
from selenium.webdriver.edge.webdriver import WebDriver
from tqdm import tqdm

from config import BING_SEARCH_LINK, SLEEP_TIME


@inject
class SearchService:

    def __init__(self) -> None:
        # TODO fill with info
        pass

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
                time.sleep(2 * SLEEP_TIME)
                pbar.update()

        time.sleep(2 * SLEEP_TIME)
