from dataclasses import dataclass

from src.card_type_enum import CardTypeEnumeration


@dataclass
class Card:
    description: str
    points: int
    is_daily: bool
    already_collected: bool
    type: CardTypeEnumeration
    soup: str

    def __str__(self) -> str:
        return (
            f"{'Daily' if self.is_daily else 'General'}: "
            f"[{self.type.value} - {self.points}] {self.description}"
            f" - {'Already Collected' if self.already_collected else 'Not Collected'}"
            # f" -> {self.soup}"
        )
