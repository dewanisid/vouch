# 0002. Keep private notes out of the public repo
Date: 2026-11-04 · Status: accepted

## Context
The repo is public, as a record of the work. Three working files don't belong
in it: `PROJECT_CONTEXT.md` (instructions for the AI assistant),
`PROGRESS.md` (a personal study log) and `STORIES.md` (interview stories that
draw on situations from a real job). Anything committed and pushed stays in
history and has to be treated as public for good.

## Options considered
1. Commit everything — files get history and a backup / exposes private notes
   and details about other people at work.
2. Git-ignore them and keep them on the laptop — private, and impossible to
   commit by accident / no history, and no backup from git.
3. A separate private repo for the notes — private with history and a backup /
   a second repo to keep in step, more work than the notes need today.

## Decision
Git-ignore them. It is the simplest option that guarantees privacy, and a
private repo can still be added later without changing this one.

## Consequences
Easier: committing without checking each file, because the rules are in `.gitignore`.
Harder: these files have no history and are lost if the laptop is lost.
Watch: set up a backup (iCloud or a private repo) before these notes hold
anything hard to recreate.
