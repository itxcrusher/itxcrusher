"""The page: hand-authored content plus the README renderer.

The prose here is the hand-authored region of the old README, moved into one place so
the theme engine can lay it out. Every string the rendering contract requires to survive
image death (R3) is plain text in this file, never inside an SVG.
"""
import datetime
import json
import re

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
    "%s (%s). Infrastructure recovery and platform work: [infraforge.agency](https://infraforge.agency)" % (NAME, HANDLE),
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

def _row_bits(r, chip_style):
    desc = r["desc"].rstrip(".")
    lang = r.get("lang") or ""
    home = r.get("home") or ""
    walk = " [Walkthrough](%s)" % home if home.startswith("http") else ""
    return desc, lang, walk


def render_block(data, text, today):
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
                lines.append("| **[%s](%s)** | %s.%s | %s | %s |" % (
                    r["name"], r["url"], _esc_cell(desc), walk, chip(lang, chip_style), r["date"]))
        else:
            for i, r in enumerate(picked, 1):
                desc, lang, walk = _row_bits(r, chip_style)
                meta = ", ".join(x for x in (chip(lang, chip_style), "updated " + r["date"]) if x)
                if rows_style == "tasks":
                    lines.append("- [x] **[%s](%s)** - %s. <sub>%s.</sub>%s" % (r["name"], r["url"], desc, meta, walk))
                elif rows_style == "numbered":
                    lines.append("%d. **[%s](%s)** - %s. <sub>%s.</sub>%s" % (i, r["name"], r["url"], desc, meta, walk))
                elif rows_style == "quotes":
                    lines.append("> **[%s](%s)**<br>%s.<br><sub>%s.%s</sub>" % (r["name"], r["url"], desc, meta, walk))
                    lines.append("")
                elif rows_style == "ls":
                    lines.append("- `drwxr-xr-x` **[%s](%s)** %s `%s`<br>%s.%s" % (
                        r["name"], r["url"], chip(lang, "code"), r["date"], desc, walk))
                else:
                    lang_part = (lang + ". ") if lang else ""
                    lines.append("- **[%s](%s)** - %s. %sUpdated %s.%s" % (
                        r["name"], r["url"], desc, lang_part, r["date"], walk))
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

def render_readme(theme, data, today, mode, n_themes):
    t = theme
    text = t["text"]
    d = "assets/themes/" + t["slug"]
    sep = " %s " % text.get("sep", "|")
    out = []
    out.append("<!-- theme: %s | mode: %s | date: %s -->" % (t["slug"], mode, today))
    out.append(picture(d, "hero", "%s, GitHub handle %s. %s theme." % (NAME, HANDLE, t["name"])))
    out.append("")
    out.append('<p align="center">')
    out.append("  " + sep.join('<a href="%s">%s</a>' % (u, l) for l, u in LINKS))
    out.append("</p>")
    out.append("")
    for para in INTRO:
        out.append(para)
        out.append("")
    alert = text.get("alert", "NOTE")
    out.append("> [!%s]" % alert)
    out.append("> **%s**" % CTA_TITLE)
    out.append("> " + CTA_BODY)
    out.append(">")
    out.append("> ```")
    for cmd in CTA_CMD:
        out.append("> " + cmd)
    out.append("> ```")
    out.append(">")
    out.append("> " + CTA_AFTER)
    out.append("")
    out.append(heading_picture(d, "h-public", "%s" % t["labels"]["public"]))
    out.append("")
    out.append(START)
    out.append(render_block(data, text, today).rstrip("\n"))
    out.append(END)
    out.append("")
    out.append(heading_picture(d, "h-stack", "%s" % t["labels"]["stack"]))
    out.append("")
    out.append(STACK_INTRO)
    out.append("")
    out.append("```" + text.get("fence", "text"))
    out.append(format_stack(text.get("fence", "text")))
    out.append("```")
    out.append("")
    out.append(UPSTREAM)
    out.append("")
    out.append("<details>")
    out.append("<summary><b>%s</b></summary>" % t["labels"]["snake"])
    out.append("<br />")
    out.append('<p align="center">')
    out.append(snake_picture())
    out.append("</p>")
    out.append("</details>")
    out.append("")
    out.append(picture(d, "signoff", "Closing line at the end of the page: %s" % t["signoff"]))
    out.append("")
    for line in FOOTER:
        out.append(line)
        out.append("")
    out.append("<sub>Today this page wears <b>%s</b>, one of %d looks it rotates through daily. "
               "<a href=\"assets/themes/README.md\">See them all</a>.</sub>" % (t["name"], n_themes))
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
