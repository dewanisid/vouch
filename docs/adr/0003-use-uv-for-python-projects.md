# 0003. Use uv to manage the Python project
Date: 2026-11-06 · Status: accepted

## Context
Python code needs its libraries installed at exact, repeatable versions on a
laptop and in CI. The project needs a virtual environment and a committed
lockfile, so that a fresh clone installs what was tested.

## Options considered
1. pip with a requirements file — ships with Python / exact locking of indirect
   dependencies needs an extra tool.
2. Poetry — mature, with a lockfile / slower, and one more tool to learn its own
   way of working.
3. uv — one tool for the virtual environment, dependencies and lockfile, and
   fast / newer, so there are fewer years of community answers.

## Decision
uv: one tool covers the whole job, and `uv run` keeps the environment in sync
without extra steps.

## Consequences
Easier: setup on a fresh clone and in CI is a single command.
Harder: every contributor and the CI image needs uv installed.
Watch: Java takes over the application from Phase 1.5, so uv's job shrinks to
tooling and the AI service.
