import random

COLLEGES = [
    ["IIT Bombay", "IITB", "IIT-Bombay"],
    ["IIT Delhi", "IITD"],
    ["BITS Pilani", "BITS", "Birla Institute of Technology and Science"],
    ["NIT Trichy", "NITT", "NIT Tiruchirappalli"],
    ["University of Delhi", "Delhi University", "DU"],
    ["VIT Vellore", "VIT"],
    ["Anna University"],
]


def college_name(rng: random.Random) -> str:
    spellings = rng.choice(COLLEGES)
    return rng.choice(spellings)
