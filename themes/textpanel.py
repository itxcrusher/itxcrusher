"""Themed prose panels: the page's sentences, laid out inside an SVG.

The badge trick does not extend to prose. A badge holds its exact size because it is
height-pinned AND narrower than the narrowest README column (238px measured), so neither
of GitHub's two caps ever binds. A line of prose is wider than that, so it falls back to
width="100%" scaling, and the README column ranges 238px to 846px: a 3.5x swing that no
single font size survives.

What does work is serving a DIFFERENT image per viewport band. GitHub's sanitizer keeps
compound media queries inside <picture> (probed against its own markdown endpoint) and a
live four-way browser check confirmed themed-picture does not interfere with them. So each
band gets its own canvas width, its own type size, and its own line breaks, and the type
lands between roughly 13px and 32px everywhere instead of 10px on a phone or 60px on a
monitor.

The cost is real and is why this is used for statement prose, not for the whole page: text
inside an image cannot be selected, copied, or searched. Every panel therefore ships with
the same words as collapsed markdown underneath, and R3 proves that copy is there.
"""
from themes import motifs as M
from themes.svg import Canvas, f, mix, width

# (key, media query, canvas width, type size). Order matters: the first matching <source>
# wins, so these run narrowest-first and the last one is the default.
#
# The widths come from measuring the live profile, not from guessing. Below 768 the README
# column is the viewport minus 82. At 768 the profile switches to a side-by-side layout and
# the column DROPS to 398px, narrower than it was at 680, which is why the md band cannot
# simply continue the desktop scale.
BANDS = [
    ("xs", "(max-width: 479px)", 280, 16),
    ("sm", "(max-width: 767px)", 460, 18),
    ("md", "(max-width: 1199px)", 600, 22),
    ("lg", None, 900, 24),
]
BAND_BY_KEY = {b[0]: b for b in BANDS}

PAD_X = 34
PAD_Y = 30
RAIL = 6


def wrap(text, kind, weight, size, max_w):
    """Greedy word wrap using the same measurement the rest of the engine uses."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and width(trial, kind, weight, size) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def layout(paragraphs, kind, weight, size, max_w):
    out = []
    for i, para in enumerate(paragraphs):
        if i:
            out.append(None)  # paragraph break
        out.extend(wrap(para, kind, weight, size, max_w))
    return out


def _font(theme):
    return theme["header"].get("font", "sans")


def panel(theme, variant, band_key, paragraphs, title):
    key, _media, cw, size = BAND_BY_KEY[band_key]
    p = theme[variant]
    kind = _font(theme)
    inner = cw - PAD_X * 2 - RAIL
    lines = layout(paragraphs, kind, 400, size, inner)
    lh = round(size * 1.45)
    gap = round(size * 0.7)

    h = PAD_Y * 2
    for ln in lines:
        h += gap if ln is None else lh
    h = int(round(h))

    c = Canvas(h, title, seed="%s:%s:%s:intro" % (theme["slug"], variant, key),
               w=cw, min_font=size)
    # Quiet ground. This block is read, not looked at, so the theme shows up as tint and
    # rail rather than as motifs competing with the sentences.
    grad = c.lin_grad([(0, p["bg2"], 1), (1, p["bg"], 1)], x1=0, y1=0, x2=1, y2=1)
    c.add('<rect x="0" y="0" width="%s" height="%s" fill="%s"/>' % (f(cw), f(h), grad))
    c.rect(0, 0, RAIL, h, p["acc"], 0.9)

    x = PAD_X + RAIL
    y = PAD_Y + size
    for ln in lines:
        if ln is None:
            y += gap
            continue
        c.text(x, y, ln, size, p["ink"], kind, 400)
        y += lh
    return c.render()


def build_theme(theme, blocks):
    """blocks: {stem: (paragraphs, title)}. One SVG per stem, band and colour scheme."""
    out = {}
    for stem, (paragraphs, title) in blocks.items():
        for variant in ("dark", "light"):
            for key, _m, _w, _s in BANDS:
                out["%s-%s-%s.svg" % (stem, key, variant)] = panel(
                    theme, variant, key, paragraphs, title)
    return out


def picture(slug, stem, alt):
    """Eight sources: four viewport bands times two colour schemes, narrowest first."""
    d = "./assets/panels/" + slug
    parts = ["<picture>"]
    for key, media, _w, _s in BANDS:
        dark = "(prefers-color-scheme: dark)" + ((" and " + media) if media else "")
        parts.append('<source media="%s" srcset="%s/%s-%s-dark.svg">' % (dark, d, stem, key))
        if media:
            parts.append('<source media="%s" srcset="%s/%s-%s-light.svg">' % (media, d, stem, key))
    last = BANDS[-1][0]
    parts.append('<img src="%s/%s-%s-light.svg" width="100%%" alt="%s" />' % (d, stem, last, alt))
    parts.append("</picture>")
    return "".join(parts)
