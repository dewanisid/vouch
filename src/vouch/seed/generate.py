import random

from vouch.seed.careers import career
from vouch.seed.colleges import college_name
from vouch.seed.names import person_names
from vouch.seed.sizes import company_sizes

FIRST_YEAR = 2010
LAST_YEAR = 2026
PEOPLE_PER_COMPANY = 20


def generate(user_count: int, seed: int) -> dict[str, list[tuple]]:
    rng = random.Random(seed)

    company_count = max(1, user_count // PEOPLE_PER_COMPANY)
    sizes = company_sizes(user_count, company_count)
    companies = [(company_id, f"Company {company_id}") for company_id in range(company_count)]

    users = list(enumerate(person_names(user_count, rng)))

    jobs = []
    educations = []
    for user_id, _ in users:
        for job in career(rng, company_weights=sizes, first_year=FIRST_YEAR, last_year=LAST_YEAR):
            jobs.append((user_id, job["company"], job["start"], job["end"]))
        educations.append((user_id, college_name(rng)))

    return {
        "companies": companies,
        "users": users,
        "jobs": jobs,
        "educations": educations,
    }
