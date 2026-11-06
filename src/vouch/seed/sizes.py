def company_sizes(total_people: int, company_count: int) -> list[int]:
    weights = [1 / rank for rank in range(1, company_count + 1)]
    total_weight = sum(weights)

    sizes = [int(total_people * weight / total_weight) for weight in weights]

    leftover = total_people - sum(sizes)
    for index in range(leftover):
        sizes[index] += 1

    return sizes
