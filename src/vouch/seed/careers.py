import random


def career(
    rng: random.Random,
    company_cum_weights: list[int],
    first_year: int,
    last_year: int,
) -> list[dict]:
    jobs = []
    year = rng.randint(first_year, last_year - 1)

    while True:
        company = rng.choices(range(len(company_cum_weights)), cum_weights=company_cum_weights)[0]
        end = year + rng.randint(1, 5)

        if end >= last_year or rng.random() < 0.3:
            jobs.append({"company": company, "start": year, "end": None})
            return jobs

        jobs.append({"company": company, "start": year, "end": end})
        year = end
