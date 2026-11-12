import random
from collections.abc import Iterator
from functools import partial
from itertools import accumulate

from vouch.seed.careers import career
from vouch.seed.colleges import COLLEGES, college_name, pick_college
from vouch.seed.names import person_name
from vouch.seed.sizes import company_sizes

FIRST_YEAR = 2010
LAST_YEAR = 2026
PEOPLE_PER_COMPANY = 20
BATCH_SIZE = 10_000

# Graduates of a college cluster in a few companies (campus hiring, alumni referrals).
FAVOURITES_PER_COLLEGE = 5
CLUSTER_SHARE = 0.6

TABLES = ["companies", "users", "jobs", "educations"]

# One table row, with its columns in order: ids, names, years, or None.
Row = tuple[int | str | None, ...]
Batch = dict[str, list[Row]]


def pick_company(
    rng: random.Random,
    favourites: list[int],
    company_ids: range,
    cum_sizes: list[int],
) -> int:
    if rng.random() < CLUSTER_SHARE:
        return rng.choice(favourites)
    return rng.choices(company_ids, cum_weights=cum_sizes)[0]


def generate_batches(user_count: int, seed: int, batch_size: int = BATCH_SIZE) -> Iterator[Batch]:
    """Yield the data in pieces, so memory stays flat however big user_count is."""
    rng = random.Random(seed)

    company_count = max(1, user_count // PEOPLE_PER_COMPANY)
    company_ids = range(company_count)
    cum_sizes = list(accumulate(company_sizes(user_count, company_count)))
    favourites = [
        rng.choices(company_ids, cum_weights=cum_sizes, k=FAVOURITES_PER_COLLEGE) for _ in COLLEGES
    ]

    companies: list[Row] = [(company_id, f"Company {company_id}") for company_id in company_ids]
    yield {"companies": companies, "users": [], "jobs": [], "educations": []}

    for batch_start in range(0, user_count, batch_size):
        batch: Batch = {"companies": [], "users": [], "jobs": [], "educations": []}

        for user_id in range(batch_start, min(batch_start + batch_size, user_count)):
            # Build each user completely before the next one, so the order of
            # random numbers (and so the data) doesn't depend on batch_size.
            batch["users"].append((user_id, person_name(rng)))
            college = pick_college(rng)

            picker = partial(pick_company, rng, favourites[college], company_ids, cum_sizes)
            for job in career(rng, pick_company=picker, first_year=FIRST_YEAR, last_year=LAST_YEAR):
                batch["jobs"].append((user_id, job["company"], job["start"], job["end"]))
            batch["educations"].append((user_id, college_name(rng, college)))

        yield batch


def generate(user_count: int, seed: int, batch_size: int = BATCH_SIZE) -> Batch:
    """All the data at once. Handy in tests; the seeder itself uses generate_batches."""
    data: Batch = {table: [] for table in TABLES}
    for batch in generate_batches(user_count, seed, batch_size):
        for table in TABLES:
            data[table].extend(batch[table])
    return data
