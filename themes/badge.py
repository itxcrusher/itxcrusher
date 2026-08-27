"""Themed technology badges.

Why these exist. The banner SVGs are `width="100%"`, so GitHub scales them with the
README column, and that column was measured across viewports at 846px down to 238px:
a 3.5x range. Type inside a scaled image cannot hold one readable size across that,
which is why the banners carry display type only and every sentence on the page stayed
as GitHub-grey markdown.

A badge escapes that. It is `height`-pinned, and GitHub turns `height="28"` into
`height:auto; max-height:28px` alongside `max-width:100%`. Keep the badge narrower than
the narrowest measured column and neither cap ever binds, so it renders at exactly its
authored size on every viewport. One SVG unit is one pixel, and 14-unit type is 14px
everywhere. That is the whole trick, and it is the only way real words on this page get
to wear the theme.

One file per theme, per colour scheme, per label. They are static, so they are built
once and committed rather than generated per run: the gallery has to render all 47
themes, and a badge that only exists for today's theme would break the other 46.
"""
from themes.svg import Canvas, darken, f, fo, lighten, mix, so, width

H = 28
FONT = 14
# The narrowest README column measured on the live profile (320px viewport). A badge
# wider than this would hit GitHub's max-width and start scaling, which is exactly the
# behaviour these exist to avoid.
MAX_W = 238

PAD = 11
MARK = 16  # left cell holding the family marker


def _shape(family):
    """Corner radius and marker, keyed off the family the theme already declares."""
    if family == "tech":
        return 2, "square"
    if family == "gritty":
        return 0, "slash"
    if family == "nature":
        return H / 2.0, "dot"
    return 5, "spark"


def _font(theme):
    return theme["header"].get("font", "sans")


def _marker(c, kind, x, cy, col):
    if kind == "square":
        c.rect(x - 3.5, cy - 3.5, 7, 7, col, 1, 1)
    elif kind == "slash":
        c.line(x - 3, cy + 4, x + 3, cy - 4, col, 1, 2)
    elif kind == "dot":
        c.circle(x, cy, 3.5, col)
    else:
        c.poly([(x, cy - 4.5), (x + 4, cy), (x, cy + 4.5), (x - 4, cy)], col)


def measure(theme, label, role):
    kind = _font(theme)
    weight = 700 if role == "group" else 500
    tw = width(label, kind, weight, FONT)
    mark = 0 if role in ("link", "lang") else MARK
    return PAD + mark + tw + PAD


def badge(theme, variant, label, role="token"):
    """One pill. `role` is 'group' (accent-filled, the category) or 'token' (outlined)."""
    p = theme[variant]
    w = measure(theme, label, role)
    if w > MAX_W:
        raise ValueError("badge %r is %.0f units, over the %d cap" % (label, w, MAX_W))
    rx, mark = _shape(theme["family"])
    kind = _font(theme)
    weight = 700 if role == "group" else 500
    c = Canvas(H, label, seed="%s:%s:%s" % (theme["slug"], variant, label),
               w=int(round(w)), min_font=FONT)

    if role == "group":
        ground = p["acc"]
        ink = p["bg"] if _readable(p["bg"], ground) else p["ink"]
        c.rect(0, 0, c.w, H, ground, 1, rx)
        _marker(c, mark, PAD + MARK / 2.0, H / 2.0, ink)
        c.text(PAD + MARK, H / 2.0 + FONT * 0.36, label, FONT, ink, kind, weight)
        return c.render()

    if role in ("link", "lang"):
        # No marker: these carry the longest labels on the page ("muhammadhassaanjaved.com"
        # is 230 of the 238 units available in the widest theme font) and the marker cell
        # would push them past the cap into GitHub's scaler. A link pill speaks in the
        # accent so it still reads as something to click; a language pill stays muted so
        # a repository row is not six competing colours.
        ink = p["acc"] if role == "link" else p["muted"]
        ground = mix(p["bg"], p["bg2"], 0.6 if role == "link" else 0.35)
        c.rect(0, 0, c.w, H, ground, 1, rx)
        c.add('<rect x="0.75" y="0.75" width="%s" height="%s" rx="%s" fill="none" %s/>'
              % (f(c.w - 1.5), f(H - 1.5), f(max(0, rx - 0.75)),
                 so(p["acc"], 0.65 if role == "link" else 0.3, 1.5)))
        c.text(c.w / 2.0, H / 2.0 + FONT * 0.36, label, FONT, ink, kind, weight, "middle")
        return c.render()

    # Token: the theme's raised surface, an accent hairline, accent marker. Deliberately
    # quieter than the group pill so a row reads as one label plus its members.
    ground = mix(p["bg"], p["bg2"], 0.75)
    c.rect(0, 0, c.w, H, ground, 1, rx)
    c.add('<rect x="0.75" y="0.75" width="%s" height="%s" rx="%s" fill="none" %s/>'
          % (f(c.w - 1.5), f(H - 1.5), f(max(0, rx - 0.75)), so(p["acc"], 0.55, 1.5)))
    _marker(c, mark, PAD + MARK / 2.0, H / 2.0, p["acc"])
    c.text(PAD + MARK, H / 2.0 + FONT * 0.36, label, FONT, p["ink"], kind, weight)
    return c.render()


def _readable(fg, bg):
    from themes.svg import contrast
    return contrast(fg, bg) >= 4.5


def slug(label):
    out = []
    for ch in label.lower():
        out.append(ch if ch.isalnum() else "-")
    s = "".join(out)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


# Languages are live data, so a repository whose language is not in this list simply
# keeps its plain-text label rather than pointing at a badge that was never built.
LANGUAGES = ["Python", "HCL", "Shell", "TypeScript", "JavaScript", "Go", "Rust",
             "Dockerfile", "Java", "Ruby"]


def build_theme(theme, groups, links=()):
    """Return {relative path: svg} for every badge one theme needs."""
    out = {}
    for variant in ("dark", "light"):
        for label, values in groups:
            out["%s/%s.svg" % (variant, slug(label))] = badge(theme, variant, label, "group")
            for v in values:
                out["%s/%s.svg" % (variant, slug(v))] = badge(theme, variant, v, "token")
        for label in links:
            out["%s/link-%s.svg" % (variant, slug(label))] = badge(theme, variant, label, "link")
        for label in LANGUAGES:
            out["%s/lang-%s.svg" % (variant, slug(label))] = badge(theme, variant, label, "lang")
    return out
