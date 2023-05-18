from dataclasses import dataclass
from typing import Optional


@dataclass
class HomepageData:
    username: Optional[str] = None
    points: Optional[int] = None
    daily: Optional[int] = None
    streak: Optional[int] = None

    def __str__(self) -> str:
        return (
            f"Username: [{self.username}] "
            f"Points: [{self.points} pts] "
            f"Daily: [{self.daily} pts] "
            f"Streak: [{self.streak} days]"
        )
