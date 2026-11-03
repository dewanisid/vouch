# Phase 0 backlog (draft)

Drafted 2026-11-03. Moves onto the GitHub Projects board next session; each story becomes one issue.
Phase 0 has no end users yet, so these are **technical stories**: the "user" is the developer.
Numbers marked _(placeholder)_ get tuned during design.

Suggested order: S1 → S2 → S3 → S4 → S5 → S6 → S7 → S8 → S9 → S10.

---

## S1 · GitHub board, remote and branch protection

**As a** developer, **I want** the repo on GitHub with a project board and a protected `main` branch, **so that** every change goes through a pull request and work is visible as cards.

**Acceptance criteria**
1. **Given** the local repo, **when** I push `main` to GitHub, **then** the remote shows the commits and none of the git-ignored private files.
2. **Given** branch protection on `main`, **when** I try `git push origin main` directly with a new commit, **then** GitHub rejects it.
3. **Given** the board, **when** I open it, **then** it has the columns Backlog → Ready → In progress → Review → Done, and the stories in this file are cards in Backlog.

**Concepts:** Branch Protection, .env in .gitignore
**Test cases:** manual checks 1–3 (no code yet).

---

## S2 · Config via environment and `.env.example`

**As a** developer, **I want** all configuration (ports, passwords, URLs) read from environment variables, with a committed `.env.example`, **so that** secrets never enter git and the same code runs unchanged locally, in CI and later on AWS.

**Acceptance criteria**
1. **Given** a fresh clone, **when** I copy `.env.example` to `.env` and fill it in, **then** the stack starts with no code edits.
2. **Given** `.env.example`, **when** I read it, **then** every variable has a comment and only fake values.
3. **Given** a required variable is missing, **when** a service starts, **then** it fails immediately with a message naming the variable (it doesn't silently use a default).

**Concepts:** .env in .gitignore, 12-Factor Apps, Environment Parity
**Test cases:** config loader unit test for criterion 3.

---

## S3 · Local stack with Docker Compose

**As a** developer, **I want** one command to start Postgres, Redis, MinIO, Prometheus, Grafana, Loki and an OpenTelemetry collector, **so that** every session and every benchmark runs on the same, known environment.

**Acceptance criteria**
1. **Given** Docker is running and `.env` exists, **when** I run `docker compose up -d`, **then** all services report healthy within 2 minutes _(placeholder)_.
2. **Given** the stack is running, **when** I open Grafana, **then** Prometheus and Loki are already connected as data sources (no clicking required).
3. **Given** the compose file, **when** I read it, **then** every image has a pinned version (no `latest`) and every container has CPU and memory limits.
4. **Given** I run `docker compose down` and then `up` again, **when** I query Postgres, **then** data written before is still there (named volumes).

**Concepts:** Environment Parity, Lockfiles (pinned versions)
**Systems lens:** find a container's process on the host; read its limits from the cgroup files.
**Test cases:** a smoke-test script that checks each service's health endpoint.

---

## S4 · Seed generator, first slice (1k users)

**As a** developer, **I want** a command that fills the database with realistic fake users, companies, colleges and affiliations at a chosen size, **so that** every benchmark runs on data shaped like the real world, and its numbers can be trusted and compared.

**Acceptance criteria**
1. **Given** an empty database, **when** I run the seeder with size `1k`, **then** exactly 1,000 users exist and every user has at least one affiliation.
2. **Given** the same random seed number, **when** I run the seeder twice on empty databases, **then** both runs produce identical data.
3. **Given** a seeded database, **when** I count employees per company, **then** the largest 1% of companies hold at least 40% of all current employees _(placeholder)_.
4. **Given** any seeded size, **when** I list institution names, **then** at least some institutions appear under more than one spelling (e.g. "IITB" and "IIT Bombay").
5. **Given** any seeded size, **when** I compare every generated person name against a list of real public figures, **then** there are zero matches; names are built only from synthetic first/last-name parts.
6. **Given** a seeded database, **when** I look at a user's company affiliations, **then** their stints never overlap each other and every end date is after its start date.

**Concepts:** HLD 4.3 back-of-envelope estimation (sizing), LLD Template Method (one base generator, per-entity steps)
**Test cases:** one unit test per criterion against a 1k seed.

---

## S5 · Seed generator at scale (100k and 1M)

**As a** developer, **I want** the seeder to produce 100k and 1M users in reasonable time, **so that** Phase 2 can measure real slowdowns at realistic scale.

**Acceptance criteria**
1. **Given** an empty database, **when** I seed `1M`, **then** it finishes in under 15 minutes on my laptop _(placeholder)_ and all S4 criteria still hold.
2. **Given** a 1M seed, **when** I check graduates of one large college, **then** most of them are concentrated in a small number of companies (clustering).
3. **Given** the seeder is running, **when** I watch memory use, **then** it stays bounded (data is generated and written in batches, not built fully in memory first).

**Concepts:** Latency vs Throughput (batch inserts vs row by row)
**Test cases:** criterion 2 as an automated check; criteria 1 and 3 measured and noted.

---

## S6 · Benchmark protocol in the repo

**As a** developer, **I want** the benchmark protocol and the `BENCHMARKS.md` template written down in the repo, **so that** every future performance claim is measured the same way and can't be bent later.

**Acceptance criteria**
1. **Given** the repo, **when** I open `docs/benchmark-protocol.md`, **then** it states: machine and Docker limits, a warm-up of at least 2 minutes, a fixed scenario, seed size and duration, at least 3 runs reporting median and spread, one change per comparison, and no local-vs-AWS comparison.
2. **Given** `BENCHMARKS.md`, **when** I open it, **then** it contains the entry template and nothing else yet.

**Concepts:** p99 Latency, Latency vs Throughput
**Test cases:** none (document).

---

## S7 · Load-test harness (k6)

**As a** developer, **I want** one command that runs a load-test scenario and records p50, p99, throughput and error rate, **so that** any change can be judged by numbers instead of feelings.

**Acceptance criteria**
1. **Given** the stack is up and a placeholder `/health` endpoint exists, **when** I run `make loadtest SCENARIO=smoke`, **then** k6 runs the warm-up, then the measured period, 3 times.
2. **Given** a finished run, **when** I open `BENCHMARKS.md`, **then** a new entry has been appended with p50, p99, req/s, error %, the median and spread of the 3 runs, and the machine and limit details.
3. **Given** the scenario files, **when** I read them, **then** search, profile-view and send-request scenarios exist (pointing at placeholder endpoints until Phase 1).

**Concepts:** Load Testing, p99 Latency, Latency vs Throughput
**Test cases:** run against a stub that sleeps a fixed time; check the recorded p50 is close to that sleep.

---

## S8 · Logging, metrics and tracing conventions

**As a** developer, **I want** a written convention plus a tiny reference service that logs in JSON with a correlation ID, exposes metrics and sends traces, **so that** Phase 1 code is observable from its first endpoint.

**Acceptance criteria**
1. **Given** a request to the reference service, **when** I look in Loki, **then** its log lines are JSON with level, timestamp, message and a correlation ID.
2. **Given** a request carrying an `X-Correlation-ID` header, **when** it's handled, **then** that same ID appears in every log line and in the trace for that request.
3. **Given** the metrics endpoint, **when** I read it, **then** no metric label uses an unbounded value (no user IDs or raw URLs as labels).
4. **Given** the convention doc, **when** I read it, **then** it defines when to use each log level and how logs are rotated.

**Concepts:** Structured Logging, Log Levels, Log Rotation, OpenTelemetry, Correlation IDs, Metrics Cardinality, Error Tracking
**Test cases:** integration test for criterion 2.

---

## S9 · CI pipeline

**As a** developer, **I want** GitHub Actions to lint, type-check, test and scan every pull request, **so that** nothing broken or leaky reaches `main`.

**Acceptance criteria**
1. **Given** a pull request, **when** CI runs, **then** ruff, mypy, pytest (with a coverage gate) and gitleaks all run, and any failure blocks the merge.
2. **Given** a commit that contains a fake AWS-style key, **when** CI runs, **then** gitleaks fails the build.
3. **Given** Dependabot is enabled, **when** a dependency has a known vulnerability, **then** a PR or alert is raised.
4. **Given** the Python tooling, **when** I check the repo, **then** a lockfile is committed and CI installs from it.

**Concepts:** Secret Scanning, Dependency Vulnerabilities, Lockfiles, Branch Protection
**Test cases:** criterion 2 is proven by a throwaway PR that should fail.

---

## S10 · Pre-commit hooks

**As a** developer, **I want** the same format, lint and secret checks to run on my laptop before each commit, **so that** I catch problems in seconds instead of waiting for CI.

**Acceptance criteria**
1. **Given** hooks are installed, **when** I try to commit a file containing a fake secret, **then** the commit is blocked with a message.
2. **Given** a badly formatted Python file, **when** I commit, **then** it's auto-formatted or the commit is blocked.

**Concepts:** Secret Scanning
**Test cases:** manual checks 1–2.

---

## Phase 0 exit criteria (from the roadmap)
- `docker compose up` starts the full stack (S3)
- Seeding 1M users works (S5)
- One command runs a load test and records p50/p99/throughput (S7)
- You can explain why p99 matters more than the average
