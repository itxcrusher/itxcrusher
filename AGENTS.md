# AGENTS.md - itxcrusher

The GitHub profile README surface for `@itxcrusher` (Muhammad Hassaan Javed). This is
the special user-named repo GitHub renders on the profile page, so whatever is on `main`
is what visitors see at github.com/itxcrusher.

## What this repo is

- A single public page, plus the small amount of Python and YAML that keeps it true.
- **It is no longer content-only.** That claim used to be in this file and was already
  false (a snake workflow had been running here for 9,000+ runs). There are now three
  workflows and two stdlib-only Python scripts. Do not reintroduce the "no code here"
  rule; reason about the code instead.
- Low-churn by design. The generated block refreshes itself; the hand-authored prose
  changes only when something about the work changes.
- Part of the `x:\itxcrusher\` workspace, cloned under `repos/itxcrusher`. The channel
  docs (strategy, the build spec, provenance) live at
  `x:\itxcrusher\docs\channels\github\`. Workspace rules: `x:\itxcrusher\AGENTS.md`.
  Global rules: `~/.claude/CLAUDE.md`.

## The one rule everything else serves

**Everything on the page is either true and checkable, or it is not on the page.**

This profile is a trust surface for InfraForge client conversion, not a resume and not
a showcase. Its central bet is the verification CTA: a stranger can clone `ripple-proof`
and audit it offline in a minute. If that ever stops working, that block comes out the
same day.

## Layout

| Path | What it is |
| --- | --- |
| `README.md` | The page. One hand-authored region plus one generated block between `<!-- PUBLIC_SURFACE:START -->` and `<!-- PUBLIC_SURFACE:END -->`. |
| `assets/hero.svg` | The only authored image. Identity only: name and handle. |
| `scripts/profile_surface.py` | Renders the generated block from the GitHub API, then splices it. Python stdlib only. |
| `scripts/check_readme.py` | Enforces the rendering contract R1-R11. Run it before every push. |
| `.github/workflows/profile.yml` | Daily: snake, render, splice, commit. One concurrency group. |
| `.github/workflows/readme-check.yml` | Runs the contract check on push and PR. |
| `.github/workflows/profile-review.yml` | Opens a quarterly review issue. |
| `docs/reference/profile-review.md` | The review checklist that issue carries. |

## The rendering contract

`scripts/check_readme.py` is the specification. Read it before editing anything. The
rules that bite most often:

- **R2 third-party image budget is ZERO.** The only permitted absolute image host is
  `raw.githubusercontent.com/itxcrusher/itxcrusher/output/`, which is this repo's own
  branch. Every stats card, streak card, language card, trophy and activity graph was
  removed for cause: two of them were rendering visible error text on the live profile,
  and the canonical `github-readme-stats` instance is deprecated and 503.
- **R3 text survives image death.** Strip every `<img>` and the page must still say who
  this is, what he does, and how to verify it. Never put content in an image.
- **R5 plain ASCII only.** No em-dashes, no curly quotes, no bullet glyphs, anywhere in
  `README.md` or any SVG. Showcased repo *descriptions* are injected verbatim, so they
  must be ASCII too; fix the repo field, not the generator.
- **R8 no facts inside images.** No counts, dates, statuses or percentages in an SVG. A
  fact frozen in a raster has to be hand-redrawn to stay true, which is how every rotted
  element on the old profile got that way.
- **R9 single source of truth.** Project one-liners live in the repo `description`
  field, stacks in `topics`, demo links in `homepageUrl`. Never restate them here.

## How to edit

- **Prose, links, the stack fence:** edit `README.md` outside the markers, then run
  `python scripts/check_readme.py` from the repo root. It must exit 0.
- **Which projects appear:** do not edit the README. Add or remove the `showcase` topic
  on the repo itself (`gh repo edit itxcrusher/<repo> --add-topic showcase`). The
  `showcase-lead` topic pins one to the top. The next run picks it up.
- **A project's one-liner:** edit that repo's `description`, not this README.
- **Never hand-edit between the markers.** The next run overwrites it.
- Test the generator locally with `GH_TOKEN=$(gh auth token) python scripts/profile_surface.py render --user itxcrusher --out block.md`.

## Branch model

- `main` renders on the profile. `output` holds exactly one orphan commit containing
  `snake.svg` and is force-pushed by the workflow; never branch from it or merge it.
- Substantive rewrites go on a working branch first, because there is no staging
  environment for a profile page. Push the branch, view the README at
  `github.com/itxcrusher/itxcrusher/blob/<branch>/README.md` to get real GitHub
  rendering, then fast-forward `main`.
- Trivial prose fixes may go straight to `main` once `check_readme.py` passes.

## What NOT to do

- Do not rename the repo. It must stay `itxcrusher` for GitHub to treat it as the
  profile README.
- Do not add a third-party image widget. See R2. This is the rule most likely to be
  broken by someone who has just found a nice-looking card.
- Do not add a PAT. Everything the workflow needs is readable with `GITHUB_TOKEN`. A PAT
  is account-wide across 70+ repos and three orgs, and it re-arms the
  workflow-triggers-workflow recursion that `GITHUB_TOKEN` suppresses by design.
- Do not let a workflow commit as `itxcrusher`. It commits as `github-actions[bot]` on
  purpose; otherwise it manufactures a green square a day on the exact contribution
  graph this page uses as evidence.
- Do not put a star count, follower count or trophy anywhere. The numbers are near zero
  and no layout rescues that.
- Do not add `Co-Authored-By` or any AI-attribution trailer to commits.
