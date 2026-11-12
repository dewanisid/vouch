import random

from vouch.seed.names import person_names


def test_returns_the_requested_number_of_names():
    names = person_names(10, random.Random(42))

    assert len(names) == 10


def test_same_seed_gives_same_names():
    first = person_names(5, random.Random(42))
    second = person_names(5, random.Random(42))

    assert first == second


def test_different_seeds_give_different_names():
    first = person_names(5, random.Random(42))
    second = person_names(5, random.Random(43))

    assert first != second


def test_each_name_has_a_first_and_last_part():
    names = person_names(20, random.Random(42))

    for name in names:
        assert len(name.split(" ")) == 2
import random

from vouch.seed.names import person_names


def test_returns_the_requested_number_of_names():
    names = person_names(10, random.Random(42))

    assert len(names) == 10


def test_same_seed_gives_same_names():
    first = person_names(5, random.Random(42))
    second = person_names(5, random.Random(42))

    assert first == second


def test_different_seeds_give_different_names():
    first = person_names(5, random.Random(42))
    second = person_names(5, random.Random(43))

    assert first != second


def test_each_name_has_a_first_and_last_part():
    names = person_names(20, random.Random(42))

    for name in names:
        assert len(name.split(" ")) == 2
