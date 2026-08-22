#!/usr/bin/env python3
"""Enforce the rendering contract for the itxcrusher profile README.

Python 3.11+ stdlib only. Run locally or from .github/workflows/readme-check.yml.
Every rule here exists because something on the live profile broke that way once.

Exit 0 if every rule passes, 1 otherwise.
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

README = "README.md"
HERO = "assets/hero.svg"
USER = "itxcrusher"

ALLOWED_IMAGE_PREFIX = "https://raw.githubusercontent.com/itxcrusher/itxcrusher/output/"
NAME = "Muhammad Hassaan Javed"
# The GitHub display name is the codename, not the legal name. Both are valid
# identities for this account; anything else means the field was changed by
# accident or by someone else.
ACCEPTED_ACCOUNT_NAMES = {"CRUSHER", "Muhammad Hassaan Javed"}

# R3: the page must still say who this is and what to do if every image dies.
# Every string below lives in the HAND-AUTHORED region, never in the generated block,
# so a dead generator cannot take them with it.
REQUIRED_TEXT = [
    NAME,
    "@" + USER,
    "muhammadhassaanjaved99@gmail.com",
    "infraforge.agency",
    "CAMPAIGN AUDIT: PASSED",
    "If infrastructure feels exciting",
    "operating stack",
    "private client and product repositories",
]

APPROVED_FONT_TOKENS = (
    "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Ubuntu", "Helvetica Neue",
    "Arial", "sans-serif", "ui-monospace", "SFMono-Regular", "Menlo", "Consolas",
    "monospace",
)

IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
ATTR_RE = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"')
START = "<!-- PUBLIC_SURFACE:START -->"
END = "<!-- PUBLIC_SURFACE:END -->"

failures = []
notes = []


def fail(rule, msg):
    failures.append(rule + ": " + msg)


def ok(rule, msg):
    notes.append(rule + ": " + msg)


def imgs(text):
    out = []
    for tag in IMG_RE.findall(text):
        out.append(dict(ATTR_RE.findall(tag)))
    return out


def hand_authored(text):
    """The README with the generated block removed."""
    i, j = text.find(START), text.find(END)
    if i == -1 or j == -1:
        return text
    return text[:i] + text[j + len(END):]


def main():
    if not os.path.isfile(README):
        print("FATAL: run this from the repository root", file=sys.stderr)
        return 1
    text = open(README, encoding="utf-8").read()
    tags = imgs(text)

    # R1 assets resolve
    missing = []
    for t in tags:
        src = t.get("src", "")
        if src.startswith("./") or (src and not src.startswith("http")):
            path = src[2:] if src.startswith("./") else src
            if not os.path.isfile(path):
                missing.append(src)
            else:
                r = subprocess.run(["git", "ls-files", "--error-unmatch", path],
                                   capture_output=True)
                if r.returncode != 0:
                    missing.append(src + " (exists but untracked)")
    if missing:
        fail("R1", "unresolved image src: " + ", ".join(missing))
    else:
        ok("R1", "every relative image src resolves to a tracked file")

    # R2 third-party image budget is zero
    foreign = [t.get("src", "") for t in tags
               if t.get("src", "").startswith("http")
               and not t.get("src", "").startswith(ALLOWED_IMAGE_PREFIX)]
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
        ok("R3", str(len(REQUIRED_TEXT)) + " required strings survive image removal")

    # R4 alt text carries content
    bad_alt = []
    for t in tags:
        alt = t.get("alt", "")
        if len(alt) < 20:
            bad_alt.append(repr(alt) + " (under 20 chars)")
        elif re.search(r"\b(card|banner|image|graph|animation|icon)s?$",
                       alt.strip().rstrip("."), re.I):
            bad_alt.append(repr(alt) + " (ends in an artifact label)")
    if bad_alt:
        fail("R4", "; ".join(bad_alt))
    else:
        ok("R4", "all " + str(len(tags)) + " images carry content-bearing alt text")

    # R5 plain ASCII only
    offenders = sorted(set(c for c in text if ord(c) > 127))
    if offenders:
        fail("R5", "non-ASCII in README: " + repr(offenders))
    else:
        ok("R5", "README is plain ASCII")

    # R6 + R7 + R8 authored SVGs
    for svg_path in sorted(
            os.path.join(dp, f)
            for dp, _, fs in os.walk("assets") for f in fs if f.endswith(".svg")) \
            if os.path.isdir("assets") else []:
        raw = open(svg_path, encoding="utf-8").read()
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            fail("R7", svg_path + " is not valid XML: " + str(e))
            continue

        vb = (root.get("viewBox") or "").split()
        if len(vb) != 4 or vb[2] != "900":
            fail("R6", svg_path + " viewBox width must be 900, got " + repr(vb))
        sizes = [int(s) for s in re.findall(r'font-size="(\d+)"', raw)]
        small = [s for s in sizes if s < 41]
        if small:
            fail("R6", svg_path + " font-size below the 41-unit floor: " + str(small))
        if not small and len(vb) == 4 and vb[2] == "900":
            ok("R6", svg_path + " canvas 900 wide, smallest type " + str(min(sizes)))

        forbidden = [tok for tok in ("<script", "@import", 'href="http', "url(#",
                                     "<filter", "Gradient", "prefers-color-scheme")
                     if tok in raw]
        if forbidden:
            fail("R7", svg_path + " contains forbidden token(s): " + str(forbidden))
        for fam in re.findall(r'font-family="([^"]*)"', raw):
            for part in [p.strip().strip("'\"") for p in fam.split(",")]:
                if part and part not in APPROVED_FONT_TOKENS:
                    fail("R7", svg_path + " uses unapproved font " + repr(part))
        if root.get("role") != "img":
            fail("R7", svg_path + ' is missing role="img"')
        if root.find("{http://www.w3.org/2000/svg}title") is None:
            fail("R7", svg_path + " is missing a <title> element")
        if not forbidden:
            ok("R7", svg_path + " is self-contained, theme-agnostic, labelled")

        # R8 no facts inside images: no multi-digit run in any rendered text node
        for el in root.iter():
            if el.text and re.search(r"\d{2,}", el.text):
                fail("R8", svg_path + " renders a number in text: " + repr(el.text))
        ok("R8", svg_path + " carries identity only, no facts")

    # R9 single source of truth: no hand-maintained repo list outside the markers
    hand = hand_authored(text)
    hand_repo_items = [ln for ln in hand.splitlines() if ln.strip().startswith("- **[")]
    if hand_repo_items:
        fail("R9", "hand-authored repo list item(s) outside the generated block: "
             + str(hand_repo_items[:2]))
    else:
        ok("R9", "no repo one-liners are hand-maintained")

    # markers present exactly once each, in order
    if text.count(START) != 1 or text.count(END) != 1 or text.find(START) > text.find(END):
        fail("R9", "PUBLIC_SURFACE markers are missing, duplicated, or out of order")

    # R10 identity strings.
    #
    # The account display name is the codename (CRUSHER); the legal name is carried by
    # the page. That split is deliberate: the handle identity sits in the sidebar, the
    # searchable human identity sits in the hero. What must NOT drift is the legal name
    # between the two artifacts here, and the account name away from a known identity.
    if NAME not in text:
        fail("R10", "the README does not contain " + repr(NAME))
    if os.path.isfile(HERO) and NAME not in open(HERO, encoding="utf-8").read():
        fail("R10", HERO + " does not contain " + repr(NAME))
    acct = subprocess.run(["gh", "api", "users/" + USER, "--jq", ".name"],
                          capture_output=True, text=True)
    if acct.returncode != 0:
        fail("R10", "could not read the account name from the public API: "
             + acct.stderr.strip()[:120])
    elif acct.stdout.strip() not in ACCEPTED_ACCOUNT_NAMES:
        fail("R10", "account name is " + repr(acct.stdout.strip())
             + ", expected one of " + repr(sorted(ACCEPTED_ACCOUNT_NAMES)))
    elif NAME in text and (not os.path.isfile(HERO)
                           or NAME in open(HERO, encoding="utf-8").read()):
        ok("R10", repr(NAME) + " matches byte-for-byte across hero SVG and README; "
           "account name " + repr(acct.stdout.strip()) + " is a known identity")

    # R11 generated blocks self-date
    i, j = text.find(START), text.find(END)
    if i != -1 and j != -1:
        block = text[i + len(START):j]
        if block.strip() and not re.search(
                r"^_Generated \d{4}-\d{2}-\d{2} from the GitHub API\._$",
                block, re.M):
            fail("R11", "the generated block has content but no Generated YYYY-MM-DD stamp")
        elif block.strip():
            ok("R11", "generated block carries a dated stamp")
        else:
            ok("R11", "generated block is empty (not yet rendered), stamp not required")

    for n in notes:
        print("  pass  " + n)
    if failures:
        print("")
        for f in failures:
            print("  FAIL  " + f)
        print("\nrendering contract: " + str(len(failures)) + " failure(s)")
        return 1
    print("\nrendering contract: all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
