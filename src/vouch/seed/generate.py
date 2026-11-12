import random
from itertools import accumulate

from vouch.seed.careers import career
from vouch.seed.colleges import COLLEGES, college_name, pick_college
from vouch.seed.names import person_names
from vouch.seed.sizes import company_sizes

FIRST_YEAR = 2010
LAST_YEAR = 2026
PEOPLE_PER_COMPANY = 20

# Graduates of a college cluster in a few companies (campus hiring, alumni referrals).
FAVOURITES_PER_COLLEGE = 5
CLUSTER_SHARE = 0.6


def pick_company(
    rng: random.Random,
    favourites: list[int],
    company_ids: range,
    cum_sizes: list[int],
) -> int:
    if rng.random() < CLUSTER_SHARE:
        return rng.choice(favourites)
    return rng.choices(company_ids, cum_weights=cum_sizes)[0]


def generate(user_count: int, seed: int) -> dict[str, list[tuple]]:
    rng = random.Random(seed)

    company_count = max(1, user_count // PEOPLE_PER_COMPANY)
    company_ids = range(company_count)
    cum_sizes = list(accumulate(company_sizes(user_count, company_count)))
    companies = [(company_id, f"Company {company_id}") for company_id in company_ids]

    favourites = [
        rng.choices(company_ids, cum_weights=cum_sizes, k=FAVOURITES_PER_COLLEGE)
        for _ in COLLEGES
    ]

    users = list(enumerate(person_names(user_count, rng)))

    jobs = []
    educations = []
    for user_id, _ in users:
        college = pick_college(rng)

        def picker() -> int:
            return pick_company(rng, favourites[college], company_ids, cum_sizes)

        for job in career(rng, pick_company=picker, first_year=FIRST_YEAR, last_year=LAST_YEAR):
            jobs.append((user_id, job["company"], job["start"], job["end"]))
        educations.append((user_id, college_name(rng, college)))

    return {
        "companies": companies,
        "users": users,
        "jobs": jobs,
        "educations": educations,
    }
