import random
import time
from typing import Callable

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import (
    REWARDS_HOMEPAGE,
    SEARCH_BETWEEN_MAX,
    SEARCH_BETWEEN_MIN,
    SEARCH_LONG_PAUSE_EVERY,
    SEARCH_LONG_PAUSE_MAX,
    SEARCH_LONG_PAUSE_MIN,
    SEARCH_RESULTS_READ_MAX,
    SEARCH_RESULTS_READ_MIN,
)
from src.search.dashboard_data import SearchProgress, parse_search_progress

_SEARCH_BOX_SELECTOR = "#rewards-suggestedSearch-searchbox"
_SEARCH_ICON_SELECTOR = ".rewards_searchboxForm .icon"
_PROGRESS_POLL_ATTEMPTS = 6
_PROGRESS_POLL_INTERVAL = (2.0, 4.0)


def _sleep(lo: float, hi: float) -> None:
    time.sleep(random.uniform(lo, hi))


def _between_searches_pause() -> None:
    """Gap before starting the next search — like a person pausing between queries."""
    _sleep(SEARCH_BETWEEN_MIN, SEARCH_BETWEEN_MAX)


def _results_reading_pause() -> None:
    """Dwell on the Bing results page as if skimming answers."""
    _sleep(SEARCH_RESULTS_READ_MIN, SEARCH_RESULTS_READ_MAX)


def _maybe_long_pause(search_index: int) -> None:
    """Occasionally take a longer break so the session doesn't look machine-timed."""
    if search_index <= 1 or search_index % SEARCH_LONG_PAUSE_EVERY != 0:
        return
    duration = random.uniform(SEARCH_LONG_PAUSE_MIN, SEARCH_LONG_PAUSE_MAX)
    mins, secs = divmod(int(duration), 60)
    label = f"{mins}m {secs}s" if mins else f"{secs}s"
    print(f"        …  Long pause ({label}) before next search")
    time.sleep(duration)


def _type_query(element, query: str) -> None:
    element.clear()
    _sleep(0.2, 0.6)
    for char in query:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.18))


def _scroll_results(driver: WebDriver) -> None:
    total = random.randint(200, 500)
    scrolled = 0
    while scrolled < total:
        step = random.randint(50, 150)
        driver.execute_script(f"window.scrollBy(0, {step});")
        scrolled += step
        _sleep(0.1, 0.35)
    if random.random() < 0.35:
        driver.execute_script(f"window.scrollBy(0, -{random.randint(40, 120)});")
        _sleep(0.3, 0.8)


def _read_progress(driver: WebDriver) -> SearchProgress | None:
    return parse_search_progress(driver.page_source)


def _wait_for_progress_increase(
    driver: WebDriver,
    before: SearchProgress,
) -> int:
    """Poll the rewards page until desktop search points increase. Returns delta."""
    for _ in range(_PROGRESS_POLL_ATTEMPTS):
        _sleep(*_PROGRESS_POLL_INTERVAL)
        driver.get(REWARDS_HOMEPAGE)
        _sleep(2.0, 4.0)
        after = _read_progress(driver)
        if after is not None and after.points_earned > before.points_earned:
            return after.points_earned - before.points_earned
    return 0


def _submit_search(driver: WebDriver, query: str) -> None:
    wait = WebDriverWait(driver, 15)
    search_box = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, _SEARCH_BOX_SELECTOR))
    )
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        search_box,
    )
    _sleep(0.4, 1.2)
    _type_query(search_box, query)
    _sleep(0.3, 1.0)
    search_box.send_keys(Keys.RETURN)
    _sleep(2.5, 5.5)

    if "bing.com" not in driver.current_url:
        try:
            icon = driver.find_element(By.CSS_SELECTOR, _SEARCH_ICON_SELECTOR)
            icon.click()
            _sleep(2.5, 5.5)
        except Exception:
            pass

    if "bing.com" in driver.current_url:
        _scroll_results(driver)
        _results_reading_pause()


def run_desktop_searches(
    driver: WebDriver,
    queries: list[str],
    *,
    on_before_search: Callable[[int, int, str], None] | None = None,
    on_after_search: Callable[[int, str, int], None] | None = None,
) -> int:
    """
    Run desktop Bing searches via the rewards dashboard textbox.

    Returns the number of searches actually performed.
    Stops early if the daily desktop search cap is already reached.
    """
    if not queries:
        return 0

    driver.get(REWARDS_HOMEPAGE)
    _sleep(3.0, 6.0)

    progress = _read_progress(driver)
    if progress is None:
        print("        ⚠  Could not read search progress — skipping searches.")
        return 0

    if progress.complete or progress.remaining_points <= 0:
        print(f"        Search cap already reached ({progress}).")
        return 0

    print(f"        Search progress: {progress}")
    performed = 0

    for index, query in enumerate(queries, start=1):
        if index > 1:
            _between_searches_pause()
            _maybe_long_pause(index)

        progress = _read_progress(driver)
        if progress is None:
            print("        ⚠  Lost search progress — stopping.")
            break
        if progress.complete or progress.remaining_points <= 0:
            print(f"        Daily search cap reached ({progress}).")
            break

        if on_before_search:
            on_before_search(index, len(queries), query)

        try:
            _submit_search(driver, query)
        except TimeoutException:
            print(f"        ✗  Search box not found for: {query!r}")
            driver.get(REWARDS_HOMEPAGE)
            _sleep(2.0, 4.0)
            continue
        except Exception as exc:
            print(f"        ✗  Search failed for {query!r}: {exc}")
            driver.get(REWARDS_HOMEPAGE)
            _sleep(2.0, 4.0)
            continue

        gained = _wait_for_progress_increase(driver, progress)
        performed += 1

        if on_after_search:
            on_after_search(index, query, gained)
        elif gained:
            print(f"        ●  [{index}/{len(queries)}] {query!r}  (+{gained} pts)")
        else:
            print(f"        ○  [{index}/{len(queries)}] {query!r}  (no points yet)")

    return performed
