#!/usr/bin/env python3
"""Render and apply the public-surface block for the itxcrusher profile README.

Python 3.11+ stdlib only. No installs, no lockfile, no local toolchain.

  render  queries the GitHub API and writes the block body to a file
  apply   splices that body between the PUBLIC_SURFACE markers in README.md
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

UA = {"User-Agent": "itxcrusher-profile-generator"}
START = "<!-- PUBLIC_SURFACE:START -->"
END = "<!-- PUBLIC_SURFACE:END -->"
STAMP_RE = re.compile(r"^_Generated (\d{4}-\d{2}-\d{2}) from the GitHub API\._$", re.M)
REPOS_TAB = "https://github.com/itxcrusher?tab=repositories&type=source&sort=pushed"
DBT_REPOS = ["analytics", "finance", "growth", "operations"]


def get(url, token=None):
    """GET a URL. Attaches the token for api.github.com only, for rate-limit headroom.

    The github.com/users/<u>/contributions HTML endpoint is documented token-free and
    is deliberately left unauthenticated.
    """
    headers = dict(UA)
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def graphql(query, variables, token):
    body = json.dumps({"query": query, "variables": variables}).encode()
    headers = dict(UA)
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def ascii_only(text, what):
    """Fold to ASCII.

    R5 bans codepoints above 127 anywhere in README.md, and repo descriptions are
    injected verbatim. One curly quote in an upstream description would otherwise fail
    the validate step on every run until a human noticed. Warn loudly, then fold.
    """
    bad = sorted(set(c for c in text if ord(c) > 127))
    if bad:
        print("warning: non-ASCII " + repr(bad) + " in " + what + "; folding. "
              "Fix the source field so this stays lossless.", file=sys.stderr)
        text = text.encode("ascii", "ignore").decode("ascii")
    return text.replace("|", "\\|").replace("<", "&lt;")


def calendar_total(user):
    """Total contributions including private. Unauthenticated, no token required."""
    html = get("https://github.com/users/" + user + "/contributions")
    m = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", html)
    if m:
        return int(m.group(1).replace(",", ""))
    # The fragment endpoint renders per-day tooltips rather than a page total. Sum them.
    days = re.findall(r">([\d,]+) contributions? on ", html)
    if days:
        return sum(int(d.replace(",", "")) for d in days)
    raise SystemExit("FATAL: could not parse the contributions calendar total")


def contribution_split(user, token, total):
    """Return (private_count, approximate)."""
    q = ("query($login:String!){user(login:$login){contributionsCollection{"
         "restrictedContributionsCount totalCommitContributions "
         "totalPullRequestContributions totalIssueContributions "
         "totalRepositoryContributions}}}")
    public_visible = None
    restricted = 0
    if token:
        try:
            d = graphql(q, {"login": user}, token)
            c = d["data"]["user"]["contributionsCollection"]
            restricted = c["restrictedContributionsCount"]
            public_visible = (c["totalCommitContributions"]
                              + c["totalPullRequestContributions"]
                              + c["totalIssueContributions"]
                              + c["totalRepositoryContributions"])
        except Exception as e:  # noqa: BLE001
            print("warning: GraphQL split unavailable: " + str(e), file=sys.stderr)
    if restricted > 0:
        return restricted, False
    # An installation token may report public-only counts. If the public calendar
    # clearly exceeds public-visible contributions, derive the split and say "about".
    if public_visible is not None and total - public_visible > 100:
        return total - public_visible, True
    return 0, False


def repos(user, token):
    data = json.loads(get(
        "https://api.github.com/users/" + user
        + "/repos?per_page=100&type=owner&sort=pushed", token))
    return [r for r in data
            if not r["fork"] and not r["archived"] and not r["private"]
            and r["name"] != user]


def showcased(rs):
    """Selection is a GitHub topic, never a hardcoded list.

    Rename a repo and nothing breaks. Archive it and it leaves the profile on the next
    run. Promote a project by adding one topic from the repo settings page.
    """
    picked = [r for r in rs if "showcase" in (r.get("topics") or [])]
    picked.sort(key=lambda r: (
        "showcase-lead" not in (r.get("topics") or []),
        -_epoch(r["pushed_at"]),
    ))
    return picked[:6]


def dbt_evidence(user, token):
    """Read the ripple-proof sibling PRs at render time.

    Hardcoding the PR numbers and the word "open" would put a fact in two systems,
    which is the exact thing this generated block exists to prevent. The day one is
    merged, the profile should say so by itself.
    """
    links = []
    states = []
    for name in DBT_REPOS:
        repo = user + "/ripple-proof-dbt-" + name
        try:
            prs = json.loads(get(
                "https://api.github.com/repos/" + repo
                + "/pulls?state=open&per_page=1", token))
        except urllib.error.HTTPError as e:
            print("warning: could not read PRs for " + repo + ": " + str(e),
                  file=sys.stderr)
            continue
        if not prs:
            states.append(False)
            continue
        states.append(True)
        links.append("[" + name + "](" + prs[0]["html_url"] + ")")
    return links, (bool(states) and all(states))


def _epoch(iso):
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


def days_since(iso):
    d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (datetime.datetime.now(datetime.timezone.utc) - d).days


def render(user, token, today):
    total = calendar_total(user)
    private, approx = contribution_split(user, token, total)
    all_public = repos(user, token)
    picked = showcased(all_public)
    lines = []

    n = len(all_public)
    if private:
        about = "about " if approx else ""
        lines.append(
            str(n) + " original public repositories. Most of the work is not here: "
            "over the last 12 months, " + about + format(private, ",") + " of "
            + format(total, ",") + " contributions were in private repositories "
            "(client delivery, product builds, and security research).")
    else:
        lines.append(
            str(n) + " original public repositories, out of " + format(total, ",")
            + " contributions in the last 12 months.")
    lines.append("")

    # There is deliberately no "shipped this month" lead. Adding a topic or a CI badge
    # touches pushed_at and would make that sentence true without any work having
    # shipped, which is the class of claim this profile is built to avoid.
    freshest = min([days_since(r["pushed_at"]) for r in picked] or [9999])
    if picked and freshest <= 120:
        lines.append("Most recent public work:")
        lines.append("")
        for r in picked:
            desc = ascii_only((r.get("description") or "").strip().rstrip("."),
                              "description of " + r["name"])
            lang = r.get("language") or "n/a"
            date = r["pushed_at"].split("T")[0]
            home = (r.get("homepage") or "").strip()
            extra = " [Walkthrough](" + home + ")" if home.startswith("http") else ""
            lines.append("- **[" + r["name"] + "](" + r["html_url"] + ")** - " + desc
                         + ". " + lang + ". Updated " + date + "." + extra)
        lines.append("")
    else:
        lines.append(
            "Nothing public has changed in the last four months. That is the normal "
            "state here. Start with [ripple-proof](https://github.com/" + user
            + "/ripple-proof), or browse [all source repositories](" + REPOS_TAB + ").")
        lines.append("")

    links, all_open = dbt_evidence(user, token)
    if links:
        state = "All open and review-only." if all_open else "Some have since been merged."
        lines.append(
            "Evidence trail for ripple-proof runs across four public sibling dbt "
            "repositories: " + ", ".join(links) + ". " + state)
        lines.append("")

    lines.append("_Generated " + today + " from the GitHub API._")
    return "\n".join(lines) + "\n"


def strip_stamp(text):
    return STAMP_RE.sub("", text).strip()


def apply(block_path, readme_path, max_age):
    new = open(block_path, encoding="utf-8").read()
    src = open(readme_path, encoding="utf-8").read()
    pat = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END))
    m = pat.search(src)
    if not m:
        raise SystemExit("FATAL: markers not found in " + readme_path)
    current = m.group(0)[len(START):-len(END)]

    body_changed = strip_stamp(current) != strip_stamp(new)
    stale = True
    sm = STAMP_RE.search(current)
    if sm:
        age = (datetime.date.today() - datetime.date.fromisoformat(sm.group(1))).days
        stale = age >= max_age

    changed = body_changed or stale
    if changed:
        out = src[:m.start()] + START + "\n" + new + END + src[m.end():]
        open(readme_path, "w", encoding="utf-8", newline="\n").write(out)

    gho = os.environ.get("GITHUB_OUTPUT")
    if gho:
        with open(gho, "a", encoding="utf-8") as f:
            f.write("changed=" + ("true" if changed else "false") + "\n")
    print("changed=" + str(changed) + " body_changed=" + str(body_changed)
          + " stale=" + str(stale))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("--user", required=True)
    r.add_argument("--out", required=True)
    a = sub.add_parser("apply")
    a.add_argument("--block", required=True)
    a.add_argument("--readme", required=True)
    a.add_argument("--max-stamp-age-days", type=int, default=7)
    args = p.parse_args()

    if args.cmd == "render":
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        today = datetime.date.today().isoformat()
        text = render(args.user, token, today)
        out_dir = os.path.dirname(args.out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        open(args.out, "w", encoding="utf-8", newline="\n").write(text)
        print(text)
    else:
        apply(args.block, args.readme, args.max_stamp_age_days)


if __name__ == "__main__":
    main()
