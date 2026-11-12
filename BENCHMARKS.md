# Benchmarks

Every entry follows the [benchmark protocol](docs/benchmark-protocol.md).
Newest entries go at the bottom. Copy the template below for each one.

<!--
## YYYY-MM-DD · Phase N · <change>
- Scenario / seed size / environment / machine + Docker limits:
- Commit before / after:
- Cache state (cold/warm), warm-up duration, measured duration, runs:
- Before: p50 __ ms · p99 __ ms · __ req/s · errors __%  (median of N runs; spread in brackets)
- After:  p50 __ ms · p99 __ ms · __ req/s · errors __%
- Why it worked (mechanism):
- What didn't help:
-->

## 2026-11-13 · Phase 0 · Baseline: smoke
- Scenario / seed size / environment / machine + Docker limits: smoke / no seeded data used (placeholder endpoints) / local-m2: Apple M2, 8 GB; Docker VM 8 CPUs / 3.8 GB; api 1 CPU / 512 MB; k6 2 CPU / 512 MB
- Commit: 036eb04
- Cache state (cold/warm), warm-up duration, measured duration, runs: warm / 2m / 1m / 3
- Measured (median of 3 runs, spread in brackets): p50 2.57 ms (2.56–2.67) · p99 3.95 ms (3.65–4.40) · 20.0 req/s (20.0–20.0) · errors 0.00% (0.00–0.00) · dropped 0
- Why it worked (mechanism): n/a, baseline
- What didn't help: n/a, baseline
