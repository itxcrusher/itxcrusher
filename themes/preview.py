"""Gallery outputs built from the same engine output that ships.

  gallery_markdown(themes)      assets/themes/README.md, browsable on GitHub
  preview_html(themes, ...)     a self-contained page: every theme, both GitHub colour
                                modes, the full README as GitHub lays it out
"""
import base64
import datetime
import html
import json
import re

from . import page as P
from .catalog import FAMILIES, snake_colours
from .render import build_theme
from .rotate import schedule


# ------------------------------------------------------------------ gallery README

def gallery_markdown(themes, n_active):
    out = ["# The themes", "",
           "This profile wears a different look every day. The pick is a date-seeded draw from "
           "the %d themes below, never the same as yesterday, made by "
           "`.github/workflows/profile.yml` at 03:17 UTC. Every asset is a committed SVG in "
           "this directory; nothing is fetched from a third party." % n_active, "",
           "Each theme changes the hero, the section headers, the sign-off strip, the "
           "contribution snake colours, the repository row style, the stack fence language, "
           "and the callout colour. The prose is the same every day.", ""]
    for fam, title in FAMILIES.items():
        rows = [t for t in themes if t["family"] == fam]
        if not rows:
            continue
        out.append("## " + title)
        out.append("")
        for t in rows:
            d = "assets/themes/" + t["slug"]
            out.append("### %s" % t["name"])
            out.append("")
            out.append(P.picture(d, "hero", "%s theme hero: %s" % (t["name"], t["tagline"])).replace("./assets/themes/", "./"))
            out.append("")
            out.append("%s <sub>rows: %s, fence: %s, callout: %s%s</sub>" % (
                t["tagline"], t["text"].get("rows", "list"), t["text"].get("fence", "text"),
                t["text"].get("alert", "NOTE"), ", disabled" if t.get("disabled") else ""))
            out.append("")
    out.append("To add one: append an entry to `themes/catalog.py`, run "
               "`python scripts/profile_theme.py build`, look at the result here, commit.")
    out.append("")
    md = "\n".join(out)
    assert all(ord(ch) < 128 for ch in md)
    return md


# ------------------------------------------------------- markdown subset -> HTML

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ITAL = re.compile(r"(?<![\w*])_(.+?)_(?![\w*])")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
AUTOMAIL = re.compile(r"<([\w.+-]+@[\w.-]+)>")


def inline(s):
    s = AUTOMAIL.sub(lambda m: '<a href="mailto:%s">%s</a>' % (m.group(1), m.group(1)), s)
    s = INLINE_CODE.sub(lambda m: "<code>%s</code>" % html.escape(m.group(1)), s)
    s = BOLD.sub(r"<strong>\1</strong>", s)
    s = LINK.sub(r'<a href="\2">\1</a>', s)
    s = ITAL.sub(r"<em>\1</em>", s)
    return s


def highlight(lang, code):
    """A small, honest approximation of GitHub's syntax colours for the fence languages
    the catalog uses. Classes: k key/entity, s string, c comment, n number, add/del diff."""
    out = []
    for line in code.split("\n"):
        e = html.escape(line)
        if lang == "diff":
            if line.startswith("+"):
                out.append('<span class="add">%s</span>' % e)
            elif line.startswith("-"):
                out.append('<span class="del">%s</span>' % e)
            else:
                out.append(e)
            continue
        if lang == "text":
            out.append(e)
            continue
        e = re.sub(r"(&quot;[^&]*?&quot;)", r'<span class="s">\1</span>', e)
        e = re.sub(r"(^|\s)(#.*)$", r'\1<span class="c">\2</span>', e)
        if lang in ("yaml", "json", "toml", "hcl", "ini", "python", "css", "makefile"):
            e = re.sub(r"^(\s*)([A-Za-z_.][\w.-]*)(\s*)(=|:)", r'\1<span class="k">\2</span>\3\4', e)
            e = re.sub(r"^(\s*)(&quot;[^&]*?&quot;)(\s*:)", r'\1<span class="k">\2</span>\3', e)
            e = re.sub(r"^(\[[^\]]+\])$", r'<span class="k">\1</span>', e)
        if lang == "bash":
            e = re.sub(r"^([a-z_]+)(=)", r'<span class="k">\1</span>\2', e)
        if lang == "python":
            e = e.replace("stack", '<span class="k">stack</span>', 1)
        out.append(e)
    return "\n".join(out)


class Converter:
    def __init__(self, slug):
        self.slug = slug

    def picture_tag(self, block):
        m = re.search(r'srcset="([^"]+)"', block)
        src = m.group(1)
        alt = re.search(r'alt="([^"]*)"', block).group(1)
        if src.startswith("http"):
            return '<img class="snake" data-snake="1" alt="%s">' % html.escape(alt)
        stem = re.search(r"/([a-z-]+)-(dark|light)\.svg$", src).group(1)
        return '<img class="th" data-stem="%s" width="100%%" alt="%s">' % (stem, html.escape(alt))

    def convert(self, md):
        lines = md.split("\n")
        out = []
        i = 0
        n = len(lines)
        while i < n:
            ln = lines[i]
            s = ln.strip()
            if not s or s.startswith("<!--"):
                i += 1
                continue
            if s.startswith("<picture>"):
                j = i
                while not lines[j].strip().startswith("</picture>"):
                    j += 1
                out.append(self.picture_tag("\n".join(lines[i:j + 1])))
                i = j + 1
                continue
            if s.startswith('<p align="center">'):
                j = i
                while not lines[j].strip().startswith("</p>"):
                    j += 1
                out.append('<p align="center">' + " ".join(x.strip() for x in lines[i + 1:j]) + "</p>")
                i = j + 1
                continue
            if s.startswith("<details>"):
                j = i
                while not lines[j].strip().startswith("</details>"):
                    j += 1
                inner = "\n".join(lines[i + 1:j])
                summ = re.search(r"<summary>(.*?)</summary>", inner).group(1)
                pic = re.search(r"<picture>[\s\S]*?</picture>", inner)
                body = self.picture_tag(pic.group(0)) if pic else ""
                out.append('<details open><summary>%s</summary><br><p align="center">%s</p></details>' % (summ, body))
                i = j + 1
                continue
            if s.startswith("> [!"):
                kind = re.match(r"> \[!(\w+)\]", s).group(1)
                j = i + 1
                body = []
                while j < n and lines[j].startswith(">"):
                    body.append(lines[j][1:].lstrip(" ") if lines[j] != ">" else "")
                    j += 1
                out.append('<div class="alert alert-%s"><p class="alert-title">%s</p>%s</div>' % (
                    kind.lower(), kind.title(), self.convert("\n".join(body))))
                i = j
                continue
            if s.startswith(">"):
                j = i
                body = []
                while j < n and lines[j].startswith(">"):
                    body.append(lines[j][1:].lstrip(" "))
                    j += 1
                out.append("<blockquote>%s</blockquote>" % self.convert("\n".join(body)))
                i = j
                continue
            if s.startswith("```"):
                lang = s[3:].strip() or "text"
                j = i + 1
                code = []
                while j < n and not lines[j].strip().startswith("```"):
                    code.append(lines[j])
                    j += 1
                out.append('<pre><code class="lang-%s">%s</code></pre>' % (lang, highlight(lang, "\n".join(code))))
                i = j + 1
                continue
            if s.startswith("|"):
                j = i
                rows = []
                while j < n and lines[j].strip().startswith("|"):
                    rows.append([c.strip() for c in lines[j].strip().strip("|").split(" | ")])
                    j += 1
                head, body = rows[0], rows[2:]
                t = ["<table><thead><tr>" + "".join("<th>%s</th>" % inline(c) for c in head) + "</tr></thead><tbody>"]
                for r in body:
                    t.append("<tr>" + "".join("<td>%s</td>" % inline(c.replace("\\|", "|")) for c in r) + "</tr>")
                t.append("</tbody></table>")
                out.append("".join(t))
                i = j
                continue
            if re.match(r"^(- |\d+\. )", s):
                ordered = s[0].isdigit()
                j = i
                items = []
                while j < n and re.match(r"^(- |\d+\. )", lines[j].strip()):
                    it = re.sub(r"^(- |\d+\. )", "", lines[j].strip())
                    cls = ""
                    if it.startswith("[x] "):
                        it = '<input type="checkbox" checked disabled> ' + it[4:]
                        cls = ' class="task"'
                    items.append("<li%s>%s</li>" % (cls, inline(it)))
                    j += 1
                out.append(("<ol>%s</ol>" if ordered else "<ul>%s</ul>") % "".join(items))
                i = j
                continue
            if s.startswith("<sub>") or s.startswith("<"):
                out.append("<p>%s</p>" % inline(s))
                i += 1
                continue
            # paragraph: gather consecutive plain lines
            j = i
            para = []
            while j < n and lines[j].strip() and not re.match(r"^(<|>|```|\||- |\d+\. )", lines[j].strip()):
                para.append(lines[j].strip())
                j += 1
            out.append("<p>%s</p>" % inline(" ".join(para)))
            i = j
        return "\n".join(out)


# ------------------------------------------------------------------ the page

def _b64(s):
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def preview_html(themes, data, today, snake_svg=None, n_active=None):
    n_active = n_active or len([t for t in themes if not t.get("disabled")])
    assets, pages, meta = {}, {}, []
    for t in themes:
        files = build_theme(t)
        for fn, svg in files.items():
            assets["%s/%s" % (t["slug"], fn[:-4])] = _b64(svg)
        md = P.render_readme(t, data, today, "preview", n_active)
        pages[t["slug"]] = Converter(t["slug"]).convert(md)
        sd, sl = snake_colours(t, "dark"), snake_colours(t, "light")
        meta.append(dict(slug=t["slug"], name=t["name"], family=t["family"], tagline=t["tagline"],
                         rows=t["text"].get("rows", "list"), fence=t["text"].get("fence", "text"),
                         alert=t["text"].get("alert", "NOTE"), disabled=bool(t.get("disabled")),
                         dark=t["dark"], light=t["light"],
                         snake=dict(dark=dict(snake=sd[0], dots=sd[1]), light=dict(snake=sl[0], dots=sl[1]))))
    start = datetime.date.fromisoformat(today)
    sched = schedule(start, 14)
    names = {t["slug"]: t["name"] for t in themes}
    sched = [(d, s, names.get(s, s)) for d, s in sched]
    snake_b64 = _b64(snake_svg) if snake_svg else ""
    payload = json.dumps(dict(assets=assets, pages=pages, meta=meta, schedule=sched, snake=snake_b64,
                              families=FAMILIES, today=today, n=n_active), separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    return TEMPLATE.replace("/*DATA*/", payload).replace("/*TODAY*/", today).replace("/*N*/", str(n_active))


TEMPLATE = r"""<title>Profile Wardrobe</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --bg:#eef0f4;--bg2:#ffffff;--ink:#141821;--muted:#5b6474;--line:#d3d8e2;--rail:#e6e9ef;
  --act:#141821;--act-ink:#ffffff;--focus:#3b5bdb;
  --gh-bg:#ffffff;--gh-bg2:#f6f8fa;--gh-ink:#1f2328;--gh-muted:#59636e;--gh-line:#d1d9e0;--gh-link:#0969da;
  --gh-code:#f6f8fa;--gh-header:#f6f8fa;--gh-kbd:#f6f8fa;--gh-kbd-line:#d1d9e0;
  --a-note:#0969da;--a-tip:#1a7f37;--a-imp:#8250df;--a-warn:#9a6700;--a-caut:#cf222e;
  --s:#0a3069;--k:#116329;--c:#59636e;--add-bg:#dafbe1;--add:#1a7f37;--del-bg:#ffebe9;--del:#cf222e;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0b0d12;--bg2:#12151c;--ink:#e8ebf1;--muted:#9aa3b2;--line:#262b36;--rail:#0f1218;
  --act:#e8ebf1;--act-ink:#0b0d12;--focus:#7b93ff;
}}
:root[data-theme="dark"]{
  --bg:#0b0d12;--bg2:#12151c;--ink:#e8ebf1;--muted:#9aa3b2;--line:#262b36;--rail:#0f1218;
  --act:#e8ebf1;--act-ink:#0b0d12;--focus:#7b93ff;
}
.gh.dark{
  --gh-bg:#0d1117;--gh-bg2:#161b22;--gh-ink:#e6edf3;--gh-muted:#9198a1;--gh-line:#3d444d;--gh-link:#4493f8;
  --gh-code:#161b22;--gh-header:#010409;--gh-kbd:#161b22;--gh-kbd-line:#3d444d;
  --a-note:#1f6feb;--a-tip:#238636;--a-imp:#8957e5;--a-warn:#9e6a03;--a-caut:#da3633;
  --s:#a5d6ff;--k:#7ee787;--c:#8b949e;--add-bg:rgba(46,160,67,.15);--add:#3fb950;--del-bg:rgba(248,81,73,.15);--del:#f85149;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Familjen Grotesk",system-ui,sans-serif;min-height:100vh}
a{color:inherit}
.top{display:flex;align-items:center;gap:18px;padding:14px 22px;border-bottom:1px solid var(--line);background:var(--bg2);position:sticky;top:0;z-index:5;flex-wrap:wrap}
.top h1{font-size:19px;margin:0;font-weight:700;letter-spacing:-.01em}
.top .sub{color:var(--muted);font:500 12px/1 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.04em;text-transform:uppercase}
.spacer{flex:1}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.seg button{border:0;background:transparent;color:var(--ink);padding:7px 12px;font:500 13px "IBM Plex Mono",ui-monospace,monospace;cursor:pointer}
.seg button.on{background:var(--act);color:var(--act-ink)}
.seg button:focus-visible,.chip:focus-visible,.btn:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.btn{border:1px solid var(--line);background:var(--bg2);color:var(--ink);border-radius:8px;padding:7px 12px;font:500 13px "IBM Plex Mono",ui-monospace,monospace;cursor:pointer}
.wrap{display:grid;grid-template-columns:250px 1fr;gap:0;min-height:calc(100vh - 60px)}
.rail{border-right:1px solid var(--line);background:var(--rail);padding:16px 12px 40px;overflow-y:auto;max-height:calc(100vh - 60px);position:sticky;top:60px}
.fam{font:500 11px/1 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:14px 6px 8px}
.fam:first-child{margin-top:0}
.chips{display:flex;flex-direction:column;gap:4px}
.chip{display:flex;align-items:center;gap:10px;border:1px solid transparent;background:transparent;color:var(--ink);text-align:left;padding:6px 8px;border-radius:8px;cursor:pointer;font:500 14px "Familjen Grotesk",system-ui,sans-serif}
.chip:hover{border-color:var(--line);background:var(--bg2)}
.chip.on{background:var(--act);color:var(--act-ink)}
.sw{width:26px;height:16px;border-radius:4px;flex:none;background:linear-gradient(90deg,var(--c1) 0 50%,var(--c2) 50% 100%);border:1px solid rgba(0,0,0,.15)}
.chip .tag{margin-left:auto;font:400 10px "IBM Plex Mono",ui-monospace,monospace;opacity:.6}
.main{padding:22px 26px 60px;overflow-x:auto}
.about{display:flex;gap:18px;align-items:baseline;flex-wrap:wrap;margin:0 0 14px}
.about h2{margin:0;font-size:26px;letter-spacing:-.02em}
.about p{margin:0;color:var(--muted);max-width:60ch}
.facts{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px}
.fact{font:500 12px "IBM Plex Mono",ui-monospace,monospace;border:1px solid var(--line);border-radius:999px;padding:4px 10px;color:var(--muted)}
.fact b{color:var(--ink);font-weight:500}
/* the GitHub mock */
.gh{background:var(--gh-bg);color:var(--gh-ink);border:1px solid var(--gh-line);border-radius:12px;overflow:hidden;width:1180px;max-width:100%;font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}
.gh-head{background:var(--gh-header);border-bottom:1px solid var(--gh-line);padding:12px 18px;display:flex;align-items:center;gap:14px;font-size:14px}
.gh-head .logo{width:26px;height:26px;border-radius:50%;background:var(--gh-ink);display:inline-block}
.gh-head .crumb{color:var(--gh-muted)}
.gh-body{display:grid;grid-template-columns:296px 846px;gap:24px;padding:24px}
.side .av{width:296px;height:296px;border-radius:50%;background:var(--sv-bg,#111);color:var(--sv-ink,#fff);display:flex;align-items:center;justify-content:center;font:700 92px/1 "Familjen Grotesk",system-ui,sans-serif;letter-spacing:-.04em;border:1px solid var(--gh-line)}
.side h3{margin:16px 0 0;font-size:24px;line-height:1.25}
.side .h{color:var(--gh-muted);font-size:20px;font-weight:300;margin:0 0 12px}
.side .status{display:inline-flex;gap:6px;align-items:center;border:1px solid var(--gh-line);border-radius:999px;padding:3px 10px;font-size:12px;margin:0 0 12px;background:var(--gh-bg)}
.side p{margin:0 0 12px}
.side .meta{font-size:14px;color:var(--gh-muted);display:flex;flex-direction:column;gap:6px}
.side .meta a{color:var(--gh-ink);text-decoration:none}
.readme{border:1px solid var(--gh-line);border-radius:8px;padding:0 0 4px}
.readme .bar{border-bottom:1px solid var(--gh-line);padding:10px 16px;font-size:12px;color:var(--gh-muted)}
.md{padding:24px 32px;overflow-wrap:anywhere}
.md p{margin:0 0 16px}
.md img.th{display:block;max-width:100%;margin:0 0 16px}
.md img.snake{max-width:100%}
.md a{color:var(--gh-link);text-decoration:none}
.md a:hover{text-decoration:underline}
.md code{background:color-mix(in srgb,var(--gh-ink) 8%,transparent);padding:.2em .4em;border-radius:6px;font:85% ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.md pre{background:var(--gh-code);border-radius:6px;padding:16px;overflow-x:auto;margin:0 0 16px;font:85%/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.md pre code{background:none;padding:0;font-size:100%}
.md .s{color:var(--s)}.md .k{color:var(--k)}.md .c{color:var(--c)}
.md .add{display:block;background:var(--add-bg);color:var(--add)}.md .del{display:block;background:var(--del-bg);color:var(--del)}
.md .alert{border-left:4px solid var(--a-note);padding:8px 16px;margin:0 0 16px;color:var(--gh-ink)}
.md .alert-tip{border-color:var(--a-tip)}.md .alert-important{border-color:var(--a-imp)}.md .alert-warning{border-color:var(--a-warn)}.md .alert-caution{border-color:var(--a-caut)}
.md .alert-title{font-weight:600;color:var(--a-note);margin:0 0 8px}
.md .alert-tip .alert-title{color:var(--a-tip)}.md .alert-important .alert-title{color:var(--a-imp)}.md .alert-warning .alert-title{color:var(--a-warn)}.md .alert-caution .alert-title{color:var(--a-caut)}
.md .alert p:last-child,.md blockquote p:last-child{margin-bottom:0}
.md blockquote{border-left:4px solid var(--gh-line);color:var(--gh-muted);padding:0 16px;margin:0 0 16px}
.md ul,.md ol{padding-left:2em;margin:0 0 16px}
.md li{margin:4px 0}
.md li.task{list-style:none;margin-left:-1.5em}
.md table{border-collapse:collapse;margin:0 0 16px;display:block;overflow-x:auto;max-width:100%}
.md th,.md td{border:1px solid var(--gh-line);padding:6px 13px;vertical-align:top}
.md th{font-weight:600}
.md tr:nth-child(2n) td{background:var(--gh-bg2)}
.md kbd{display:inline-block;padding:3px 5px;font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;line-height:10px;color:var(--gh-ink);vertical-align:middle;background:var(--gh-kbd);border:1px solid var(--gh-kbd-line);border-radius:6px;box-shadow:inset 0 -1px 0 var(--gh-kbd-line)}
.md sub{font-size:75%;color:var(--gh-muted)}
.md details{margin:0 0 16px}
.md summary{cursor:pointer}
.md hr{border:0;border-top:4px solid var(--gh-line);margin:24px 0}
/* schedule */
.sched{margin:22px 0 0;max-width:1180px}
.sched h3{margin:0 0 8px;font-size:15px}
.days{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}
.day{border:1px solid var(--line);background:var(--bg2);border-radius:10px;padding:10px 12px;cursor:pointer;text-align:left;color:var(--ink);font:inherit}
.day:hover{border-color:var(--muted)}
.day .d{font:500 11px "IBM Plex Mono",ui-monospace,monospace;color:var(--muted);letter-spacing:.04em}
.day .n{font-weight:700;margin-top:4px;display:flex;align-items:center;gap:8px}
.day.today{outline:2px solid var(--focus);outline-offset:1px}
@media (max-width:1100px){
  .wrap{grid-template-columns:1fr}
  .rail{position:static;max-height:none;border-right:0;border-bottom:1px solid var(--line)}
  .chips{flex-direction:row;flex-wrap:wrap}
  .gh-body{grid-template-columns:1fr}
  .side .av{width:120px;height:120px;font-size:40px}
  .days{grid-template-columns:repeat(2,1fr)}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="top">
  <h1>Profile Wardrobe</h1>
  <span class="sub">itxcrusher / <span id="count">/*N*/</span> looks, one a day</span>
  <span class="spacer"></span>
  <button class="btn" id="shuffle" type="button">Surprise me</button>
  <div class="seg" role="group" aria-label="GitHub colour mode">
    <button type="button" id="mdark" class="on">GitHub dark</button>
    <button type="button" id="mlight">GitHub light</button>
  </div>
</div>

<div class="wrap">
  <nav class="rail" id="rail" aria-label="Themes"></nav>
  <main class="main">
    <div class="about">
      <h2 id="tname"></h2>
      <p id="ttag"></p>
    </div>
    <div class="facts" id="facts"></div>
    <div class="gh dark" id="gh">
      <div class="gh-head"><span class="logo"></span><span class="crumb">github.com / itxcrusher</span></div>
      <div class="gh-body">
        <aside class="side">
          <div class="av" id="av">C</div>
          <h3>CRUSHER</h3>
          <p class="h">itxcrusher</p>
          <p class="status"><span>&#127919;</span> Focusing</p>
          <p>Cloud and platform engineer. Terraform, Kubernetes, GitOps. I run InfraForge, a DevOps and infra-recovery practice.</p>
          <div class="meta">
            <span>@infraforge-agency</span>
            <a href="https://muhammadhassaanjaved.com">muhammadhassaanjaved.com</a>
            <a href="https://www.linkedin.com/in/itxcrusher">in/itxcrusher</a>
          </div>
        </aside>
        <section class="readme">
          <div class="bar">itxcrusher / README.md</div>
          <article class="md" id="md"></article>
        </section>
      </div>
    </div>
    <div class="sched">
      <h3>The next two weeks, as the daily draw will pick them</h3>
      <div class="days" id="days"></div>
    </div>
  </main>
</div>

<script>
const D = /*DATA*/;
let variant = 'dark';
let current = null;
const $ = (s) => document.querySelector(s);

function uri(key){ return 'data:image/svg+xml;base64,' + D.assets[key]; }
function snakeUri(meta, v){
  if(!D.snake) return '';
  const svg = atob(D.snake);
  const s = meta.snake[v];
  const root = ':root{--cb:#1b1f230a;--cs:' + s.snake + ';--ce:' + s.dots[0] + ';--c0:' + s.dots[0] +
    ';--c1:' + s.dots[1] + ';--c2:' + s.dots[2] + ';--c3:' + s.dots[3] + ';--c4:' + s.dots[4] + '}';
  const out = svg.replace(/:root\{[^}]*\}/, root);
  return 'data:image/svg+xml;base64,' + btoa(out);
}
function buildRail(){
  const rail = $('#rail');
  let h = '';
  for (const fam in D.families){
    const rows = D.meta.filter(m => m.family === fam);
    if(!rows.length) continue;
    h += '<div class="fam">' + D.families[fam] + '</div><div class="chips">';
    for (const m of rows){
      h += '<button type="button" class="chip" data-slug="' + m.slug + '" style="--c1:' + m.dark.acc + ';--c2:' + m.light.acc + '">' +
           '<span class="sw"></span>' + m.name + '<span class="tag">' + m.rows + '</span></button>';
    }
    h += '</div>';
  }
  rail.innerHTML = h;
  rail.addEventListener('click', e => { const b = e.target.closest('.chip'); if(b) select(b.dataset.slug); });
}
function paintImages(){
  const meta = D.meta.find(m => m.slug === current);
  document.querySelectorAll('#md img.th').forEach(img => { img.src = uri(current + '/' + img.dataset.stem + '-' + variant); });
  document.querySelectorAll('#md img.snake').forEach(img => { img.src = snakeUri(meta, variant); });
  const gh = $('#gh'); gh.classList.toggle('dark', variant === 'dark'); gh.classList.toggle('light', variant === 'light');
  const p = meta[variant];
  $('#av').style.setProperty('--sv-bg', p.bg2); $('#av').style.setProperty('--sv-ink', p.acc);
  $('#mdark').classList.toggle('on', variant === 'dark'); $('#mlight').classList.toggle('on', variant === 'light');
}
function select(slug){
  current = slug;
  const meta = D.meta.find(m => m.slug === slug);
  $('#md').innerHTML = D.pages[slug];
  $('#tname').textContent = meta.name;
  $('#ttag').textContent = meta.tagline;
  $('#facts').innerHTML = [['rows', meta.rows], ['fence', meta.fence], ['callout', meta.alert], ['family', D.families[meta.family]]]
    .map(([k, v]) => '<span class="fact">' + k + ' <b>' + v + '</b></span>').join('');
  document.querySelectorAll('.chip').forEach(c => c.classList.toggle('on', c.dataset.slug === slug));
  paintImages();
  try { localStorage.setItem('wardrobe.theme', slug); } catch(e) {}
}
function buildSchedule(){
  const names = Object.fromEntries(D.meta.map(m => [m.slug, m]));
  $('#days').innerHTML = D.schedule.map(([d, s, n], i) => {
    const m = names[s];
    return '<button type="button" class="day' + (i === 0 ? ' today' : '') + '" data-slug="' + s + '"><div class="d">' + d + (i === 0 ? ' &middot; today' : '') +
      '</div><div class="n"><span class="sw" style="--c1:' + m.dark.acc + ';--c2:' + m.light.acc + '"></span>' + n + '</div></button>';
  }).join('');
  $('#days').addEventListener('click', e => { const b = e.target.closest('.day'); if(b) select(b.dataset.slug); });
}
$('#mdark').addEventListener('click', () => { variant = 'dark'; paintImages(); try{localStorage.setItem('wardrobe.variant','dark')}catch(e){} });
$('#mlight').addEventListener('click', () => { variant = 'light'; paintImages(); try{localStorage.setItem('wardrobe.variant','light')}catch(e){} });
$('#shuffle').addEventListener('click', () => { const pool = D.meta.filter(m => !m.disabled && m.slug !== current); select(pool[Math.floor(Math.random() * pool.length)].slug); });
document.addEventListener('keydown', e => {
  if(e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
  const list = D.meta.map(m => m.slug); let i = list.indexOf(current);
  i = (i + (e.key === 'ArrowRight' ? 1 : -1) + list.length) % list.length; select(list[i]);
});
buildRail(); buildSchedule();
let first = D.schedule[0][1];
try { first = localStorage.getItem('wardrobe.theme') || first; const v = localStorage.getItem('wardrobe.variant'); if (v) variant = v; } catch(e) {}
if(!D.meta.some(m => m.slug === first)) first = D.meta[0].slug;
select(first);
</script>
"""
