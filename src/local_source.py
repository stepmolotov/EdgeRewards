from typing import Any

from bs4 import BeautifulSoup

from src.helpers.string_remove_space_newline import string_remove_space_newline


def open_page_source() -> Any:
    with open("page_source.html", "r", encoding="utf-8") as f:
        data = f.read()
    return data


def get_available_cards(source: Any) -> None:
    soup = BeautifulSoup(source, "html5lib")
    # cards_items = soup.find_all(
    #     "mee-rewards-daily-set-item-content", class_="ng-isolate-scope"
    # )
    cards_items = soup.find_all("div", class_="c-card-content")
    print(f"Found {len(cards_items)} cards")
    counter = 0
    for card in cards_items:
        # description = card.find("h3", class_="c-heading ellipsis ng-binding")
        points = card.find("div", class_="points clearfix")
        if points:
            # points_available = points.find("span", class_="mee-icon mee-icon-AddMedium")
            points_quantity = points.find(
                "span", class_="c-heading pointsString ng-binding ng-scope"
            )
            if points_quantity:
                points_quantity_val = string_remove_space_newline(
                    points.find(
                        "span", class_="c-heading pointsString ng-binding ng-scope"
                    ).get_text()
                )
            else:
                points_quantity_val = ""
            points_already_collected = points.find(
                "span", class_="mee-icon mee-icon-SkypeCircleCheck"
            )
            counter += 1
            description = card.find("h3", class_="c-heading ellipsis ng-binding")
            not_interesting_description = card.find("h3", class_="c-heading ng-binding")
            if description:
                print(f"\t** [{points_quantity_val}] {description.get_text()} **")
            elif not_interesting_description:
                print(
                    f"\t [{points_quantity_val}] {not_interesting_description.get_text()}"
                )
            if points_already_collected:
                print("\t\t Already Collected")
            else:
                already_collected = points.find(
                    "span", class_="mee-icon mee-icon-SkypeCircleCheck"
                )
                if already_collected:
                    print(f"Already collected")
                # else:
                #     print("Can't find icons")
    print(f"Points Cards: {counter}/{len(cards_items)}")


if __name__ == "__main__":
    data = open_page_source()
    get_available_cards(source=data)
