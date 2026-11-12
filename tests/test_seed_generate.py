from vouch.seed.generate import generate


def test_creates_exactly_the_requested_number_of_users():
    data = generate(1000, seed=42)

    assert len(data["users"]) == 1000


def test_every_user_has_a_job_and_a_college():
    data = generate(1000, seed=42)
    users_with_a_job = {job[0] for job in data["jobs"]}
    users_with_a_college = {education[0] for education in data["educations"]}

    for user_id, _ in data["users"]:
        assert user_id in users_with_a_job
        assert user_id in users_with_a_college


def test_same_seed_gives_identical_data():
    assert generate(1000, seed=42) == generate(1000, seed=42)


def test_different_seed_gives_different_data():
    assert generate(1000, seed=42) != generate(1000, seed=43)


def test_jobs_point_at_existing_companies():
    data = generate(1000, seed=42)
    company_ids = {company[0] for company in data["companies"]}

    for job in data["jobs"]:
        assert job[1] in company_ids


def test_biggest_company_has_more_jobs_than_smallest():
    data = generate(1000, seed=42)
    last_company = len(data["companies"]) - 1
    jobs_at_biggest = [job for job in data["jobs"] if job[1] == 0]
    jobs_at_smallest = [job for job in data["jobs"] if job[1] == last_company]

    assert len(jobs_at_biggest) > len(jobs_at_smallest)
