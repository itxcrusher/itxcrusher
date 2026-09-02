"""The page: hand-authored content plus the README renderer.

The prose here is the hand-authored region of the old README, moved into one place so
the theme engine can lay it out. Every string the rendering contract requires to survive
image death (R3) is plain text in this file, never inside an SVG.
"""
import datetime
import json
import re

from . import page_art
from .render import NAME, HANDLE

USER = "itxcrusher"
EMAIL = "muhammadhassaanjaved99@gmail.com"
REPOS_TAB = "https://github.com/itxcrusher?tab=repositories&type=source&sort=pushed"
OUTPUT_BRANCH = "https://raw.githubusercontent.com/itxcrusher/itxcrusher/output/"
START = "<!-- PUBLIC_SURFACE:START -->"
END = "<!-- PUBLIC_SURFACE:END -->"
THEME_STAMP_RE = re.compile(r"<!-- theme: ([a-z0-9-]+) \| mode: ([a-z:0-9-]+) \| date: (\d{4}-\d{2}-\d{2}) -->")

LINKS = [
    ("muhammadhassaanjaved.com", "https://muhammadhassaanjaved.com"),
    ("infraforge.agency", "https://infraforge.agency"),
    ("repositories", REPOS_TAB),
]

INTRO = [
    "I build infrastructure and bounded automation for other people's production systems. "
    "Terraform, Kubernetes, CI/CD, and lately agents that act on evidence they can prove "
    "instead of guessing.",
    "Most of that work is in private client and product repositories, so what is public here "
    "is a sample rather than the volume. The contribution graph counts it. The repository "
    "list cannot show it.",
    "If infrastructure feels exciting, something is probably wrong. The goal is systems that "
    "are quiet, predictable, and uninteresting in production.",
]

TOP_ALT = ("Opening statement: this account builds "
           "infrastructure and bounded automation for other people's production systems, "
           "most of it in private repositories, followed by a runnable check that the work "
           "is real. The same words are in the plain-text copy at the foot of the page.")
CLOSE_ALT = ("Contact lines: how to reach Muhammad Hassaan Javed, by the agency site, the "
             "personal site, or directly by email. The same words are in the plain-text "
             "copy at the foot of the page.")

INTRO_ALT = ("Opening statement: I build infrastructure and bounded automation for other "
             "people's production systems. Most of that work is in private client and product "
             "repositories, so what is public here is a sample rather than the volume. If "
             "infrastructure feels exciting, something is probably wrong; the goal is systems "
             "that are quiet, predictable, and uninteresting in production.")

CTA_TITLE = "Want to check whether any of this is real?"
CTA_BODY = ("`ripple-proof` audits a full captured campaign offline in about a minute, with "
            "Python 3.11 and nothing else. No install, no account, no credential, no network call. "
            "It prints every point where it refused to act.")
CTA_CMD = ["git clone https://github.com/itxcrusher/ripple-proof", "cd ripple-proof",
           "PYTHONPATH=src python -S -m lineage_agent.cli demo"]
CTA_AFTER = ("Expect `CAMPAIGN AUDIT: PASSED`, 11 of 11 checks. The "
             "[walkthrough](https://itxcrusher.github.io/ripple-proof/) keeps one run that fails its "
             "dbt build on purpose rather than dropping it.")

STACK_INTRO = ("Everything in the operating stack below has a public artifact in this account. "
               "Work that does not is in private repositories and is not listed here.")
STACK = [
    ("cloud", ["AWS", "Azure"]),
    ("platform", ["Kubernetes", "Docker", "Terraform", "Helm"]),
    ("delivery", ["GitHub Actions", "CI/CD pipelines", "ArgoCD", "GitOps"]),
    ("systems", ["Linux", "networking", "shell automation"]),
    ("ai", ["bounded agents", "MCP", "LLM workflows", "computer vision"]),
    ("languages", ["Python", "Bash", "HCL", "YAML"]),
]
UPSTREAM = ("Upstream, open: [skip_cache for get_lineage](https://github.com/acryldata/mcp-server-datahub/pull/190) "
            "in acryldata/mcp-server-datahub, and a "
            "[repair-boundary skill](https://github.com/datahub-project/datahub-skills/pull/125) "
            "in datahub-project/datahub-skills.")
SNAKE_ALT = ("Contribution snake: an animation eating this account's GitHub contribution squares, "
             "regenerated daily from the output branch in today's theme colours.")
FOOTER = [
    "%s (%s). Infrastructure recovery and platform work: [infraforge.agency](https://infraforge.agency). "
    "Personal site: [muhammadhassaanjaved.com](https://muhammadhassaanjaved.com)" % (NAME, HANDLE),
    "Direct: <%s>" % EMAIL,
]


# --------------------------------------------------------------------------- helpers

def _attr(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def picture(theme_dir, stem, alt, width="100%"):
    alt = _attr(alt)
    return "\n".join([
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="./%s/%s-dark.svg">' % (theme_dir, stem),
        '  <source media="(prefers-color-scheme: light)" srcset="./%s/%s-light.svg">' % (theme_dir, stem),
        '  <img src="./%s/%s-light.svg" width="%s" alt="%s" />' % (theme_dir, stem, width, alt),
        "</picture>",
    ])


def badge_picture(slug, variant_file, label):
    """One themed badge. height=28 and nothing else: GitHub turns that into
    height:auto + max-height:28px, and because every badge is narrower than the
    narrowest measured README column (238px) the max-width cap never binds either.
    So it renders at its authored size on every viewport, which is the only way real
    words on this page get to carry the theme's colours instead of GitHub's grey."""
    d = "./assets/badges/" + slug
    return (
        "<picture>"
        '<source media="(prefers-color-scheme: dark)" srcset="%s/dark/%s.svg">'
        '<source media="(prefers-color-scheme: light)" srcset="%s/light/%s.svg">'
        '<img src="%s/light/%s.svg" height="28" alt="%s" />'
        "</picture>"
    ) % (d, variant_file, d, variant_file, d, variant_file, _attr(label))


def badge_rows(slug):
    """The stack as themed pills, one line per category, replacing the code fence.
    The fence was the largest block on the page that GitHub painted in its own grey."""
    from themes.badge import slug as bslug
    out = []
    for label, values in STACK:
        row = [badge_picture(slug, bslug(label), label)]
        row += [badge_picture(slug, bslug(v), v) for v in values]
        out.append("<p>" + "\n".join(row) + "</p>")
    # The badges are images, and this page's contract says the facts survive with
    # images off (R3). Every badge carries its word as alt text, but a hostile network
    # drops both, so the same list stays here as text. Collapsed on purpose: it is a
    # fallback, not a second copy of the section.
    out.append("<details><summary><sub>the same stack as plain text</sub></summary>")
    out.append("")
    for label, values in STACK:
        out.append("- **%s** - %s" % (label, ", ".join(values)))
    out.append("")
    out.append("</details>")
    return "\n".join(out)


def heading_picture(theme_dir, stem, alt, level=2):
    """A section heading that is a themed image AND a real heading element.

    The themed page carries its section headings as artwork, which until now meant the
    rendered document had zero <h1>-<h6> elements: no screen-reader heading navigation,
    no anchor links, and an empty outline menu on GitHub. A markdown heading must sit on
    one line, so the picture is emitted inline rather than pretty-printed; GitHub then
    renders <h2><themed-picture>...</themed-picture></h2> and both properties hold at
    once. Verified against GitHub's own markdown API.
    """
    alt = _attr(alt)
    inner = (
        "<picture>"
        '<source media="(prefers-color-scheme: dark)" srcset="./%s/%s-dark.svg">'
        '<source media="(prefers-color-scheme: light)" srcset="./%s/%s-light.svg">'
        '<img src="./%s/%s-light.svg" width="100%%" alt="%s" />'
        "</picture>"
    ) % (theme_dir, stem, theme_dir, stem, theme_dir, stem, alt)
    return "%s %s" % ("#" * level, inner)


def snake_picture():
    return "\n".join([
        "<picture>",
        '  <source media="(prefers-color-scheme: dark)" srcset="%ssnake-dark.svg">' % OUTPUT_BRANCH,
        '  <source media="(prefers-color-scheme: light)" srcset="%ssnake-light.svg">' % OUTPUT_BRANCH,
        '  <img src="%ssnake-light.svg" alt="%s" />' % (OUTPUT_BRANCH, SNAKE_ALT),
        "</picture>",
    ])


def chip(text, style):
    if not text:
        return ""
    if style == "kbd":
        return "<kbd>%s</kbd>" % text
    if style == "code":
        return "`%s`" % text
    return text


def _esc_cell(s):
    return s.replace("|", "\\|")


def format_stack(lang):
    """The stack block in the theme's fence language, so GitHub colours it natively."""
    rows = STACK
    if lang == "yaml":
        return "\n".join("%s: [%s]" % (k, ", ".join(v)) for k, v in rows)
    if lang in ("hcl", "toml"):
        w = max(len(k) for k, _ in rows)
        return "\n".join('%s = [%s]' % (k.ljust(w), ", ".join('"%s"' % x for x in v)) for k, v in rows)
    if lang == "json":
        return json.dumps(dict(rows), indent=2)
    if lang == "ini":
        return "\n\n".join("[%s]\n%s" % (k, "\n".join("%s = on" % x for x in v)) for k, v in rows)
    if lang == "bash":
        return "\n".join("%s=(%s)" % (k, " ".join('"%s"' % x for x in v)) for k, v in rows)
    if lang == "python":
        body = "\n".join('    "%s": [%s],' % (k, ", ".join('"%s"' % x for x in v)) for k, v in rows)
        return "stack = {\n%s\n}" % body
    if lang == "diff":
        w = max(len(k) for k, _ in rows)
        return "\n".join("+ %s  %s" % (k.ljust(w), " | ".join(v)) for k, v in rows)
    if lang == "makefile":
        return "\n\n".join("%s:\n\t%s" % (k, " ".join(x.replace(" ", "-") for x in v)) for k, v in rows)
    if lang == "css":
        return "\n\n".join(".%s {\n  stack: %s;\n}" % (k, ", ".join(v)) for k, v in rows)
    w = max(len(k) for k, _ in rows)
    return "\n".join("%s  %s" % (k.ljust(w), " | ".join(v)) for k, v in rows)


# --------------------------------------------------------------------- the block

def _row_bits(r, chip_style, slug=None):
    desc = r["desc"].rstrip(".")
    lang = r.get("lang") or ""
    home = r.get("home") or ""
    walk = " [Walkthrough](%s)" % home if home.startswith("http") else ""
    return desc, lang, walk


def lang_pill(slug, lang):
    """A themed language chip, or the plain word when no badge was built for it.
    Languages come from the live API, so an unlisted one must not point at a file that
    does not exist: R1 would fail the build rather than ship a broken image."""
    from themes.badge import LANGUAGES, slug as bslug
    if not lang:
        return ""
    if lang not in LANGUAGES:
        return lang
    return badge_picture(slug, "lang-" + bslug(lang), lang)


def render_block(data, text, today, slug):
    """The PUBLIC_SURFACE block. Same facts and the same guards as the original
    generator; only the row style is themed."""
    rows_style = text.get("rows", "list")
    chip_style = text.get("chip", "plain")
    lines = []
    n, total, private = data["n"], data["total"], data["private"]
    if private:
        about = "about " if data.get("approx") else ""
        lines.append(
            "%d original public repositories. Most of the work is not here: over the last 12 "
            "months, %s%s of %s contributions were in private repositories (client delivery, "
            "product builds, and security research)." % (n, about, format(private, ","), format(total, ",")))
    else:
        lines.append("%d original public repositories, out of %s contributions in the last 12 months."
                     % (n, format(total, ",")))
    lines.append("")

    picked = data["picked"]
    if picked and data.get("freshest_days", 9999) <= 120:
        lines.append("Most recent public work:")
        lines.append("")
        if rows_style == "table":
            lines.append("| repository | what it is | language | updated |")
            lines.append("| --- | --- | --- | --- |")
            for r in picked:
                desc, lang, walk = _row_bits(r, chip_style)
                pill = lang_pill(slug, lang)
                lines.append("| **[%s](%s)** | %s.%s | %s | %s |" % (
                    r["name"], r["url"], _esc_cell(desc), walk, pill, r["date"]))
        else:
            for i, r in enumerate(picked, 1):
                desc, lang, walk = _row_bits(r, chip_style)
                pill = lang_pill(slug, lang)
                # The pill closes the row rather than sitting inside the sentence: an
                # inline image mid-paragraph interrupts the line and pushes the leading
                # around it, which read as clutter once the rows were laid out live.
                meta = "updated " + r["date"]
                tail = (" " + pill) if pill else ""
                if rows_style == "tasks":
                    lines.append("- [x] **[%s](%s)** - %s. <sub>%s.</sub>%s%s" % (
                        r["name"], r["url"], desc, meta, walk, tail))
                elif rows_style == "numbered":
                    lines.append("%d. **[%s](%s)** - %s. <sub>%s.</sub>%s%s" % (
                        i, r["name"], r["url"], desc, meta, walk, tail))
                elif rows_style == "quotes":
                    lines.append("> **[%s](%s)**<br>%s.<br><sub>%s.%s</sub>%s" % (
                        r["name"], r["url"], desc, meta, walk, tail))
                    lines.append("")
                elif rows_style == "ls":
                    lines.append("- `drwxr-xr-x` **[%s](%s)** `%s`<br>%s.%s%s" % (
                        r["name"], r["url"], r["date"], desc, walk, tail))
                else:
                    lines.append("- **[%s](%s)** - %s. Updated %s.%s%s" % (
                        r["name"], r["url"], desc, r["date"], walk, tail))
        if lines[-1] != "":
            lines.append("")
    else:
        lines.append(
            "Nothing public has changed in the last four months. That is the normal state here. "
            "Start with [ripple-proof](https://github.com/%s/ripple-proof), or browse "
            "[all source repositories](%s)." % (USER, REPOS_TAB))
        lines.append("")

    links = data.get("dbt_links") or []
    if links:
        state = "All open and review-only." if data.get("all_open") else "Some have since been merged."
        lines.append("Evidence trail for ripple-proof runs across four public sibling dbt repositories: "
                     + ", ".join("[%s](%s)" % (a, b) for a, b in links) + ". " + state)
        lines.append("")
    lines.append("_Generated %s from the GitHub API._" % today)
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------------- README

def art_content(data, today):
    """Everything the artwork needs, as plain strings.

    Kept apart from the drawing code so the words stay in one file. Markdown syntax is
    stripped here rather than in the renderer: backticks and [text](url) mean nothing
    inside an SVG, and a link cannot live in the artwork at all, so the destinations are
    carried by the strip beneath it instead.
    """
    n, total, private = data["n"], data["total"], data["private"]
    if private:
        about = "about " if data.get("approx") else ""
        stats = ("%d original public repositories. Most of the work is not here: over the "
                 "last 12 months, %s%s of %s contributions were in private repositories "
                 "(client delivery, product builds, and security research)."
                 % (n, about, format(private, ","), format(total, ",")))
    else:
        stats = ("%d original public repositories, out of %s contributions in the last 12 "
                 "months." % (n, format(total, ",")))
    links = data.get("dbt_links") or []
    evidence = ""
    if links:
        state = "All open and review-only." if data.get("all_open") else "Some have since been merged."
        evidence = ("Evidence trail for ripple-proof runs across four public sibling dbt "
                    "repositories: " + ", ".join(a for a, _ in links) + ". " + state)
    return {
        "name": NAME, "handle": HANDLE, "email": EMAIL, "intro": INTRO,
        "cta_title": CTA_TITLE,
        "cta_body": _plain(CTA_BODY),
        "cta_cmd": CTA_CMD,
        "cta_after": _plain(CTA_AFTER),
        "footer": [_plain(x) for x in FOOTER],
        "stack": STACK, "stack_intro": STACK_INTRO,
        "upstream": _plain(UPSTREAM),
        "stats": stats, "evidence": evidence,
    }


def _plain(s):
    """Markdown to plain text: drop code ticks, keep a link's label, drop its URL."""
    s = re.sub(r"\[([^\]]+)\]\([^)\s]+\)", r"\1", s)
    s = re.sub(r"<([\w.+-]+@[\w.-]+)>", r"\1", s)
    return s.replace("`", "").replace("**", "")


def link_strip(data):
    """Every destination on the page, in one line.

    GitHub strips <map> and <area>, so a clickable region inside an image is impossible
    and only a whole image can be a link. With the page drawn as artwork, this is where
    the links live."""
    items = list(LINKS)
    items.append(("walkthrough", "https://itxcrusher.github.io/ripple-proof/"))
    for r in data.get("picked") or []:
        items.append((r["name"], r["url"]))
    for label, url in (data.get("dbt_links") or []):
        items.append(("dbt " + label, url))
    items.append(("skip_cache PR", "https://github.com/acryldata/mcp-server-datahub/pull/190"))
    items.append(("repair-boundary PR", "https://github.com/datahub-project/datahub-skills/pull/125"))
    return items


def render_readme(theme, data, today, mode, n_themes):
    t = theme
    text = t["text"]
    sep = " %s " % text.get("sep", "|")
    c = art_content(data, today)
    pages = "%s/%s" % (page_art.PAGES_DIR, t["slug"])
    out = []
    art = "assets/art/" + t["slug"]
    out.append("<!-- theme: %s | mode: %s | date: %s -->" % (t["slug"], mode, today))
    out.append(picture(art, "hero", "%s, GitHub handle %s. %s theme."
                       % (NAME, HANDLE, t["name"])))
    out.append("")
    out.append(page_art.picture(pages, "top", _attr(TOP_ALT)))
    out.append("")
    # The commands are drawn in the artwork, where they cannot be selected. This is the
    # copyable original, collapsed so it does not repeat the panel above it.
    out.append("<details><summary><sub>copy the commands</sub></summary>")
    out.append("")
    out.append("```")
    for cmd in CTA_CMD:
        out.append(cmd)
    out.append("```")
    out.append("")
    out.append("</details>")
    out.append("")
    out.append(START)
    out.append("")
    out.append("## " + page_art.picture(page_art.TODAY_DIR, "work",
                                        _attr("%s and %s" % (t["labels"]["public"],
                                                             t["labels"]["stack"]))))
    out.append("")
    out.append("## <picture>"
               '<source media="(prefers-color-scheme: dark)" srcset="%ssnake-dark.svg">'
               '<source media="(prefers-color-scheme: light)" srcset="%ssnake-light.svg">'
               '<img src="%ssnake-light.svg" width="100%%" alt="%s" />'
               "</picture>" % (OUTPUT_BRANCH, OUTPUT_BRANCH, OUTPUT_BRANCH, _attr(SNAKE_ALT)))
    out.append("")
    out.append(picture(art, "signoff", "Closing line at the end of the page: %s"
                       % t["signoff"]))
    out.append("")
    out.append(page_art.picture(pages, "close", _attr(CLOSE_ALT)))
    out.append("")
    out.append('<p align="center"><sub>')
    out.append("  " + sep.join('<a href="%s">%s</a>' % (u, l) for l, u in link_strip(data)))
    out.append("</sub></p>")
    out.append("")
    # The page above is artwork, so none of it can be selected, searched or translated.
    # This is the same page as text. R3 fails the build if it goes missing.
    out.append("<details><summary><sub>the whole page as plain text</sub></summary>")
    out.append("")
    for para in INTRO:
        out.append(para)
        out.append("")
    out.append("**%s** %s" % (CTA_TITLE, CTA_BODY))
    out.append("")
    out.append(CTA_AFTER)
    out.append("")
    out.append(c["stats"])
    out.append("")
    for r in data["picked"]:
        lang = (r.get("lang") + ". ") if r.get("lang") else ""
        out.append("- **[%s](%s)** - %s. %sUpdated %s." % (
            r["name"], r["url"], r["desc"].rstrip("."), lang, r["date"]))
    out.append("")
    if c["evidence"]:
        out.append(c["evidence"])
        out.append("")
    out.append(STACK_INTRO)
    out.append("")
    for label, values in STACK:
        out.append("- **%s** - %s" % (label, ", ".join(values)))
    out.append("")
    out.append(UPSTREAM)
    out.append("")
    for line in FOOTER:
        out.append(line)
        out.append("")
    out.append("_Generated %s from the GitHub API._" % today)
    out.append("")
    out.append("</details>")
    out.append("")
    out.append(END)
    out.append("")
    out.append("<sub>Today this page wears <b>%s</b>, one of %d looks it rotates through daily. "
               "<a href=\"assets/pages/README.md\">See them all</a>.</sub>" % (t["name"], n_themes))
    out.append("")
    md = "\n".join(out)
    assert all(ord(ch) < 128 for ch in md), "R5: README output is not plain ASCII"
    return md


def parse_stamp(readme_text):
    m = THEME_STAMP_RE.search(readme_text)
    return m.groups() if m else None


def fixture_data(today=None):
    """Sample data with real values from the live profile block, for previews and tests."""
    return {
        "n": 19, "total": 6279, "private": 4952, "approx": False, "freshest_days": 0,
        "picked": [
            {"name": "ripple-proof", "url": "https://github.com/itxcrusher/ripple-proof",
             "desc": "Bounded PostgreSQL column-rename agent: turns DataHub lineage evidence into validated dbt repairs across repositories, refuses ambiguous or stale evidence, and stops at human-reviewed pull requests",
             "lang": "Python", "date": "2026-08-09", "home": "https://itxcrusher.github.io/ripple-proof/"},
            {"name": "vision-ai-poc", "url": "https://github.com/itxcrusher/vision-ai-poc",
             "desc": "Real-time people detection, per-zone counting and dwell tracking with YOLOv8, ByteTrack and OpenCV. Runs as a local GUI demo or headless against RTSP cameras with server-fetched zones and privacy masking",
             "lang": "Python", "date": "2026-08-26", "home": ""},
            {"name": "kind-cluster-recovery", "url": "https://github.com/itxcrusher/kind-cluster-recovery",
             "desc": "Four-node KIND cluster provisioned onto a remote host with Terraform over SSH, then debugged: CoreDNS Corefile repair, crash-loop recovery, and a least-privilege NetworkPolicy expressed in Terraform",
             "lang": "HCL", "date": "2026-08-26", "home": ""},
            {"name": "k8s-gitops-platform", "url": "https://github.com/itxcrusher/k8s-gitops-platform",
             "desc": "ArgoCD app-of-apps GitOps configuration for a 17-service Kubernetes platform: parameterised Helm charts, an ELK logging stack, and cert-manager across three environments. Generalised from production",
             "lang": "", "date": "2026-08-22", "home": ""},
            {"name": "wordpress-fargate-deployment", "url": "https://github.com/itxcrusher/wordpress-fargate-deployment",
             "desc": "AWS CloudFormation template and helper scripts to deploy a production-ready WordPress environment on AWS Fargate with RDS, EFS, and an Application Load Balancer",
             "lang": "Shell", "date": "2025-08-08", "home": ""},
            {"name": "azure-devops-demo", "url": "https://github.com/itxcrusher/azure-devops-demo",
             "desc": "End-to-end Terraform and GitHub Actions pipeline that deploys a containerized service to Azure, with six reusable Terraform modules",
             "lang": "HCL", "date": "2025-05-16", "home": ""},
        ],
        "dbt_links": [("analytics", "https://github.com/itxcrusher/ripple-proof-dbt-analytics/pull/6"),
                      ("finance", "https://github.com/itxcrusher/ripple-proof-dbt-finance/pull/6"),
                      ("growth", "https://github.com/itxcrusher/ripple-proof-dbt-growth/pull/5"),
                      ("operations", "https://github.com/itxcrusher/ripple-proof-dbt-operations/pull/5")],
        "all_open": True,
        "today": today or datetime.date.today().isoformat(),
    }
