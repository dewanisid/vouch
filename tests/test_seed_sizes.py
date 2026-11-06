from vouch.seed.sizes import company_sizes


def test_sizes_add_up_to_total_people():
    sizes = company_sizes(total_people=1000, company_count=100)

    assert sum(sizes) == 1000


def test_returns_one_size_per_company():
    sizes = company_sizes(total_people=1000, company_count=100)

    assert len(sizes) == 100


def test_sizes_go_from_largest_to_smallest():
    sizes = company_sizes(total_people=1000, company_count=100)

    assert sizes == sorted(sizes, reverse=True)

def test_sizes_add_up_when_people_do_not_divide_evenly():
    sizes = company_sizes(total_people=10, company_count=3)

    assert sum(sizes) == 10

def test_largest_one_percent_of_companies_hold_most_people():
    sizes = company_sizes(total_people=100_000, company_count=5_000)

    largest_one_percent = sizes[:50]

    assert sum(largest_one_percent) >= 40_000
