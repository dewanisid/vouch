# 0005. One institutions table for companies and colleges, with aliases
Date: 2026-11-24 · Status: accepted

## Context
People work at companies and study at colleges. Vouch uses both the same way:
an affiliation is a person at a place between two dates, both have spelling
variants ("IITB", "IIT Bombay") that must match, typing should suggest the right
one, duplicates must be mergeable, and search ranks "worked with you" and
"studied with you" together. Some places are both: IIT Bombay is a college and an
employer. Phase 1 needs almost no fields that only one kind has.

## Options considered
1. Separate `companies` and `colleges` tables — each kind can have its own
   fields / affiliations need two tables or two nullable keys; aliases,
   matching and merging are built twice; a university exists twice, unlinked.
2. One `institutions` table with a `kind` column and every field, unused ones
   left empty — one place to point at / messy when the kinds differ a lot.
3. One `institutions` table for the shared fields, plus a side table per kind
   for kind-only fields — one place to point at, and separate homes for
   differing fields / an extra join when those fields are read.

Spelling variants: a free-text name on each affiliation (grouping by matching
text later is unreliable) vs one canonical row plus an `institution_aliases`
table (each spelling maps to exactly one institution).

## Decision
One `institutions` table with `kind` (`company` or `college`), a canonical
`name`, and an `institution_aliases` table with case-insensitive unique aliases.
Side tables (option 3) are added only when a kind-only field is needed.
Siddharth first chose option 1 because the fields might differ; checking the
Phase 1 features showed they almost don't.

## Consequences
Easier: affiliations, matching, merging and search are written once; every
spelling lands on one row.
Harder: a place that is both college and employer keeps a single `kind`.
Watch: when a kind-only field appears, add a side table rather than nullable
columns.
