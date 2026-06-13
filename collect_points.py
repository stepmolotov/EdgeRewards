"""
collect_points.py
-----------------
Visits Microsoft Rewards, collects all available daily click-type cards,
and reports the total points before and after the run.

Usage:
    python collect_points.py

Configuration is read from config.py (PROFILES, EDGE_EXE_PATH, etc.).
The script reuses your existing Edge profile so no login is required.
"""

import os
import random
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

from config import (
    EDGE_DRIVER_PATH,
    EDGE_EXE_PATH,
    EDGE_EXTRA_ARGS,
    EDGE_USER_DATA_PATH,
    PROFILES,
    REWARDS_HOMEPAGE,
)
from src.card import Card
from src.card_type_enum import CardTypeEnumeration
from src.helpers.kill_edge_process import kill_edge_processes
from src.helpers.string_remove_space_newline import string_remove_space_newline
from src.search.homepage_data import HomepageData

# ---------------------------------------------------------------------------
# Human-like timing helpers
# ---------------------------------------------------------------------------

def _sleep(lo: float, hi: float) -> None:
    """Sleep for a random duration between lo and hi seconds."""
    time.sleep(random.uniform(lo, hi))


def _short_pause() -> None:
    """Brief hesitation — like a human glancing at the screen."""
    _sleep(0.4, 1.2)


def _reading_pause() -> None:
    """Pause as if reading the page before doing anything."""
    _sleep(1.5, 4.0)


def _after_click_pause() -> None:
    """Wait after a click for the page to respond and settle."""
    _sleep(2.5, 5.5)


def _between_cards_pause() -> None:
    """Gap between collecting consecutive cards."""
    _sleep(3.0, 8.0)

# ---------------------------------------------------------------------------
# Driver helpers
# ---------------------------------------------------------------------------

def _make_driver(profile: str) -> webdriver.Edge:
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.binary_location = EDGE_EXE_PATH
    options.add_argument("user-data-dir=" + EDGE_USER_DATA_PATH)
    options.add_argument("--profile-directory=" + profile)
    # Extra args (e.g. --no-sandbox on Docker, --disable-dev-shm-usage)
    if EDGE_EXTRA_ARGS:
        for arg in EDGE_EXTRA_ARGS.split():
            options.add_argument(arg)
    # Never use headless — it has a distinct fingerprint that sites can detect

    # Prefer a pre-installed driver (set EDGE_DRIVER_PATH) over the
    # webdriver_manager download — that's what the Docker image does so we
    # don't depend on a network fetch at every run.
    if EDGE_DRIVER_PATH and os.path.exists(EDGE_DRIVER_PATH):
        service = Service(EDGE_DRIVER_PATH)
    else:
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(service=service, options=options)


def _patch_webdriver_flag(driver: webdriver.Edge) -> None:
    """
    Remove the navigator.webdriver JavaScript property that sites use to
    detect Selenium. Must be called before the first page load.
    """
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        },
    )


def _human_scroll(driver: webdriver.Edge) -> None:
    """
    Scroll the page in small, irregular steps — like a person skimming content.
    """
    total = random.randint(300, 700)
    scrolled = 0
    while scrolled < total:
        step = random.randint(60, 180)
        driver.execute_script(f"window.scrollBy(0, {step});")
        scrolled += step
        _sleep(0.1, 0.4)
    # Occasionally scroll back up a little, as humans do
    if random.random() < 0.4:
        driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 150)});")
        _sleep(0.3, 0.8)


def _fetch_soup(driver: webdriver.Edge, save_debug: bool = False) -> BeautifulSoup:
    """Navigate to the rewards homepage and return a BeautifulSoup of the page."""
    driver.get(REWARDS_HOMEPAGE)
    # Wait for the page to fully load (randomised so it's not a fixed interval)
    _sleep(4.0, 7.0)
    # Read the page as if scanning it before acting
    _human_scroll(driver)
    _reading_pause()
    if save_debug:
        _save_page_source(driver, "page_source_debug.html")
    return BeautifulSoup(driver.page_source, "html5lib")


def _save_page_source(driver: webdriver.Edge, filename: str = "page_source.html") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------

def _parse_points(soup: BeautifulSoup) -> HomepageData:
    """
    Read username, total points, daily points and streak from the page banner.
    Returns a HomepageData with None fields if parsing fails.
    """
    data = HomepageData()
    banner_items = soup.find_all(
        "mee-rewards-user-status-banner-item", class_="ng-isolate-scope"
    )
    if len(banner_items) < 5:
        print(f"    ⚠  Banner items found: {len(banner_items)} (expected 5). "
              "Page structure may have changed.")
        return data

    try:
        username_el = banner_items[0].find(
            "h1", class_="c-heading-2 ellipsis ng-binding c-heading"
        )
        points_el = banner_items[1].find(
            "p", class_="bold pointsValue margin-top-1 ellipsis"
        )
        daily_el = banner_items[3].find(
            "p", class_="bold pointsValue margin-top-1 ellipsis"
        )
        streak_el = banner_items[4].find(
            "p", class_="bold pointsValue margin-top-1 ellipsis"
        )

        if username_el and points_el and daily_el and streak_el:
            data.username = string_remove_space_newline(
                username_el.get_text().split(" ")[-1]
            )
            data.points = int(string_remove_space_newline(points_el.get_text()))
            data.daily  = int(string_remove_space_newline(daily_el.get_text()))
            data.streak = int(string_remove_space_newline(streak_el.get_text()))
        else:
            print("    ⚠  Could not locate all banner sub-elements.")
    except Exception as exc:
        print(f"    ⚠  Error while parsing banner: {exc}")

    return data


def _parse_daily_set_cards(soup: BeautifulSoup) -> list[Card]:
    """
    Parse the SET GIORNALIERO (Daily Set) section.

    Daily set cards use a different HTML structure from the other activity
    cards. The key markers are:
      - Element: mee-rewards-daily-set-item-content
      - tabindex="0"  on the inner div → today's card  (tabindex="-1" → tomorrow's, skip)
      - aria-disabled on a.ds-card-sec: empty or "false" = available, "true" = collected
      - Points: span.pointsString inside the card
      - Clickable element: the a.ds-card-sec link itself
    """
    cards: list[Card] = []
    items = soup.find_all("mee-rewards-daily-set-item-content")

    for item in items:
        try:
            container = item.find("div", class_="rewards-card-container")
            if not container:
                continue

            # tabindex="-1" means this is tomorrow's preview — skip it
            if container.get("tabindex") == "-1":
                continue

            link = item.find("a", class_="ds-card-sec")
            if not link:
                continue

            # aria-disabled="true" on today's card means already collected
            already_done = link.get("aria-disabled") == "true"

            pts_span = item.find(
                "span", class_="c-heading pointsString ng-binding ng-scope"
            )
            if not pts_span:
                continue
            pts_val = int(string_remove_space_newline(pts_span.get_text()))

            h3 = item.find("h3", class_="c-heading ellipsis ng-binding") \
              or item.find("h3", class_="c-heading ng-binding")
            description = h3.get_text().strip() if h3 else (
                link.get("aria-label", "").split("  ")[0].strip()
            )

            # Type detection: quizzes are >10 pts; polls contain "sondaggio"
            if pts_val > 10:
                card_type = CardTypeEnumeration.quiz
            elif CardTypeEnumeration.poll.value in description.lower():
                card_type = CardTypeEnumeration.poll
            else:
                card_type = CardTypeEnumeration.click

            # Store the clickable link element (not the heading) as soup
            cards.append(Card(
                description=description,
                points=pts_val,
                is_daily=True,
                already_collected=already_done,
                type=card_type,
                soup=link,
            ))
        except Exception as exc:
            print(f"    ⚠  Skipping daily set card due to parse error: {exc}")

    return cards


def _parse_other_cards(soup: BeautifulSoup) -> list[Card]:
    """
    Parse the 'Altre attività' / more-activities cards (non daily-set).

    The clickable element is `a.ds-card-sec` (the same selector daily-set
    cards use). Completion is signalled by a `span.mee-icon-SkypeCircleCheck`
    icon — `aria-disabled` is NOT reliable here: it stays "false" even on
    completed cards in this section.
    """
    cards: list[Card] = []
    card_items = soup.find_all("div", class_="c-card-content")

    for item in card_items:
        try:
            # Skip items that belong to the daily set (handled separately)
            if item.find("mee-rewards-daily-set-item-content"):
                continue

            link = item.find("a", class_="ds-card-sec")
            if not link:
                continue

            points_div = item.find("div", class_="points clearfix")
            if not points_div:
                continue

            pts_span = points_div.find(
                "span", class_="c-heading pointsString ng-binding ng-scope"
            )
            if not pts_span:
                continue

            pts_val = int(string_remove_space_newline(pts_span.get_text()))
            already_done = (
                points_div.find("span", class_="mee-icon mee-icon-SkypeCircleCheck")
                is not None
            )

            daily_h3   = item.find("h3", class_="c-heading ellipsis ng-binding")
            general_h3 = item.find("h3", class_="c-heading ng-binding")
            desc_el = daily_h3 if daily_h3 else general_h3
            if not desc_el:
                continue

            description = desc_el.get_text().strip()
            is_daily    = daily_h3 is not None

            if pts_val <= 10:
                card_type = (
                    CardTypeEnumeration.poll
                    if CardTypeEnumeration.poll.value in description.lower()
                    else CardTypeEnumeration.click
                )
            else:
                card_type = CardTypeEnumeration.quiz

            cards.append(Card(
                description=description,
                points=pts_val,
                is_daily=is_daily,
                already_collected=already_done,
                type=card_type,
                soup=link,
            ))
        except Exception as exc:
            print(f"    ⚠  Skipping card due to parse error: {exc}")

    return cards


def _parse_cards(soup: BeautifulSoup) -> list[Card]:
    """Return all available cards: daily set + other activities."""
    daily  = _parse_daily_set_cards(soup)
    others = _parse_other_cards(soup)
    # Daily set first, then the rest
    return daily + others

# ---------------------------------------------------------------------------
# Card collection
# ---------------------------------------------------------------------------

def _human_click(driver: webdriver.Edge, element) -> None:
    """
    Move the mouse naturally towards the element, hover briefly,
    then click — instead of teleporting the cursor directly onto it.
    A small random offset within the element avoids always hitting
    the exact centre, which is a known bot tell.
    """
    actions = ActionChains(driver)

    # Scroll element into view smoothly
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        element,
    )
    _sleep(0.4, 1.0)

    # Move to element with a slight random offset from its centre
    offset_x = random.randint(-10, 10)
    offset_y = random.randint(-5, 5)
    actions.move_to_element_with_offset(element, offset_x, offset_y)
    actions.pause(random.uniform(0.2, 0.6))   # hover before clicking
    actions.click()
    actions.perform()


def _prevent_new_tab(driver: webdriver.Edge, element) -> None:
    """
    Two-layer defence against new tabs opening:
      1. Remove the HTML target attribute from the link.
      2. Override window.open() in JS so any programmatic new-window call
         instead navigates the current tab — covers Angular click handlers
         that call window.open() directly rather than relying on the href.
    """
    driver.execute_script("""
        arguments[0].removeAttribute('target');
        window.open = function(url) { if (url) window.location.href = url; };
    """, element)


def _go_home(driver: webdriver.Edge) -> None:
    """Navigate back to the rewards homepage and wait for it to load."""
    driver.get(REWARDS_HOMEPAGE)
    _sleep(3.5, 6.0)


# ---------------------------------------------------------------------------
# Live DOM readers for "Other activity" cards
# ---------------------------------------------------------------------------
#
# These cards live under ``mee-rewards-more-activities-card-item`` and use
# ``a.ds-card-sec`` as the clickable element.  Completion is reported via a
# green check icon (``span.mee-icon-SkypeCircleCheck``) — ``aria-disabled``
# stays "false" even after completion, so we cannot rely on it.

_DAILY_SET_LINK_SELECTOR = (
    "mee-rewards-daily-set-item-content "
    ".rewards-card-container[tabindex='0'] a.ds-card-sec"
)

_OTHER_LINK_SELECTOR = (
    "mee-rewards-more-activities-card-item a.ds-card-sec"
)


def _daily_set_card_is_available(element) -> bool:
    """Return True if the daily-set card can still be clicked for points."""
    return element.get_attribute("aria-disabled") != "true"


def _other_card_is_completed(element) -> bool:
    try:
        return bool(element.find_elements(
            By.CSS_SELECTOR, "span.mee-icon-SkypeCircleCheck"
        ))
    except Exception:
        return False


def _other_card_points(element) -> int:
    try:
        pts_els = element.find_elements(By.CSS_SELECTOR, "span.pointsString")
        if not pts_els:
            return 0
        return int(string_remove_space_newline(pts_els[0].text))
    except Exception:
        return 0


def _other_card_description(element) -> str:
    try:
        h3 = element.find_elements(By.CSS_SELECTOR, "h3.c-heading")
        if h3 and h3[0].text.strip():
            return h3[0].text.strip()
    except Exception:
        pass
    label = element.get_attribute("aria-label") or ""
    return label.split(",")[0].strip() or "Other card"


def _verify_other_card_completed(driver: webdriver.Edge, aria_label: str) -> bool:
    """Return True if the card with the given aria-label now shows the green check."""
    try:
        for link in driver.find_elements(By.CSS_SELECTOR, _OTHER_LINK_SELECTOR):
            if link.get_attribute("aria-label") == aria_label:
                return _other_card_is_completed(link)
    except Exception:
        pass
    return False


def _collect_cards(driver: webdriver.Edge, cards: list[Card]) -> int:
    """
    Click every uncollected click-type card using human-like interactions.
    Returns the number of cards whose credit was confirmed on the page.

    Both daily-set and other-activity cards are handled with live CSS-selector
    lookups (fresh before every click) so stale element references after page
    navigation are never an issue. After each other-activity click we verify
    that the card now displays the green-check completion icon — if it does
    not, the click is reported as "Not credited" rather than "Collected".
    """
    # ── Print status of all cards ────────────────────────────────────────────
    for card in cards:
        if card.already_collected:
            print(f"    ✓  [Already done ]  {card.description} ({card.points} pts)")
        elif card.type == CardTypeEnumeration.poll:
            print(f"    ○  [Poll (skip)  ]  {card.description} ({card.points} pts)")
        elif card.type == CardTypeEnumeration.quiz:
            print(f"    ○  [Quiz (skip)  ]  {card.description} ({card.points} pts)")
        elif card.type == CardTypeEnumeration.click:
            print(f"    ○  [Click        ]  {card.description} ({card.points} pts)")

    clicked = 0

    # ── Daily set cards ──────────────────────────────────────────────────────
    # Re-query the DOM before every click so element references are never stale.
    # Track clicked cards by aria-label to avoid infinite loops if the page is
    # slow to update the aria-disabled state.
    seen_labels: set[str] = set()

    while True:
        _short_pause()
        try:
            candidates = driver.find_elements(
                By.CSS_SELECTOR, _DAILY_SET_LINK_SELECTOR
            )
        except Exception:
            break

        # Available cards use aria-disabled="" or "false"; collected use "true".
        # tabindex="0" on the container excludes tomorrow's preview (tabindex="-1").
        available = [
            el for el in candidates
            if _daily_set_card_is_available(el)
            and el.get_attribute("aria-label") not in seen_labels
        ]
        if not available:
            break

        element = random.choice(available)
        label   = element.get_attribute("aria-label") or ""
        seen_labels.add(label)

        # First part of aria-label is the card title, rest is description + pts
        description = label.split("   ")[0].strip() or "Daily card"
        try:
            pts_els = element.find_elements(By.CSS_SELECTOR, "span.pointsString")
            points  = int(string_remove_space_newline(pts_els[0].text)) if pts_els else 0
        except Exception:
            points = 0

        try:
            _prevent_new_tab(driver, element)
            _human_click(driver, element)
            _sleep(2.5, 5.0)        # simulate reading the destination page
            _go_home(driver)

            clicked += 1
            print(f"    ●  [Collected    ]  {description} (+{points} pts)")

        except Exception as exc:
            print(f"    ✗  [Failed       ]  {description} — {exc}")
            try:
                if REWARDS_HOMEPAGE not in driver.current_url:
                    _go_home(driver)
            except Exception:
                pass

        _between_cards_pause()

    # ── Other activity cards ─────────────────────────────────────────────────
    # Mirror the daily-set pattern: re-query the live DOM before each click so
    # references are never stale, and verify completion after the click by
    # looking for the green check icon. `aria-disabled` is unreliable in this
    # section — it stays "false" even on completed cards.
    seen_labels.clear()

    while True:
        _short_pause()
        try:
            candidates = driver.find_elements(
                By.CSS_SELECTOR, _OTHER_LINK_SELECTOR
            )
        except Exception:
            break

        # Filter: not already collected, not yet tried, click-type only
        clickable: list[tuple] = []
        for el in candidates:
            label = el.get_attribute("aria-label") or ""
            if not label or label in seen_labels:
                continue
            if _other_card_is_completed(el):
                continue
            points = _other_card_points(el)
            # Skip ads (no points) and quizzes (>10 pts — need answers)
            if points <= 0 or points > 10:
                continue
            description = _other_card_description(el)
            # Skip polls (require an opinion vote)
            if CardTypeEnumeration.poll.value in description.lower():
                continue
            clickable.append((el, label, points, description))

        if not clickable:
            break

        element, label, points, description = random.choice(clickable)
        seen_labels.add(label)

        try:
            _prevent_new_tab(driver, element)
            _human_click(driver, element)
            _sleep(2.5, 5.0)        # simulate reading the destination page
            _go_home(driver)

            _short_pause()
            if _verify_other_card_completed(driver, label):
                clicked += 1
                print(f"    ●  [Collected    ]  {description} (+{points} pts)")
            else:
                print(f"    ⚠  [Not credited ]  {description} ({points} pts) — click did not register")

        except Exception as exc:
            print(f"    ✗  [Failed       ]  {description} — {exc}")
            try:
                if REWARDS_HOMEPAGE not in driver.current_url:
                    _go_home(driver)
            except Exception:
                pass

        _between_cards_pause()

    return clicked

# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def run() -> None:
    print("=" * 60)
    print("   Microsoft Rewards — Daily Point Collector")
    print("=" * 60)

    kill_edge_processes()
    _sleep(1.5, 3.0)

    for idx, profile in enumerate(PROFILES):
        print(f"\n{'─' * 60}")
        print(f"  Profile: {profile}  [{idx + 1}/{len(PROFILES)}]")
        print(f"{'─' * 60}")

        driver = None
        try:
            driver = _make_driver(profile=profile)

            # Patch the navigator.webdriver flag before any page loads
            _patch_webdriver_flag(driver)

            # ── Step 1 · Read current points ────────────────────────────
            print("\n  [1/4] Loading rewards page…")
            soup_before = _fetch_soup(driver, save_debug=True)
            before = _parse_points(soup_before)
            print(f"        BEFORE  →  {before}")

            # ── Step 2 · Scan cards ──────────────────────────────────────
            print("\n  [2/4] Scanning available cards…")
            cards = _parse_cards(soup_before)
            if not cards:
                print("        No cards found. Saving page source for inspection…")
                _save_page_source(driver, "page_source_debug.html")
            else:
                print(f"        Found {len(cards)} card(s):")
                for card in cards:
                    status = "✓ done" if card.already_collected else "○ pending"
                    kind   = card.type.value
                    print(f"          [{status:10}] [{kind:8}] {card.description} ({card.points} pts)")

            # ── Step 3 · Collect click-type cards ────────────────────────
            print("\n  [3/4] Collecting cards…")
            collected = _collect_cards(driver, cards)
            print(f"\n        Clicked {collected} card(s).")

            # ── Step 4 · Read updated points ─────────────────────────────
            print("\n  [4/4] Refreshing page to confirm points…")
            soup_after = _fetch_soup(driver)
            after = _parse_points(soup_after)
            print(f"        AFTER   →  {after}")

            # ── Summary ──────────────────────────────────────────────────
            print(f"\n  {'─' * 56}")
            name = before.username or profile
            print(f"  SUMMARY  ·  {name}")
            print(f"  {'─' * 56}")
            if before.points is not None and after.points is not None:
                gained = after.points - before.points
                print(f"  Points before  :  {before.points:>8,}")
                print(f"  Points after   :  {after.points:>8,}")
                print(f"  Points gained  :  {gained:>+8,}")
            else:
                print("  Could not retrieve point totals.")
            if after.streak is not None:
                print(f"  Streak         :  {after.streak} day(s)")
            if after.daily is not None:
                print(f"  Daily progress :  {after.daily} pt(s) earned today")
            print(f"  {'─' * 56}")

        except Exception as exc:
            print(f"\n  [ERROR] Profile {profile}: {exc}")
        finally:
            if driver:
                driver.quit()

    print("\n  All done!\n")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user.")
        kill_edge_processes()
        sys.exit(0)
