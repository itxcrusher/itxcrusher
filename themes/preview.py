"""Two ways to look at every theme before it ships.

  gallery_markdown(themes)   assets/pages/README.md, browsable on GitHub
  preview_html(themes, root) one self-contained local page, every theme, both schemes

Both show the two STATIC slices. The data-dependent slice is deliberately absent: it
carries live repository counts and dates, and only today's theme has a current copy of
it, so rendering 46 others here would put stale numbers on a public page.

This file used to be ten times longer. Most of it was a markdown-subset-to-HTML
converter whose whole job was to imitate the way GitHub lays out a README, because the
page was a README with artwork in it. The page is now artwork; there is nothing left to
imitate.
"""
import base64
import os

from . import page_art
from .catalog import FAMILIES
from .textpanel import BANDS


def gallery_markdown(themes, n_active):
    out = [
        "# The looks", "",
        "This profile is drawn, not written. The page body is a small number of long SVGs "
        "rather than markdown, because GitHub strips `style` and `class` from a README and "
        "an SVG is the only surface left that can carry a colour. A different look is drawn "
        "every morning: a date-seeded draw from the %d below, never the same as yesterday, "
        "made by `.github/workflows/profile.yml` at 03:17 UTC. Every asset is a committed "
        "SVG in this directory; nothing is fetched from a third party." % n_active, "",
        "Each look changes the ground, the ink, the accent, the panel and card treatment, "
        "the pill shape, the type family, the section labels, the sign-off and the "
        "contribution snake colours. The words are the same every day.", "",
        "Below is each look's opening panel. The middle panel carries live repository data "
        "and only today's look has a current copy of it, so it is not shown here.", "",
    ]
    for fam, title in FAMILIES.items():
        rows = [t for t in themes if t["family"] == fam]
        if not rows:
            continue
        out.append("## " + title)
        out.append("")
        for t in rows:
            out.append("### %s" % t["name"])
            out.append("")
            out.append(page_art.picture(t["slug"], "top",
                                        "%s look: the opening panel, showing this theme's "
                                        "ground, ink, accent and panel treatment" % t["name"]))
            out.append("")
            out.append("%s <sub>family: %s, type: %s%s</sub>" % (
                t["tagline"], t["family"], t["header"].get("font", "sans"),
                ", disabled" if t.get("disabled") else ""))
            out.append("")
    out.append("To add one: append an entry to `themes/catalog.py`, run "
               "`python scripts/profile_theme.py build`, look at the result here, commit.")
    out.append("")
    md = "\n".join(out)
    assert all(ord(ch) < 128 for ch in md)
    return md


def _uri(path):
    with open(path, "rb") as fh:
        return "data:image/svg+xml;base64," + base64.b64encode(fh.read()).decode("ascii")


def preview_html(themes, root, band="lg"):
    """Every theme, both colour schemes, side by side, in one dependency-free file.

    Reads the built SVGs off disk rather than re-rendering them, so what is on screen is
    byte for byte what will ship.
    """
    width = dict((k, w) for k, _m, w, _s in BANDS)[band]
    cards = []
    for t in themes:
        d = os.path.join(root, t["slug"])
        pair = []
        for variant in ("dark", "light"):
            cell = []
            for stem in ("top", "close"):
                p = os.path.join(d, "%s-%s-%s.svg" % (stem, band, variant))
                if os.path.isfile(p):
                    cell.append('<img src="%s">' % _uri(p))
            pair.append('<div class="v %s">%s</div>' % (variant, "".join(cell)))
        cards.append('<section><h2>%s <small>%s / %s</small></h2><div class="pair">%s</div>'
                     "</section>" % (t["name"], t["family"], t["slug"], "".join(pair)))
    return (
        "<!doctype html><meta charset=utf-8><title>Theme preview</title>"
        "<style>"
        "body{margin:0;padding:24px;background:#161b22;color:#e6edf3;"
        "font:14px/1.5 ui-sans-serif,system-ui,sans-serif}"
        "h1{font-size:20px;margin:0 0 4px}p.lede{color:#8b949e;margin:0 0 24px}"
        "section{margin:0 0 40px}h2{font-size:16px;margin:0 0 8px}"
        "h2 small{color:#8b949e;font-weight:400}"
        ".pair{display:flex;gap:16px;align-items:flex-start}"
        ".v{flex:1;min-width:0;padding:12px;border-radius:8px}"
        ".v.dark{background:#0d1117}.v.light{background:#fff}"
        ".v img{display:block;width:100%%;max-width:%dpx}"
        "</style>"
        "<h1>%d themes, %s band, both colour schemes</h1>"
        "<p class=lede>Opening and closing panels, read from the built files. The middle "
        "panel is data-dependent and only exists for today's theme.</p>%s"
        % (width, len(themes), band, "".join(cards)))
