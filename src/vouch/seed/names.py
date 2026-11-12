import random

FIRST_NAMES = [
    "Aarav", "Priya", "Rohan", "Ananya", "Vikram",
    "Sara", "Kabir", "Meera", "Arjun", "Zoya",
]

LAST_NAMES = [
    "Sharma", "Iyer", "Khan", "Patel", "Reddy",
    "Das", "Mehta", "Nair", "Gupta", "Singh",
]


def person_names(count: int, rng: random.Random) -> list[str]:
    return [
        f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        for _ in range(count)
    ]
