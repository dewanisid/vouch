import argparse
import time
from pathlib import Path

from vouch.db import connect
from vouch.seed.generate import generate

SCHEMA = Path(__file__).parents[3] / "db" / "schema.sql"

SIZES = {"1k": 1_000, "10k": 10_000, "100k": 100_000, "1m": 1_000_000}

COLUMNS = {
    "companies": "id, name",
    "users": "id, name",
    "jobs": "user_id, company_id, start_year, end_year",
    "educations": "user_id, college_name",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill the database with fake Vouch data.")
    parser.add_argument("--size", choices=SIZES, default="1k")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    started = time.perf_counter()
    data = generate(SIZES[args.size], seed=args.seed)
    generated = time.perf_counter()

    with connect() as conn:
        conn.execute("DROP TABLE IF EXISTS educations, jobs, users, companies")
        conn.execute(SCHEMA.read_text())
        with conn.cursor() as cur:
            for table, columns in COLUMNS.items():
                with cur.copy(f"COPY {table} ({columns}) FROM STDIN") as copy:
                    for row in data[table]:
                        copy.write_row(row)
    finished = time.perf_counter()

    for table in COLUMNS:
        print(f"{table:<11} {len(data[table]):>9,} rows")
    print(f"generate {generated - started:.2f}s, write {finished - generated:.2f}s")


if __name__ == "__main__":
    main()
