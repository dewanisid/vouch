import random

from vouch.seed.colleges import COLLEGES, college_name


def many_names():
    rng = random.Random(42)
    return [college_name(rng) for _ in range(1000)]


def all_spellings():
    spellings = []
    for group in COLLEGES:
        spellings.extend(group)
    return spellings


def test_every_name_is_a_known_spelling():
    known = all_spellings()
    for name in many_names():
        assert name in known


def test_some_college_appears_under_more_than_one_spelling():
    names = many_names()

    assert "IIT Bombay" in names
    assert "IITB" in names


def test_same_seed_gives_same_college_names():
    first_rng = random.Random(42)
    second_rng = random.Random(42)

    first = [college_name(first_rng) for _ in range(5)]
    second = [college_name(second_rng) for _ in range(5)]

    assert first == second
