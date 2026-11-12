# Benchmark protocol

Numbers are only compared when they were measured the same way. This protocol
was written once, in Phase 0, and isn't bent afterwards. If a rule turns out to
be wrong, change it through an ADR, and don't compare numbers across the change.

Every performance claim in this repo (a PR, an ADR, a retrospective) points at
an entry in [`BENCHMARKS.md`](../BENCHMARKS.md) that followed these rules.

## What we measure

All latency is measured **at the client** (the load generator), because that's
what a user waits for.

| Metric | Meaning | Why it's here |
| --- | --- | --- |
| p50 | Half of requests are faster than this | The typical experience |
| p99 | 99% are faster; the slowest 1% are slower | The bad-day experience, and the first place queues, locks and pauses show up |
| Throughput (req/s) | Requests completed per second | Capacity. Latency only means something at a stated load |
| Error rate (%) | Requests that failed or timed out | A fast error isn't a success. A run with errors above 1% is reported but not compared |

The average isn't reported. It blends fast and slow requests into one number
that describes nobody: 98 requests at 20 ms and 2 at 4 s average out
to about 100 ms, which hides both the typical case and the disaster.

## The environment

### Local machine (baseline environment "local-m2")

| Item | Value |
| --- | --- |
| Machine | Apple M2, 8 cores, 8 GB RAM, macOS 26.0 |
| Docker | Docker Engine 29.2.1; Docker Desktop VM with 8 CPUs and 3.8 GB memory |
| Postgres | `postgres:17.5`, 1.0 CPU, 1 GB |
| Redis | `redis:7.4.2`, 0.5 CPU, 256 MB |
| Observability | Prometheus, Loki, Grafana, OTel collector: 0.5 CPU each, 256–512 MB |
| App containers | Limits set in `compose.yaml` when they're added (Phase 1 on) |

Limits come from `compose.yaml`. If any of these values change, it's a new
baseline: earlier numbers are no longer comparable, and the entry says so.

### AWS (later phases)

AWS gets its own baseline, written here when it exists. **Local and AWS numbers
are never compared with each other.** Different hardware, network and noise
make the comparison meaningless.

## Before a run

1. Same machine, plugged into power, no heavy apps running alongside (no builds,
   video calls, browser tabs playing video).
2. Docker limits as listed above. `docker compose up -d --wait` and the smoke test pass.
3. Fresh data: `python -m vouch.seed --size <size> --seed 42`. Same size and
   same seed for both sides of a comparison.
4. Note the git commit (`git rev-parse --short HEAD`) of the code being measured.

## The run

- **Fixed scenario.** A named k6 script from the repo, unchanged between the
  two sides of a comparison.
- **Fixed load.** The scenario sets the request rate (arrival rate), not just
  the number of virtual users. With a fixed number of users, a slow server
  receives fewer requests and looks better than it is.
- **Warm-up: at least 2 minutes** of the same load before measuring, so caches,
  connection pools and (from Phase 1.5) the JVM's JIT compiler reach a steady state.
  Warm-up results are thrown away.
- **Record cache state:** cold (caches flushed before the run) or warm (after warm-up).
- **Fixed duration.** The measured period is stated in the entry. Default: 5 minutes.
- **At least 3 runs.** Report the **median** of each metric across runs, and the
  **spread** (lowest–highest), for example `p99 142 ms (138–151)`.

## Comparing

- **One change per comparison.** Two changes at once means neither result can
  be trusted.
- **Spread decides what counts.** If the before and after ranges overlap, the
  result is "no measurable difference", whatever the medians say.
- **Write down what didn't help**, too. A failed attempt with numbers is
  worth keeping, because it stops the same idea being tried twice.
- **No entry, no claim.** A performance change without a `BENCHMARKS.md` entry
  didn't happen.
