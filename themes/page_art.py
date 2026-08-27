"""Composition: which blocks go in which slice, and how the README references them.

Three slices, and the split is forced by what GitHub allows rather than by taste.

  top    hero, the opening statement, the trust callout.  Static per theme.
  work   what is public, the repository cards, the stack.  Depends on live API data,
         so it is rewritten on every run into assets/today/ and never committed per
         theme. That directory is the only place the contract permits a number inside
         an image, because it is the only place a number cannot go stale.
  close  the sign-off and the contact lines.  Static per theme.

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
    fl = Flow(theme, variant, band)
    fl.hero(content["name"], content["handle"])
    fl.paras(content["intro"], fl.s["body"], fl.p["ink"])
    fl.space(fl.base * 0.9)
    fl.note(content["cta_title"], content["cta_body"], content["cta_cmd"], content["cta_after"])
    return fl.render("%s, %s. %s theme." % (content["name"], content["handle"], theme["name"]),
                     desc=" ".join(content["intro"]))


def _close(theme, variant, band, content):
    fl = Flow(theme, variant, band)
    fl.space(fl.base * 0.4)
    size = fl._fit(theme["signoff"], 700, fl.s["head"], fl.inner, fl.s["lead"])
    fl.text(theme["signoff"], size, fl.p["acc"], 700)
    fl.space(fl.base * 0.35)
    y = fl.y
    fl.bg.append(lambda c: c.line(fl.x, y, fl.x + fl.inner * 0.5, y, fl.p["acc"], 0.7,
                                  max(2, fl.base / 10.0)))
    fl.space(fl.base * 0.9)
    for line in content["footer"]:
        fl.wrap(line, fl.s["micro"], fl.p["muted"])
        fl.space(fl.base * 0.25)
    return fl.render("Closing panel: %s" % theme["signoff"],
                     desc=" ".join(content["footer"]))


def _work(theme, variant, band, content, data, today):
    fl = Flow(theme, variant, band)
    fl.space(fl.base * 0.3)
    fl.section(theme["labels"]["public"])
    fl.wrap(content["stats"], fl.s["micro"], fl.p["muted"])
    fl.space(fl.base * 0.6)
    for row in data["picked"]:
        meta = ", ".join(x for x in (row.get("lang") or "", "updated " + row["date"]) if x)
        fl.card(row["name"], row["desc"].rstrip("."), meta)
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
