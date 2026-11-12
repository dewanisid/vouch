import argparse
import time
from pathlib import Path

from vouch.db import connect
from vouch.seed.generate import TABLES, generate_batches

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
    rows = dict.fromkeys(TABLES, 0)

    with connect() as conn:
        conn.execute("DROP TABLE IF EXISTS educations, jobs, users, companies")
        conn.execute(SCHEMA.read_text())
        with conn.cursor() as cur:
            for batch in generate_batches(SIZES[args.size], seed=args.seed):
                for table in TABLES:
                    if not batch[table]:
                        continue
                    with cur.copy(f"COPY {table} ({COLUMNS[table]}) FROM STDIN") as copy:
                        for row in batch[table]:
                            copy.write_row(row)
                    rows[table] += len(batch[table])

    for table in TABLES:
        print(f"{table:<11} {rows[table]:>9,} rows")
    print(f"total {time.perf_counter() - started:.2f}s")

if __name__ == "__main__":
    main()
