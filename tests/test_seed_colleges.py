import random

from vouch.seed.colleges import COLLEGES, college_name, pick_college


def many_names():
    rng = random.Random(42)
    return [college_name(rng, pick_college(rng)) for _ in range(1000)]


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


def test_name_is_a_spelling_of_the_given_college():
    rng = random.Random(42)
    for _ in range(100):
        assert college_name(rng, 3) in COLLEGES[3]


def test_bigger_colleges_are_picked_more_often():
    rng = random.Random(42)
    picks = [pick_college(rng) for _ in range(10_000)]

    assert picks.count(0) > picks.count(len(COLLEGES) - 1) * 3


def test_same_seed_gives_same_college_names():
    first_rng = random.Random(42)
    second_rng = random.Random(42)

    first = [college_name(first_rng, pick_college(first_rng)) for _ in range(5)]
    second = [college_name(second_rng, pick_college(second_rng)) for _ in range(5)]

    assert first == second
