# AGENTS.md - itxcrusher

The GitHub profile README surface for `@itxcrusher` (Muhammad Hassaan Javed). This is the special user-named repo GitHub renders on the profile page, so `README.md` is the one file that matters: whatever it contains is what visitors see at github.com/itxcrusher.

## What this repo is

- Content-only. No build step, no code, no dependencies.
- Low-churn: it changes only when the profile copy or the stats/graph widgets change.
- Part of the `x:\itxcrusher\` workspace, cloned under `repos/itxcrusher`. Workspace-level rules live in `x:\itxcrusher\AGENTS.md`; global rules in `~/.claude/CLAUDE.md`.

## Branch model

- `main` only. There is no `dev` branch and no deploy gate; GitHub renders `main` directly on the profile.
- Small edits commit straight to `main`.

## How to edit

- Edit `README.md`. That is the whole job.
- The stats cards, streak, language graph, activity graph, snake animation, and visitor counter are third-party image widgets referenced by URL; adjust their query params in place if needed.
- Keep punctuation plain ASCII (straight quotes, no em-dashes, no curly apostrophes).

## What NOT to do

- Do not rename the repo. It must stay `itxcrusher` for GitHub to treat it as the profile README.
- Do not add source code, CI, or a build here; it is a single markdown surface.
- Do not add `Co-Authored-By` / AI-attribution trailers to commits.
