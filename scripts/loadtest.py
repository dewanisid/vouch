"""Run a k6 scenario under the benchmark protocol and record the result.

    uv run python scripts/loadtest.py smoke            # protocol run, writes BENCHMARKS.md
    uv run python scripts/loadtest.py smoke --quick    # 3 short runs to try things; writes nothing

Each run is a warm-up, then a measured period, at a fixed request rate.
After 3 runs it reports the median and spread (lowest-highest) of each metric
and appends an entry to BENCHMARKS.md. See docs/benchmark-protocol.md.
"""

import argparse
import datetime
import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "loadtest" / "results"
BENCHMARKS = ROOT / "BENCHMARKS.md"

RUNS = 3
WARMUP = "2m"
# Measured duration per scenario. Smoke is a health check, so a shorter window is enough.
DURATIONS = {"smoke": "1m", "search": "5m", "profile-view": "5m", "send-request": "5m"}
QUICK_WARMUP, QUICK_DURATION = "5s", "10s"


def seconds(duration: str) -> int:
    value, unit = int(duration[:-1]), duration[-1]
    return value * {"s": 1, "m": 60}[unit]


def run(command: list[str]) -> str:
    return subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True).stdout


def one_run(scenario: str, number: int, warmup: str, duration: str) -> dict[str, float]:
    out = f"results/{scenario}-run{number}.json"
    subprocess.run(
        [
            "docker", "compose", "run", "--rm", "--quiet-pull",
            "-e", f"WARMUP={warmup}", "-e", f"DURATION={duration}", "-e", f"SUMMARY_OUT={out}",
            "k6", "run", "--quiet", f"scenarios/{scenario}.js",
        ],
        cwd=ROOT, check=True, capture_output=True,
    )  # fmt: skip
    metrics = json.loads((ROOT / "loadtest" / out).read_text())["metrics"]

    latency = metrics["http_req_duration{scenario:measure}"]["values"]
    requests = metrics["http_reqs{scenario:measure}"]["values"]["count"]
    failed = metrics["http_req_failed{scenario:measure}"]["values"]["rate"]
    dropped = metrics["dropped_iterations{scenario:measure}"]["values"]["count"]
    return {
        "p50": latency["p(50)"],
        "p99": latency["p(99)"],
        # k6's own rate divides by the whole test, warm-up included. Use the measured window.
        "rps": requests / seconds(duration),
        "errors": failed * 100,
        "dropped": dropped,
    }


def summarise(values: list[float], unit: str, digits: int) -> str:
    median = statistics.median(values)
    low, high = min(values), max(values)
    return f"{median:.{digits}f}{unit} ({low:.{digits}f}–{high:.{digits}f})"  # noqa: RUF001


def environment() -> str:
    cpu = run(["sysctl", "-n", "machdep.cpu.brand_string"]).strip()
    ram_gb = int(run(["sysctl", "-n", "hw.memsize"])) / 2**30
    docker = json.loads(run(["docker", "info", "--format", "{{json .}}"]))
    config = run(["docker", "compose", "--profile", "tools", "config", "--format", "json"])
    services = json.loads(config)["services"]

    def limits(name: str) -> str:
        service = services[name]
        return f"{name} {service.get('cpus', '?')} CPU / {int(service['mem_limit']) // 2**20} MB"

    return (
        f"local-m2: {cpu}, {ram_gb:.0f} GB; Docker VM {docker['NCPU']} CPUs / "
        f"{docker['MemTotal'] / 2**30:.1f} GB; {limits('api')}; {limits('k6')}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("scenario", choices=DURATIONS)
    parser.add_argument("--quick", action="store_true", help="short runs; writes nothing")
    parser.add_argument("--label", help="title for the BENCHMARKS.md entry")
    args = parser.parse_args()

    if args.quick:
        warmup, duration = QUICK_WARMUP, QUICK_DURATION
    else:
        warmup, duration = WARMUP, DURATIONS[args.scenario]
    print(f"Starting the API, then {RUNS} runs of '{args.scenario}'")
    print(f"Each run: {warmup} warm-up + {duration} measured")
    run(["docker", "compose", "up", "-d", "--wait", "api"])

    results = []
    for number in range(1, RUNS + 1):
        result = one_run(args.scenario, number, warmup, duration)
        results.append(result)
        print(
            f"  run {number}: p50 {result['p50']:.2f} ms · p99 {result['p99']:.2f} ms · "
            f"{result['rps']:.1f} req/s · errors {result['errors']:.2f}% · "
            f"dropped {result['dropped']:.0f}"
        )

    def column(key: str) -> list[float]:
        return [result[key] for result in results]

    measured = (
        f"p50 {summarise(column('p50'), ' ms', 2)} · p99 {summarise(column('p99'), ' ms', 2)} · "
        f"{summarise(column('rps'), ' req/s', 1)} · errors {summarise(column('errors'), '%', 2)} · "
        f"dropped {sum(column('dropped')):.0f}"
    )
    print(f"Median (spread): {measured}")

    if args.quick:
        print("Quick run: not protocol-compliant, so nothing was written to BENCHMARKS.md.")
        return

    commit = run(["git", "rev-parse", "--short", "HEAD"]).strip()
    dirty = " (with uncommitted changes)" if run(["git", "status", "--porcelain"]).strip() else ""
    label = args.label or f"Baseline: {args.scenario}"
    entry = f"""
## {datetime.date.today()} · Phase 0 · {label}
- Scenario / seed size / environment / machine + Docker limits: {args.scenario} / no seeded data used (placeholder endpoints) / {environment()}
- Commit: {commit}{dirty}
- Cache state (cold/warm), warm-up duration, measured duration, runs: warm / {warmup} / {duration} / {RUNS}
- Measured (median of {RUNS} runs, spread in brackets): {measured}
- Why it worked (mechanism): n/a, baseline
- What didn't help: n/a, baseline
"""  # noqa: E501
    with BENCHMARKS.open("a") as file:
        file.write(entry)
    print(f"Appended to {BENCHMARKS.name}.")


if __name__ == "__main__":
    main()
