import random
from itertools import pairwise

from vouch.seed.careers import career


def any_of_50(rng):
    return lambda: rng.randrange(50)


def many_careers():
    rng = random.Random(42)
    return [
        career(rng, pick_company=any_of_50(rng), first_year=2010, last_year=2026)
        for _ in range(500)
    ]


def test_every_career_has_at_least_one_job():
    for jobs in many_careers():
        assert len(jobs) >= 1


def test_each_job_ends_after_it_starts():
    for jobs in many_careers():
        for job in jobs:
            if job["end"] is not None:
                assert job["end"] > job["start"]


def test_jobs_do_not_overlap():
    for jobs in many_careers():
        for earlier, later in pairwise(jobs):
            assert later["start"] >= earlier["end"]


def test_only_the_last_job_can_be_ongoing():
    for jobs in many_careers():
        for job in jobs[:-1]:
            assert job["end"] is not None


def test_years_stay_within_range():
    for jobs in many_careers():
        for job in jobs:
            assert 2010 <= job["start"] <= 2026
            if job["end"] is not None:
                assert job["end"] <= 2026


def test_company_is_a_valid_index():
    for jobs in many_careers():
        for job in jobs:
            assert 0 <= job["company"] < 50


def test_same_seed_gives_same_career():
    first_rng = random.Random(42)
    second_rng = random.Random(42)

    first = career(first_rng, pick_company=any_of_50(first_rng), first_year=2010, last_year=2026)
    second = career(second_rng, pick_company=any_of_50(second_rng), first_year=2010, last_year=2026)

    assert first == second


def test_every_job_uses_the_given_picker():
    rng = random.Random(42)
    jobs = career(rng, pick_company=lambda: 7, first_year=2010, last_year=2026)

    for job in jobs:
        assert job["company"] == 7
