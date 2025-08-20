from __future__ import annotations

import random
import string
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from ..enums import STATE


def random_name(prefix: str, rng: Optional[random.Random] = None) -> str:
    r = rng or random
    letters = "".join(r.choice(string.ascii_uppercase) for _ in range(4))
    return f"{prefix} {letters} {r.randint(100,999)}"


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class RandomContext:
    db_path: Optional[str] = None
    rng_seed: Optional[int] = None

    def __post_init__(self) -> None:
        self.rng = random.Random(self.rng_seed)

    def random_state(self) -> Optional[str]:
        return self.rng.choice(STATE)

    def random_currency(self) -> str:
        return self.rng.choice(["USD", "CAD", "EUR"])

    def random_date_within(self, days_back: int = 30) -> str:
        today = date.today()
        start = today - timedelta(days=self.rng.randint(0, days_back))
        return start.strftime("%Y-%m-%d")


