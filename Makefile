# Shortcuts for common tasks. Run `make <target>`.

SCENARIO ?= smoke

.PHONY: loadtest loadtest-quick

# Protocol run: 3 x (2 min warm-up + measured period), then append to BENCHMARKS.md.
loadtest:
	uv run python -u scripts/loadtest.py $(SCENARIO)

# Three short runs to try a scenario. Writes nothing.
loadtest-quick:
	uv run python -u scripts/loadtest.py $(SCENARIO) --quick
