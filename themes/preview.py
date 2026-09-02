"""Two ways to look at every theme before it ships.

  gallery_markdown(themes)   assets/pages/README.md, browsable on GitHub
  preview_html(themes)       one local page: every theme's COMPLETE page, both schemes

The gallery shows the opening panel only, because it is public and the data-dependent
slice would carry stale numbers for every theme but today's. The local preview has no
such constraint: it renders the whole page on fixture data, for review before a change
ships.

This file used to be ten times longer. Most of it was a markdown-subset-to-HTML
converter whose whole job was to imitate the way GitHub lays out a README, because the
page was a README with artwork in it. The page is now artwork; there is nothing left to
imitate.
"""
import base64

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


def _b64(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def preview_html(themes, band="lg", only=None):
    """Every theme as the COMPLETE page it would ship as, both colour schemes, in one
    dependency-free file: hero, opening slice, work slice on fixture data, sign-off
    band and colophon, stacked exactly as the README stacks them.

    Rendered from the engine directly rather than read off disk, so it previews the
    code as it is now, built or not. The work slice uses fixture data, which is why
    this file is never committed: its numbers are sample numbers.
    """
    from . import page as P, page_art as A, render as R
    data = P.fixture_data()
    content = P.art_content(data, data["today"])
    picked = [t for t in themes if not only or t["slug"] in only]
    sections = []
    for t in picked:
        cols = []
        for v in ("dark", "light"):
            imgs = [
                R.hero(t, v),
                A._top(t, v, band, content),
                A._work(t, v, band, content, data, data["today"]),
                R.signoff(t, v),
                A._close(t, v, band, content),
            ]
            cols.append('<div class="v %s">%s</div>' % (
                v, "".join('<img src="%s">' % _b64(x) for x in imgs)))
        sections.append(
            '<section id="%s"><h2>%s <small>%s &middot; %s &middot; header %s &middot; rows %s</small></h2>'
            '<div class="pair">%s</div></section>'
            % (t["slug"], t["name"], t["family"], t["slug"], t["header"].get("style", "rule"),
               t["text"].get("rows", "list"), "".join(cols)))
    nav = " ".join('<a href="#%s">%s</a>' % (t["slug"], t["name"]) for t in picked)
    width = dict((k, w) for k, _m, w, _s in BANDS)[band]
    return (
        "<!doctype html><meta charset=utf-8><title>Theme preview</title>"
        "<style>"
        "body{margin:0;padding:20px 24px 60px;background:#161b22;color:#e6edf3;"
        "font:14px/1.5 ui-sans-serif,system-ui,sans-serif}"
        "h1{font-size:20px;margin:0 0 6px}p.lede{color:#8b949e;margin:0 0 14px}"
        "nav{position:sticky;top:0;background:#161b22;padding:10px 0;margin:0 0 20px;"
        "border-bottom:1px solid #30363d;line-height:2;z-index:2}"
        "nav a{color:#8b949e;text-decoration:none;margin-right:12px;font-size:12px}"
        "nav a:hover{color:#e6edf3}"
        "section{margin:0 0 48px;scroll-margin-top:70px}h2{font-size:16px;margin:0 0 8px}"
        "h2 small{color:#8b949e;font-weight:400;font-size:12px}"
        ".pair{display:flex;gap:16px;align-items:flex-start}"
        ".v{flex:1;min-width:0;padding:14px;border-radius:8px}"
        ".v.dark{background:#0d1117}.v.light{background:#fff}"
        ".v img{display:block;width:100%%;max-width:%dpx}"
        "</style>"
        "<h1>%d themes, %s band, dark and light, full page</h1>"
        "<p class=lede>Rendered from the engine as it is right now, on fixture data. "
        "Jump with the index; each section is the page exactly as the README stacks it.</p>"
        "<nav>%s</nav>%s"
        % (width, len(picked), band, nav, "".join(sections)))
