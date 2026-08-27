# AGENTS.md - itxcrusher

The GitHub profile README surface for `@itxcrusher` (Muhammad Hassaan Javed). This is
the special user-named repo GitHub renders on the profile page, so whatever is on `main`
is what visitors see at github.com/itxcrusher.

## What this repo is

- A single public page that wears a different look every day, plus the Python and YAML
  that generate it and keep it true. Stdlib only; no installs anywhere in the pipeline.
- **Nothing here is content-only.** `README.md` is a build output. Do not hand-edit it;
  edit the source it is rendered from (see "How to edit") and re-render.
- Part of the `x:\itxcrusher\` workspace, cloned under `repos/itxcrusher`. The channel
  docs (strategy, the build spec, provenance) live at
  `x:\itxcrusher\docs\channels\github\`. Workspace rules: `x:\itxcrusher\AGENTS.md`.
  Global rules: `~/.claude/CLAUDE.md`.

## The one rule everything else serves

**Everything on the page is either true and checkable, or it is not on the page.**

This profile is a trust surface for InfraForge client conversion. Its central bet is the
verification CTA: a stranger can clone `ripple-proof` and audit it offline in a minute.
If that ever stops working, that block comes out the same day. The themes are costume;
the prose, the facts and the CTA are the same every day and never live inside an image.

## Layout

| Path | What it is |
| --- | --- |
| `README.md` | The page. Generated daily by the `profile` workflow. Carries a theme stamp on line 1 and the `PUBLIC_SURFACE` markers around the API-fed block. |
| `themes/catalog.py` | The 47 themes: palettes, motif stacks, type treatment, section labels, row/fence/callout styling, snake colours. Add a theme here. |
| `themes/motifs.py` | Text-free SVG scenery (rain, snow, traces, gears, ...). Seeded, seamless loops, slow motion. |
| `themes/svg.py` | Canvas, colour maths, contrast, and measured text fitting (Pillow when present, wide-font estimate otherwise). |
| `themes/render.py` | Composes hero (900x240), section headers (900x80) and the sign-off strip (900x64) from a catalog entry. |
| `themes/page.py` | The hand-authored prose, and the README renderer (row styles, fence languages, callout type). |
| `themes/rotate.py` | The daily draw: date-seeded, simulated from a fixed epoch, no repeat within seven days. Also weekly, seasonal and fixed modes. |
| `themes/preview.py` | The gallery README under `assets/themes/` and the self-contained preview page. |
| `assets/themes/<slug>/` | Eight committed SVGs per theme (hero, h-public, h-stack, signoff; dark and light). Never edited by hand: rebuilt from the catalog. |
| `assets/themes/README.md`, `index.json` | The browsable gallery and the list the checker validates the stamp against. |
| `scripts/profile_theme.py` | `build`, `pick`, `render`, `preview`, `schedule`, `report`. |
| `scripts/profile_surface.py` | Reads the facts from the GitHub API (`data`); the pre-theme `render`/`apply` path is kept for reference. |
| `scripts/check_readme.py` | Enforces the rendering contract R1-R13. Run it before every push. |
| `.github/workflows/profile.yml` | Daily: pick, snake in theme colours, facts, render, check, commit. One concurrency group. |
| `.github/workflows/readme-check.yml` | Runs the contract check on push and PR. |
| `.github/workflows/profile-review.yml` | Opens a quarterly review issue. |
| `docs/reference/profile-review.md` | The review checklist that issue carries. |

## The rendering contract

`scripts/check_readme.py` is the specification. Read it before editing anything. The
rules that bite most often:

- **R2 third-party image budget is ZERO.** The only permitted absolute image host is
  `raw.githubusercontent.com/itxcrusher/itxcrusher/output/`, this repo's own branch.
  Every stats card, streak card, language card, trophy and activity graph was removed
  for cause: two of them were rendering visible error text on the live profile.
- **R3 text survives image death.** Strip every `<img>` and the page must still say who
  this is, what he does, and how to verify it. Section headers are images, so their
  labels are decoration, never the only place a fact lives.
- **R5 plain ASCII only.** No em-dashes, no curly quotes, no bullet glyphs, in
  `README.md` or any SVG. The engine asserts this at render time.
- **R6 type floor.** Every SVG is 900 units wide and no rendered text is under 41 units,
  so a label survives the 308px phone column. Decorative "code" is drawn as rects.
- **R7 self-contained SVGs.** Gradients, filters, `url(#...)`, CSS keyframes and SMIL
  are allowed (verified under GitHub's CSP). Script, imports, external hrefs, embedded
  fonts and `prefers-color-scheme` are not; theme pairing is `<picture>`'s job.
- **R8 no facts inside images.** No counts, dates, statuses or percentages in an SVG.
- **R12 one theme at a time.** The stamp on line 1 and every asset path must agree.
- **R13 page weight.** The images the README references stay under 160 KB.

## How to edit

Full theme workflow, verified command by command: [`docs/reference/themes.md`](docs/reference/themes.md).

- **Prose, links, the stack:** edit `themes/page.py`, then re-render:
  `python scripts/profile_theme.py render --theme <slug> --data fixture` and run
  `python scripts/check_readme.py`. The workflow re-renders with live data next morning.
- **A theme:** edit its entry in `themes/catalog.py`, run
  `python scripts/profile_theme.py build`, look at `assets/themes/<slug>/` (or
  `python scripts/profile_theme.py preview --out preview.html --snake snake.svg` for the
  whole page in both colour modes), commit the rebuilt assets with the catalog change.
- **Retire a theme:** set `disabled=True` on it and rebuild. It leaves the draw; its
  assets stay so old commits still render.
- **See it live today:** run the `profile` workflow by hand with the `theme` input set
  to a slug. Tomorrow's draw resumes on its own.
- **Which projects appear:** do not edit the README. Add or remove the `showcase` topic
  on the repo itself (`gh repo edit itxcrusher/<repo> --add-topic showcase`). The
  `showcase-lead` topic pins one to the top.
- **A project's one-liner:** edit that repo's `description`, not this README.
- **Never hand-edit README.md.** The next run overwrites it.
- Test the facts path locally: `GH_TOKEN=$(gh auth token) python scripts/profile_surface.py data --user itxcrusher --out data.json`.

## Branch model

- `main` renders on the profile. `output` holds exactly one orphan commit containing
  `snake.svg`, `snake-dark.svg` and `snake-light.svg` and is force-pushed by the workflow; never
  branch from it or merge it.
- Substantive rewrites go on a working branch first, because there is no staging
  environment for a profile page. Push the branch, view the README at
  `github.com/itxcrusher/itxcrusher/blob/<branch>/README.md` to get real GitHub
  rendering, then fast-forward `main`.

## What NOT to do

- Do not rename the repo. It must stay `itxcrusher` for GitHub to treat it as the
  profile README.
- Do not add a third-party image widget. See R2.
- Do not add a PAT. Everything the workflow needs is readable with `GITHUB_TOKEN`.
- Do not let a workflow commit as `itxcrusher`. It commits as `github-actions[bot]` on
  purpose; otherwise it manufactures a green square a day on the exact contribution
  graph this page uses as evidence.
- Do not put a star count, follower count or trophy anywhere.
- Do not put text in a motif. Motifs are scenery; the type block is the only text.
- Do not add `Co-Authored-By` or any AI-attribution trailer to commits.
