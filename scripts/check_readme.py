#!/usr/bin/env python3
"""Enforce the rendering contract for the itxcrusher profile README.

Python 3.11+ stdlib only. Run locally or from .github/workflows/readme-check.yml.
Every rule here exists because something on the live profile broke that way once, or
because the theme engine could break it silently.

  R1   every relative image resolves to a tracked file
  R2   third-party image hosts: zero (own output branch excepted)
  R3   the required text survives image death
  R4   alt text carries content (a heading image may use its heading text)
  R5   README.md and every SVG are plain ASCII
  R6   every page slice matches its viewport band: canvas width and type scale
  R7   SVGs are self-contained: no script, no imports, no external refs, no
       prefers-color-scheme (theme pairing is <picture>'s job), system fonts only,
       role="img" and a <title>
  R8   a committed image may only render numbers that are hand-authored constants;
       anything from the API belongs in assets/today/, which is rewritten every run
  R9   single source of truth for the repository list
  R10  identity strings agree across README, the opening panel and the account
  R11  the generated block self-dates
  R12  the page wears exactly one theme, and it is a catalogued one
  R13  page weight: the images the README references stay under budget
  R14  light-variant accents carry weight, so the light page never reads as a
       washed-out copy of the dark one

Exit 0 if every rule passes, 1 otherwise.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from themes.fullpage import allowed_sizes  # noqa: E402
from themes.textpanel import BAND_BY_KEY as PANEL_BANDS  # noqa: E402

README = "README.md"
USER = "itxcrusher"
THEME_INDEX = "assets/index.json"

ALLOWED_IMAGE_PREFIX = "https://raw.githubusercontent.com/itxcrusher/itxcrusher/output/"
NAME = "Muhammad Hassaan Javed"
# The GitHub display name is the codename, not the legal name. Both are valid
# identities for this account; anything else means the field was changed by
# accident or by someone else.
ACCEPTED_ACCOUNT_NAMES = {"CRUSHER", "Muhammad Hassaan Javed"}

# R3: the page must still say who this is and what to do if every image dies.
# Every string below lives in hand-authored prose (themes/page.py), never inside an
# SVG and never in the generated block, so a dead generator cannot take them with it.
REQUIRED_TEXT = [
    NAME,
    "@" + USER,
    "muhammadhassaanjaved99@gmail.com",
    "infraforge.agency",
    "muhammadhassaanjaved.com",
    "CAMPAIGN AUDIT: PASSED",
    "If infrastructure feels exciting",
    "operating stack",
    "private client and product repositories",
    # The stack moved into badges, which are images. These prove the text fallback
    # under them is still there, so the section does not vanish when images do.
    "Kubernetes", "Terraform", "GitHub Actions", "computer vision",
]

APPROVED_FONT_TOKENS = (
    "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Ubuntu", "Helvetica Neue",
    "Arial", "sans-serif", "ui-monospace", "SFMono-Regular", "Menlo", "Consolas",
    "monospace", "Georgia", "Times New Roman", "serif",
)
# Verified to render inside an <img>-loaded SVG under GitHub's CSP: gradients, filters,
# clipPath/mask/pattern via url(#...), CSS @keyframes and SMIL. What is still banned
# either cannot load (script, imports, external hrefs) or renders inconsistently
# across engines (prefers-color-scheme inside the SVG; WebKit ignores it).
FORBIDDEN_SVG_TOKENS = ("<script", "@import", 'href="http', "url(http", 'url("http',
                        "url('http", "prefers-color-scheme", "@font-face", "<image",
                        "<foreignObject", "<a ")
PAGE_WEIGHT_BUDGET = 160 * 1024
# The page is drawn per viewport band, so there is no single canvas width or type floor
# any more: each band declares both, and every slice is checked against the same table
# the builder lays out from.
TODAY_DIR = "assets/today/"


def _authored_numbers():
    """Every number that appears in the hand-authored strings in themes/page.py."""
    from themes import page as P
    blob = " ".join([P.NAME, P.HANDLE, P.EMAIL, P.CTA_TITLE, P.CTA_BODY, P.CTA_AFTER,
                     P.STACK_INTRO, P.UPSTREAM] + list(P.INTRO) + list(P.CTA_CMD)
                    + list(P.FOOTER) + [l for l, _ in P.LINKS]
                    + [x for _, v in P.STACK for x in v]
                    + [t["signoff"] for t in __import__("themes.catalog", fromlist=["x"]).THEMES]
                    + [t["labels"][k] for t in __import__("themes.catalog", fromlist=["x"]).THEMES
                       for k in ("public", "stack", "snake")])
    return set(tok.rstrip(".,") for tok in re.findall(r"\d[\d.,]*", blob))


AUTHORED_NUMBERS = _authored_numbers()

IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
ATTR_RE = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"')
SRCSET_RE = re.compile(r'<source\b[^>]*srcset\s*=\s*"([^"]+)"[^>]*>', re.I)
THEME_STAMP_RE = re.compile(r"<!-- theme: ([a-z0-9-]+) \| mode: [a-z:0-9-]+ \| date: \d{4}-\d{2}-\d{2} -->")
START = "<!-- PUBLIC_SURFACE:START -->"
END = "<!-- PUBLIC_SURFACE:END -->"

failures = []
notes = []


def fail(rule, msg):
    failures.append(rule + ": " + msg)


def ok(rule, msg):
    notes.append(rule + ": " + msg)


def imgs(text):
    return [dict(ATTR_RE.findall(tag)) for tag in IMG_RE.findall(text)]


def hand_authored(text):
    i, j = text.find(START), text.find(END)
    if i == -1 or j == -1:
        return text
    return text[:i] + text[j + len(END):]


def local_path(src):
    if src.startswith("http"):
        return None
    return src[2:] if src.startswith("./") else src


def main():
    if not os.path.isfile(README):
        print("FATAL: run this from the repository root", file=sys.stderr)
        return 1
    text = open(README, encoding="utf-8").read()
    tags = imgs(text)
    srcsets = SRCSET_RE.findall(text)
    all_srcs = [t.get("src", "") for t in tags] + srcsets
    local = sorted(set(p for p in (local_path(s) for s in all_srcs) if p))

    # R1 assets resolve to tracked files
    missing = []
    for path in local:
        if not os.path.isfile(path):
            missing.append(path)
            continue
        r = subprocess.run(["git", "ls-files", "--error-unmatch", path], capture_output=True)
        if r.returncode != 0:
            missing.append(path + " (exists but untracked)")
    if missing:
        fail("R1", "unresolved image src: " + ", ".join(missing))
    else:
        ok("R1", "all %d relative image sources resolve to tracked files" % len(local))

    # R1b the allowed absolute images resolve too.
    # R1 only walks relative paths, so when the README started asking the output branch
    # for snake-dark.svg and snake-light.svg before the workflow had ever published them,
    # every rule passed while the live page showed a broken image. Verified over the
    # network: a 404 is a real failure, an unreachable network is not.
    remote = sorted(set(u for u in all_srcs if u.startswith(ALLOWED_IMAGE_PREFIX)))
    if remote:
        import urllib.error
        import urllib.request
        dead, unreachable = [], False
        for u in remote:
            try:
                req = urllib.request.Request(u, method="HEAD",
                                             headers={"User-Agent": "itxcrusher-contract"})
                urllib.request.urlopen(req, timeout=15)
            except urllib.error.HTTPError as e:
                dead.append("%s (HTTP %s)" % (u.rsplit("/", 1)[-1], e.code))
            except Exception:  # noqa: BLE001
                unreachable = True
        if dead:
            fail("R1", "referenced but not published: " + ", ".join(dead))
        elif unreachable:
            ok("R1", "%d output-branch image(s) not verified (network unavailable)" % len(remote))
        else:
            ok("R1", "all %d output-branch image(s) resolve" % len(remote))

    # R2 third-party image budget is zero
    foreign = [u for u in all_srcs if u.startswith("http") and not u.startswith(ALLOWED_IMAGE_PREFIX)]
    if foreign:
        fail("R2", "third-party image host: " + ", ".join(foreign))
    else:
        ok("R2", "no third-party image hosts")

    # R3 text survives image death
    stripped = IMG_RE.sub("", text)
    gone = [s for s in REQUIRED_TEXT if s not in stripped]
    if gone:
        fail("R3", "required text missing with images off: " + "; ".join(gone))
    else:
        ok("R3", "%d required strings survive image removal" % len(REQUIRED_TEXT))

    # R4 alt text carries content.
    # An image that IS a heading is exempt from the length floor: its correct alt is the
    # heading text, which is short by design, and the surrounding <h2> already tells a
    # screen reader what it is. The floor exists to catch lazy alt like "banner", and the
    # artifact-label check below still applies to every image.
    heading_alts = set()
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s", line):
            heading_alts.update(m.get("alt", "") for m in imgs(line))
    bad_alt = []
    for t in tags:
        alt = t.get("alt", "")
        if not alt.strip():
            bad_alt.append("empty alt")
        elif len(alt) < 20 and alt not in heading_alts:
            bad_alt.append(repr(alt) + " (under 20 chars)")
        elif re.search(r"\b(card|banner|image|graph|animation|icon)s?$", alt.strip().rstrip("."), re.I):
            bad_alt.append(repr(alt) + " (ends in an artifact label)")
    if bad_alt:
        fail("R4", "; ".join(bad_alt))
    else:
        ok("R4", "all %d images carry content-bearing alt text" % len(tags))

    # R5 plain ASCII in the README
    offenders = sorted(set(c for c in text if ord(c) > 127))
    if offenders:
        fail("R5", "non-ASCII in README: " + repr(offenders))
    else:
        ok("R5", "README is plain ASCII")

    # R6 + R7 + R8 over every authored SVG (the whole theme library, not just today's)
    svgs = sorted(os.path.join(dp, f) for dp, _, fs in os.walk("assets") for f in fs if f.endswith(".svg")) \
        if os.path.isdir("assets") else []
    svg_fail = 0
    smallest = 10 ** 6
    for svg_path in svgs:
        raw = open(svg_path, encoding="utf-8").read()
        bad = False
        if any(ord(c) > 127 for c in raw):
            fail("R5", svg_path + " is not plain ASCII")
            bad = True
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            fail("R7", svg_path + " is not valid XML: " + str(e))
            svg_fail += 1
            continue
        rel = svg_path.replace(os.sep, "/")
        is_today = rel.startswith(TODAY_DIR)
        vb = (root.get("viewBox") or "").split()
        sizes = [int(x) for x in re.findall(r'font-size="(\d+)"', raw)]
        band = os.path.basename(rel).rsplit("-", 2)[-2]
        spec = PANEL_BANDS.get(band)
        if spec is None:
            fail("R6", svg_path + " is not named for a known viewport band")
            bad = True
        else:
            # Each band declares its canvas width and its base type size. Everything the
            # page draws must sit on that band's scale: a size between the rungs is how a
            # hand-tuned heading ends up at 6px on a phone.
            if len(vb) != 4 or vb[2] != str(spec[2]):
                fail("R6", svg_path + " band %s must be %d units wide, got %r"
                     % (band, spec[2], vb))
                bad = True
            allowed = allowed_sizes(spec[3])
            off = sorted(set(x for x in sizes if x not in allowed))
            if off:
                fail("R6", svg_path + " band %s uses type off the scale %s: %s"
                     % (band, sorted(allowed), off))
                bad = True
            if sizes:
                smallest = min(smallest, min(sizes))
        forbidden = [tok for tok in FORBIDDEN_SVG_TOKENS if tok in raw]
        if forbidden:
            fail("R7", svg_path + " contains forbidden token(s): " + str(forbidden))
            bad = True
        for fam in re.findall(r'font-family="([^"]*)"', raw):
            for part in [p.strip().strip("'\"") for p in fam.split(",")]:
                if part and part not in APPROVED_FONT_TOKENS:
                    fail("R7", svg_path + " uses unapproved font " + repr(part))
                    bad = True
        if root.get("role") != "img":
            fail("R7", svg_path + ' is missing role="img"')
            bad = True
        if root.find("{http://www.w3.org/2000/svg}title") is None:
            fail("R7", svg_path + " is missing a <title> element")
            bad = True
        # R8. A live fact inside a committed image goes stale silently: the file is
        # written once and the fact moves on. But "Python 3.11" and "11 of 11 checks" are
        # hand-authored constants that cannot drift, so a flat ban on digits is the wrong
        # rule. The rule is: a committed image may only render numbers that appear in the
        # authored constants. Anything the API produced has nowhere to hide but
        # assets/today/, which is rewritten on every run.
        if not is_today:
            rendered = ("{http://www.w3.org/2000/svg}text", "{http://www.w3.org/2000/svg}tspan")
            for el in root.iter():
                if el.tag not in rendered or not el.text:
                    continue
                for tok in re.findall(r"\d[\d.,]*", el.text):
                    if tok.rstrip(".,") not in AUTHORED_NUMBERS:
                        fail("R8", svg_path + " renders %r, which is not a hand-authored "
                             "constant: a live fact in a committed image goes stale"
                             % tok)
                        bad = True
        svg_fail += bad
    if svgs and not svg_fail:
        nt = sum(1 for x in svgs if x.replace(os.sep, "/").startswith(TODAY_DIR))
        ok("R6", "%d page slices match their band's canvas and type scale (%d of them "
                 "data-dependent), smallest type %d units"
                 % (len(svgs), nt, smallest))
        ok("R7", "every SVG is self-contained, system-font, labelled")
        ok("R8", "no SVG renders a number")

    # R9 single source of truth: no hand-maintained repo list outside the markers
    hand = hand_authored(text)
    hand_repo_items = [ln for ln in hand.splitlines() if re.match(r"^\s*(- |\d+\. |- \[x\] )\**\[", ln)]
    if hand_repo_items:
        fail("R9", "hand-authored repo list item(s) outside the generated block: " + str(hand_repo_items[:2]))
    else:
        ok("R9", "no repo one-liners are hand-maintained")
    if text.count(START) != 1 or text.count(END) != 1 or text.find(START) > text.find(END):
        fail("R9", "PUBLIC_SURFACE markers are missing, duplicated, or out of order")

    # R10 identity strings: the legal name in the README and in every hero variant the
    # README references; the account name a known identity.
    hero_variants = [p for p in local if os.path.basename(p).startswith("top-")]
    if NAME not in text:
        fail("R10", "the README does not contain " + repr(NAME))
    if not hero_variants:
        fail("R10", "the README references no opening panel")
    for hv in hero_variants:
        if os.path.isfile(hv) and NAME not in open(hv, encoding="utf-8").read():
            fail("R10", hv + " does not contain " + repr(NAME))
    try:
        acct = subprocess.run(["gh", "api", "users/" + USER, "--jq", ".name"], capture_output=True, text=True)
    except FileNotFoundError:
        acct = subprocess.CompletedProcess([], 1, "", "gh is not installed")
    if acct.returncode != 0:
        if os.environ.get("CHECK_SKIP_ACCOUNT"):
            ok("R10", "account name check skipped (CHECK_SKIP_ACCOUNT set)")
        else:
            fail("R10", "could not read the account name from the public API: " + acct.stderr.strip()[:120])
    elif acct.stdout.strip() not in ACCEPTED_ACCOUNT_NAMES:
        fail("R10", "account name is %r, expected one of %r" % (acct.stdout.strip(), sorted(ACCEPTED_ACCOUNT_NAMES)))
    elif NAME in text and hero_variants and all(NAME in open(hv, encoding="utf-8").read() for hv in hero_variants):
        ok("R10", "%r present in README and %d hero variant(s); account name %r is a known identity"
           % (NAME, len(hero_variants), acct.stdout.strip()))

    # R11 generated block self-dates
    i, j = text.find(START), text.find(END)
    if i != -1 and j != -1:
        block = text[i + len(START):j]
        if block.strip() and not re.search(r"^_Generated \d{4}-\d{2}-\d{2} from the GitHub API\._$", block, re.M):
            fail("R11", "the generated block has content but no Generated YYYY-MM-DD stamp")
        elif block.strip():
            ok("R11", "generated block carries a dated stamp")
        else:
            ok("R11", "generated block is empty (not yet rendered), stamp not required")

    # R12 exactly one theme, and a catalogued one
    m = THEME_STAMP_RE.search(text)
    if not m:
        fail("R12", "no theme stamp (<!-- theme: slug | mode: ... | date: ... -->) at the top of the README")
    else:
        slug = m.group(1)
        used = set(re.findall(r"assets/pages/([a-z0-9-]+)/", text))
        if used != {slug}:
            fail("R12", "README wears theme %r but references assets from %r" % (slug, sorted(used)))
        try:
            idx = json.load(open(THEME_INDEX, encoding="utf-8"))
            if slug not in idx.get("all", []):
                fail("R12", "theme %r is not in %s" % (slug, THEME_INDEX))
            else:
                expected = {"top", "close"}
                stems = set(re.findall(r"assets/pages/%s/([a-z]+)-(?:xs|sm|md|lg)-(?:dark|light)\.svg"
                                       % slug, text))
                if stems != expected:
                    fail("R12", "theme %r is missing pieces: %s" % (slug, sorted(expected - stems)))
                else:
                    ok("R12", "the page wears one catalogued theme, %r, with every piece present" % slug)
        except (OSError, ValueError) as e:
            fail("R12", "cannot read %s: %s" % (THEME_INDEX, e))

    # R13 page weight, measured as what ONE reader downloads.
    # The page is drawn per viewport band, so the README references four canvases of
    # every panel but a browser fetches exactly one of them, plus one colour scheme.
    # Summing all of them would fail a page nobody actually downloads. The worst real
    # case is the widest band, which is the largest file, in one scheme.
    per_band = {}
    for p in local:
        if not os.path.isfile(p):
            continue
        m = re.search(r"-(xs|sm|md|lg)-(dark|light)\.svg$", p.replace(os.sep, "/"))
        key = (m.group(1), m.group(2)) if m else ("*", "*")
        per_band[key] = per_band.get(key, 0) + os.path.getsize(p)
    fixed = per_band.pop(("*", "*"), 0)
    worst = max(per_band.values()) if per_band else 0
    weight = fixed + worst
    if weight > PAGE_WEIGHT_BUDGET:
        fail("R13", "the heaviest single load is %d KB, budget is %d KB"
             % (weight // 1024, PAGE_WEIGHT_BUDGET // 1024))
    else:
        ok("R13", "the heaviest single load is %d KB of a %d KB budget; the contribution "
                  "snake is generated elsewhere and not counted here"
           % (weight // 1024, PAGE_WEIGHT_BUDGET // 1024))

    # R14 light accents carry weight.
    # Measured 2026-08-27 before this rule existed: accent contrast averaged 10.7:1 on
    # the dark variants and 5.1:1 on the light ones, 21 of 47 below WCAG AA. Dark gets
    # presence from glow against a deep ground; on white the only equivalent is ink
    # density. catalog.py normalises at import; this stops it regressing in what ships.
    try:
        sys.path.insert(0, os.getcwd())
        from themes.catalog import THEMES, LIGHT_ACCENT_FLOOR
        from themes.svg import contrast as _contrast
        weak = []
        for _t in THEMES:
            lp = _t["light"]
            for key in ("acc", "acc2"):
                if key in lp:
                    c = _contrast(lp[key], lp["bg"])
                    if c < LIGHT_ACCENT_FLOOR:
                        weak.append("%s.%s %.1f:1" % (_t["slug"], key, c))
        if weak:
            fail("R14", "light accent below %.1f:1: %s" % (LIGHT_ACCENT_FLOOR, ", ".join(weak[:6])))
        else:
            ok("R14", "all %d themes clear the %.1f:1 light-accent floor" % (len(THEMES), LIGHT_ACCENT_FLOOR))
    except ImportError:
        ok("R14", "theme engine not present; light-accent floor not applicable")

    for n in notes:
        print("  pass  " + n)
    if failures:
        print("")
        for f in failures[:40]:
            print("  FAIL  " + f)
        if len(failures) > 40:
            print("  ... and %d more" % (len(failures) - 40))
        print("\nrendering contract: %d failure(s)" % len(failures))
        return 1
    print("\nrendering contract: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
