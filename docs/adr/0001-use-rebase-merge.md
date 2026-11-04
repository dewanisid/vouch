# 0001. Use rebase merge for pull requests
Date: 2026-11-04 · Status: accepted

## Context
Every change reaches `main` through a pull request. GitHub offers three ways
to merge one, and the choice decides what the permanent history looks like.
The project is test-first and public, so readers should be able to see the
red → green → refactor sequence in the commits.

## Options considered
1. Squash merge — clean, one commit per PR / hides the test-first sequence.
2. Regular merge — keeps every commit / adds a merge commit per PR and a
   branching history that gets harder to read.
3. Rebase merge — keeps every commit in a straight line / commit IDs change on
   merge, and every commit message becomes permanent.

## Decision
Rebase merge: it is the only option that keeps both the individual commits
and a linear history.

## Consequences
Easier: seeing how a feature was built, commit by commit.
Harder: each commit must stand on its own, so no `wip` commits on a branch
that will be merged.
Watch: if commit quality slips and history gets noisy, revisit squash merge.
