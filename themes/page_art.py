"""Composition: which blocks go in which slice, and how the README references them.

Three slices, and the split is forced by what GitHub allows rather than by taste.

  top    the opening statement and the trust callout.  Static per theme.
  work   what is public, the repository cards, the stack.  Depends on live API data,
         so it is rewritten on every run into assets/today/ and never committed per
         theme. That directory is the only place the contract permits a number inside
         an image, because it is the only place a number cannot go stale.
  close  the contact lines.  Static per theme.

A link cannot live inside the artwork (`<map>`/`<area>` are stripped, so clickable
regions are impossible and only a whole image can be a link), so every destination is
gathered into one markdown strip beneath the art. Under that sits a collapsed copy of
the whole page as plain text, which is what keeps the facts alive when images do not
load, and what R3 checks.
"""
from themes.fullpage import Flow
from themes.textpanel import BANDS

PAGES_DIR = "assets/pages"
TODAY_DIR = "assets/today"


def _top(theme, variant, band, content):
    fl = Flow(theme, variant, band, edge_pos="top")
    fl.space(fl.base * 0.6)
    fl.paras(content["intro"], fl.s["body"], fl.p["ink"])
    fl.space(fl.base * 0.9)
    fl.note(content["cta_title"], content["cta_body"], content["cta_cmd"], content["cta_after"])
    return fl.render("Opening statement and the runnable check",
                     desc=" ".join(content["intro"]))


def _close(theme, variant, band, content):
    """The colophon. It used to be three muted lines floating on the ground, which made
    the page trail off; now the name carries ink, the handle carries the accent, and the
    contact rows keep their labels muted and their values in ink, so the ending has the
    same hierarchy as everything above it."""
    fl = Flow(theme, variant, band, edge_pos="bottom")
    fl.space(fl.base * 0.7)
    fl.run([(content["name"], fl.p["ink"], 700, None),
            ("  " + content["handle"], fl.p["acc"], 700, "mono")], fl.s["body"])
    fl.space(fl.base * 0.55)
    rows = [("agency", "infraforge.agency"),
            ("site", "muhammadhassaanjaved.com"),
            ("direct", content["email"])]
    label_w = max(width_of(fl, lab) for lab, _ in rows) + fl.base * 0.9
    for lab, val in rows:
        y = fl.y + fl.s["micro"]
        fl.fg.append(lambda c, lab=lab, y=y: c.text(fl.x, y, lab, fl.s["micro"],
                                                    fl.p["muted"], fl.font, 500))
        fl.fg.append(lambda c, val=val, y=y: c.text(fl.x + label_w, y, val, fl.s["micro"],
                                                    fl.p["ink"], "mono", 500))
        fl.y = y + fl.s["micro"] * 0.75
    fl.space(fl.base * 0.4)
    return fl.render("Contact: how to reach %s" % content["name"],
                     desc=" ".join(content["footer"]))


def width_of(fl, text):
    from themes.svg import width
    return width(text, fl.font, 500, fl.s["micro"])


def _work(theme, variant, band, content, data, today):
    fl = Flow(theme, variant, band)
    fl.space(fl.base * 0.3)
    fl.section(theme["labels"]["public"])
    fl.wrap(content["stats"], fl.s["micro"], fl.p["muted"])
    fl.space(fl.base * 0.6)
    for i, row in enumerate(data["picked"], 1):
        meta = ", ".join(x for x in (row.get("lang") or "", "updated " + row["date"]) if x)
        fl.card(row["name"], row["desc"].rstrip("."), meta, index=i)
    if content["evidence"]:
        fl.space(fl.base * 0.15)
        fl.wrap(content["evidence"], fl.s["micro"], fl.p["muted"])
    fl.space(fl.base * 0.3)
    fl.wrap("Generated %s from the GitHub API." % today, fl.s["micro"], fl.p["muted"])

    fl.section(theme["labels"]["stack"])
    fl.wrap(content["stack_intro"], fl.s["micro"], fl.p["muted"])
    fl.space(fl.base * 0.7)
    fl.pill_rows(content["stack"])
    fl.space(fl.base * 0.35)
    fl.wrap(content["upstream"], fl.s["micro"], fl.p["muted"])
    return fl.render("%s and %s" % (theme["labels"]["public"], theme["labels"]["stack"]),
                     desc=content["stats"])


def build_static(theme, content):
    """{filename: svg} for the two slices that never change with the API."""
    out = {}
    for variant in ("dark", "light"):
        for key, _m, _w, _s in BANDS:
            out["top-%s-%s.svg" % (key, variant)] = _top(theme, variant, key, content)
            out["close-%s-%s.svg" % (key, variant)] = _close(theme, variant, key, content)
    return out


def build_work(theme, content, data, today):
    """{filename: svg} for the data-dependent slice. Rewritten every run."""
    out = {}
    for variant in ("dark", "light"):
        for key, _m, _w, _s in BANDS:
            out["work-%s-%s.svg" % (key, variant)] = _work(theme, variant, key, content,
                                                           data, today)
    return out


def picture(directory, stem, alt):
    """Eight sources: four viewport bands times two colour schemes, narrowest first."""
    parts = ["<picture>"]
    for key, media, _w, _s in BANDS:
        dark = "(prefers-color-scheme: dark)" + ((" and " + media) if media else "")
        parts.append('<source media="%s" srcset="./%s/%s-%s-dark.svg">' % (dark, directory, stem, key))
        if media:
            parts.append('<source media="%s" srcset="./%s/%s-%s-light.svg">'
                         % (media, directory, stem, key))
    last = BANDS[-1][0]
    parts.append('<img src="./%s/%s-%s-light.svg" width="100%%" alt="%s" />'
                 % (directory, stem, last, alt))
    parts.append("</picture>")
    return "".join(parts)
