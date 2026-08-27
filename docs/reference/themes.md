# Working with themes

The profile wears one of 47 looks, drawn fresh each morning. Everything here runs on
Python 3.11+ with no installs, from the repository root. Every command below was run
before it was written down.

## See them all

```bash
python scripts/profile_theme.py preview --out preview.html
```

Opens a self-contained page: every theme in the sidebar grouped by family, the full
README laid out as GitHub renders it, and a **GitHub dark / GitHub light** toggle so you
can check both grounds. There is a "Surprise me" button. This is the fastest way to
judge a change, and it is the file to look at before committing one.

Add `--snake snake.svg` to have the contribution snake recoloured per theme in the
preview too. Without it the snake slot is simply empty.

## Change one theme

Every look is one entry in `themes/catalog.py`. Edit it, then:

```bash
python scripts/profile_theme.py build          # re-render all 47 into assets/themes/
python scripts/profile_theme.py preview --out preview.html
python scripts/check_readme.py                 # the 14-rule contract
```

`build` is safe to run any time; it is deterministic, so a rebuild with no catalog change
produces no diff.

To see just the markdown a theme produces, without the browser:

```bash
python scripts/profile_theme.py render --theme frost --data fixture --out /tmp/frost.md
```

`--data fixture` uses built-in sample facts, so it needs no token and no network. For the
real numbers:

```bash
GH_TOKEN=$(gh auth token) python scripts/profile_surface.py data --user itxcrusher --out data.json
python scripts/profile_theme.py render --theme frost --data data.json --out /tmp/frost.md
```

## Add a theme

Append a `T(...)` entry to `themes/catalog.py`. Copy the nearest existing theme and change
it; the fields are documented at the top of that file. The parts that matter:

| field | what it does |
| --- | --- |
| `dark` / `light` | `bg`, `bg2`, `ink`, `muted`, `acc`, `acc2`. Both variants are designed, not inverted |
| `hero` | the banner: `back` / `mid` / `front` motif layers from `themes/motifs.py` |
| `header` | how the two section-heading images are drawn |
| `labels` | the wording of those headings, so "what is public" can become something else |
| `signoff` | the closing line image |
| `text` | `rows`, `chip`, `fence`, `alert`, `sep`: the native-markdown half |

Then `build`, `preview`, `check_readme.py`, and commit the catalog change together with
the rebuilt assets.

Three guards fire at import, before anything renders, so a new theme cannot ship broken:

- **`alert` must be `NOTE` or `TIP`.** `WARNING`, `CAUTION` and `IMPORTANT` render with
  alarm styling, and the callout they wrap is the invitation to verify the work. A red
  danger box on that block reads as a problem report.
- **`sep` may not be `*` or `_`.** Both are markdown emphasis characters, and between the
  header links they read as footnote markers.
- **Light accents are darkened** until they clear 7:1 against the light ground. Dark
  variants get their presence from glow against a deep ground; on white the only
  equivalent is ink density, so the accent has to go darker rather than lighter.

`check_readme.py` re-checks the last of these as R14 on what actually ships.

## Remove a theme

```python
T("slug", ..., disabled=True)
```

It leaves the draw immediately. Its assets stay on disk so any older commit still renders.
Deleting the entry outright also works, but then a rebuilt old README points at files that
no longer exist.

## Check the rotation

```bash
python scripts/profile_theme.py schedule --days 30        # the next 30 picks
python scripts/profile_theme.py schedule --mode seasonal --days 30
python scripts/profile_theme.py report                    # per-theme contrast, both variants
```

The draw is a pure function of the date and the pool, so a re-run on the same day is a
no-op and tomorrow's pick can be known today. A theme cannot return within 7 days.

A few dates draw from their own pool instead, listed in `SPECIAL_DAYS` in
`themes/rotate.py`: Halloween, New Year, and the account's own anniversary. Add a date
there and it works with no other change.

## Wear one today, out of turn

```bash
gh workflow run profile.yml -f theme=frost
```

Runs the live workflow immediately with that theme. Tomorrow's scheduled draw resumes on
its own. To pin one permanently instead, set `MODE = "fixed:frost"` in `themes/rotate.py`.

## What the daily run actually does

`.github/workflows/profile.yml` at 03:17 UTC: draw today's theme, regenerate the
contribution snake in that theme's palette, read the facts from the GitHub API, lay the
page out, run the 14-rule contract, commit only if the page changed. It commits as
`github-actions[bot]`, never as the account owner, so a daily rebuild cannot manufacture
contribution squares on the graph the page uses as evidence.

If it fails it opens one reusable issue titled "profile automation is failing". Nobody
reads the Actions tab of a profile repo, so that issue is the entire signal.
