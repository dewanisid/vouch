import random
from itertools import accumulate

# Each inner list is one college: every spelling people use for it.
# Ordered by size: the first is the biggest (Zipf, like companies).
COLLEGES = [
    ["Anna University"],
    ["University of Delhi", "Delhi University", "DU"],
    ["VIT Vellore", "VIT"],
    ["IIT Bombay", "IITB", "IIT-Bombay"],
    ["BITS Pilani", "BITS", "Birla Institute of Technology and Science"],
    ["NIT Trichy", "NITT", "NIT Tiruchirappalli"],
    ["IIT Delhi", "IITD"],
    ["Jadavpur University", "JU"],
    ["IIIT Hyderabad", "IIITH", "IIIT-H"],
    ["College of Engineering Pune", "COEP"],
]

CUM_WEIGHTS = list(accumulate(1 / rank for rank in range(1, len(COLLEGES) + 1)))


def pick_college(rng: random.Random) -> int:
    return rng.choices(range(len(COLLEGES)), cum_weights=CUM_WEIGHTS)[0]


def college_name(rng: random.Random, college: int) -> str:
    return rng.choice(COLLEGES[college])
