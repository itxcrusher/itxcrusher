#!/usr/bin/env python3
"""The theme engine's command line. Python 3.11+ stdlib only at runtime.

  build     draw the two static page slices for every theme into assets/pages/<slug>/
  pick      decide today's theme (deterministic); writes GITHUB_OUTPUT when present
  render    write README.md for a theme from the data file profile_surface.py produced
  preview   write the self-contained gallery page (every theme, both colour modes)
  schedule  print the next N picks
  report    per-theme contrast numbers for both variants

Run from the repository root.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from themes import catalog, page, page_art, preview, render, rotate, textpanel  # noqa: E402

PAGES = os.path.join(ROOT, "assets", "pages")
TODAY = os.path.join(ROOT, "assets", "today")


def write(path, text):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def cmd_build(args):
    """The two slices that do not depend on the API, for every theme.

    The data-dependent slice is NOT built here. It carries live counts and dates, and a
    committed copy per theme would be 46 pages of stale numbers the moment the rotation
    moved on. It is written by `render` into assets/today/ instead, which is the only
    directory the contract lets a number appear in.
    """
    if args.clean:
        for d in (PAGES, TODAY):
            if os.path.isdir(d):
                shutil.rmtree(d)
    content = page.art_content(page.fixture_data(), datetime.date.today().isoformat())
    total = n = 0
    for t in catalog.THEMES:
        for fn, svg in page_art.build_static(t, content).items():
            write(os.path.join(PAGES, t["slug"], fn), svg)
            total += len(svg)
            n += 1
    write(os.path.join(PAGES, "README.md"),
          preview.gallery_markdown(catalog.THEMES, len(catalog.ACTIVE)))
    write(os.path.join(ROOT, "assets", "index.json"), json.dumps(
        {"active": [t["slug"] for t in catalog.ACTIVE],
         "all": [t["slug"] for t in catalog.THEMES]}, indent=2) + "\n")
    print("built %d themes (%d active), %d page slices, %.1f KB"
          % (len(catalog.THEMES), len(catalog.ACTIVE), n, total / 1024))


def _date(s):
    return datetime.date.fromisoformat(s) if s else datetime.date.today()


def _snake_query(theme, variant):
    snake, dots = catalog.snake_colours(theme, variant)
    return "color_snake=%s&color_dots=%s" % (snake, ",".join(dots))


def cmd_pick(args):
    override = args.force or os.environ.get("PROFILE_THEME") or None
    slug, mode = rotate.pick(_date(args.date), args.mode, override)
    t = catalog.BY_SLUG[slug]
    out = {
        "theme": slug, "mode": mode, "name": t["name"],
        "snake_dark": _snake_query(t, "dark"), "snake_light": _snake_query(t, "light"),
    }
    gho = os.environ.get("GITHUB_OUTPUT")
    if gho:
        with open(gho, "a", encoding="utf-8") as fh:
            for k, v in out.items():
                fh.write("%s=%s\n" % (k, v))
    print(json.dumps(out, indent=2))


def cmd_render(args):
    slug = args.theme
    if slug not in catalog.BY_SLUG:
        raise SystemExit("unknown theme %r" % slug)
    t = catalog.BY_SLUG[slug]
    if args.data == "fixture":
        data = page.fixture_data(args.date)
    else:
        data = json.load(open(args.data, encoding="utf-8"))
    today = args.date or data.get("today") or datetime.date.today().isoformat()
    # The data-dependent slice is drawn here, not at build time, because it carries live
    # counts and dates. assets/today/ is rewritten on every run, which is precisely why
    # it is the one place the contract allows a number inside an image: it cannot go
    # stale between runs the way a committed per-theme copy would.
    content = page.art_content(data, today)
    if os.path.isdir(TODAY):
        shutil.rmtree(TODAY)
    for fn, svg in page_art.build_work(t, content, data, today).items():
        write(os.path.join(TODAY, fn), svg)
    md = page.render_readme(t, data, today, args.mode, len(catalog.ACTIVE))
    write(args.out, md)
    print("wrote %s and %d slices for theme %s (%s)"
          % (args.out, len(page_art.build_work(t, content, data, today)), slug, today))


def cmd_preview(args):
    html = preview.preview_html(catalog.THEMES, PAGES, args.band)
    write(args.out, html)
    print("wrote %s: %d themes, %s band" % (args.out, len(catalog.THEMES), args.band))


def cmd_schedule(args):
    for d, s in rotate.schedule(_date(args.date), args.days, args.mode):
        print(d, s)


def cmd_report(args):
    print("%-12s %-6s %8s %8s %8s" % ("theme", "mode", "ink/bg", "acc/bg", "muted/bg"))
    worst = []
    for t in catalog.THEMES:
        for v, ink, acc, muted in render.contrast_report(t):
            flag = " <-- low" if ink < 7 or acc < 3 or muted < 4.5 else ""
            print("%-12s %-6s %8.1f %8.1f %8.1f%s" % (t["slug"], v, ink, acc, muted, flag))
            if flag:
                worst.append((t["slug"], v))
    print("\n%d variant(s) below the floor (ink 7:1, accent 3:1, muted 4.5:1)" % len(worst))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--clean", action="store_true")
    b.set_defaults(fn=cmd_build)
    k = sub.add_parser("pick")
    k.add_argument("--date")
    k.add_argument("--mode", default=None, help="daily | weekly | seasonal | fixed:<slug>")
    k.add_argument("--force", default=None, help="a theme slug; beats the mode")
    k.set_defaults(fn=cmd_pick)
    r = sub.add_parser("render")
    r.add_argument("--theme", required=True)
    r.add_argument("--data", default="fixture", help="path to data.json from profile_surface.py, or 'fixture'")
    r.add_argument("--out", default="README.md")
    r.add_argument("--date", default=None)
    r.add_argument("--mode", default="daily")
    r.set_defaults(fn=cmd_render)
    v = sub.add_parser("preview")
    v.add_argument("--out", default="preview.html")
    v.add_argument("--band", default="lg", choices=[k for k, _m, _w, _s in textpanel.BANDS])
    v.set_defaults(fn=cmd_preview)
    s = sub.add_parser("schedule")
    s.add_argument("--date")
    s.add_argument("--days", type=int, default=14)
    s.add_argument("--mode", default=None)
    s.set_defaults(fn=cmd_schedule)
    c = sub.add_parser("report")
    c.set_defaults(fn=cmd_report)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
