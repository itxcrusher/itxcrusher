"""Compose a theme into its SVG assets: hero, section headers, sign-off strip.

Sizes are fixed so the README layout never shifts when the theme rotates:
  hero      900 x 240
  header    900 x 80
  sign-off  900 x 64
"""
from . import motifs as M
from .svg import (Canvas, fit, width, f, fo, so, mix, lighten, darken, contrast, MIN_FONT)

HERO_H, HEAD_H, SIGN_H = 240, 80, 64
NAME = "Muhammad Hassaan Javed"
HANDLE = "@itxcrusher"
TAGLINE = "cloud + platform engineer"
LEFT = 44

SECTIONS = ("public", "stack")


def palette(theme, variant):
    p = dict(theme[variant])
    p["variant"] = variant
    p.setdefault("muted", mix(p["ink"], p["bg"], 0.45))
    p.setdefault("acc2", p["acc"])
    return p


def _kw(kw, variant):
    """Merge motif kwargs: shared keys plus an optional dark:/light: override dict."""
    out = {k: v for k, v in kw.items() if k not in ("dark", "light")}
    out.update(kw.get(variant, {}))
    return out


def _run_motifs(c, p, box, spec, variant, stage):
    for item in spec.get(stage, []):
        name, kw = (item, {}) if isinstance(item, str) else item
        kw = _kw(kw, variant)
        if kw.pop("skip", False):
            continue
        region = kw.pop("region", None)
        b = box
        if region:
            rx, ry, rw, rh = region
            b = (box[0] + box[2] * rx, box[1] + box[3] * ry, box[2] * rw, box[3] * rh)
        getattr(M, name)(c, p, b, **kw)


# ------------------------------------------------------------------------ type block

def _name_text(theme):
    style = theme["hero"].get("type", "plain")
    case = theme["hero"].get("case", "as-is")
    s = NAME
    if case == "upper":
        s = s.upper()
    elif case == "lower":
        s = s.lower()
    return s, style


def type_block(c, p, theme, box):
    h = theme["hero"]
    style = h.get("type", "plain")
    if isinstance(style, dict):
        style = style.get(p["variant"], "plain")
    layout = h.get("layout", "left")
    kind = h.get("font", "sans")
    ls = h.get("ls", 0)
    # The name and the handle are enough; the hero no longer carries a job title.
    # Kept as an opt-in flag rather than deleted so a theme can reintroduce a line
    # of type under the handle if a composition ever needs the third weight.
    show_tag = h.get("tagline", False)
    reserve = h.get("reserve", 0)          # width kept clear on the far side for a focal
    max_w = 900 - 2 * LEFT - reserve
    name, _ = _name_text(theme)

    if layout == "left":
        x, anchor = LEFT, "start"
    elif layout == "center":
        x, anchor = 450, "middle"
        max_w = 900 - 2 * LEFT
    else:
        x, anchor = 900 - LEFT, "end"

    ink, acc, acc2, muted = p["ink"], p["acc"], p["acc2"], p["muted"]
    name_col = h.get("name_col", {}).get(p["variant"], ink) if isinstance(h.get("name_col"), dict) else ink
    handle_col = acc
    tag_col = muted

    if style == "console":
        # a terminal session: prompt line, the answer, and a cursor
        prompt = h.get("prompt", "root@itxcrusher:~# whoami")
        c.text(x, 72, prompt, MIN_FONT, acc2, "mono", 700)
        size, w, _ = fit(name, "mono", 700, max_w, 50)
        c.text(x, 124, name, size, ink, "mono", 700)
        c.text(x, 170, HANDLE, 42, acc, "mono", 700)
        # The console answers with the handle and stops. The cursor follows it rather
        # than a third line, so the session reads as finished instead of truncated.
        hw = width(HANDLE, "mono", 700, 42)
        M.cursor(c, p, x + hw + 12, 138, 18, 38, acc)
        return

    # vertical rhythm
    if show_tag:
        y_name, y_handle, y_tag = 116, 168, 212
    else:
        y_name, y_handle, y_tag = 126, 184, None

    size, w, _ = fit(name, kind, 700, max_w, h.get("name_size", 58), ls=ls)
    attrs = ""
    if style == "glow":
        gl = c.glow(h.get("glow_std", 7), acc, 0.9 if p["variant"] == "dark" else 0.35)
        attrs = 'filter="%s"' % gl
        name_col = name_col if p["variant"] == "dark" else ink
    if style == "plate":
        # solid block behind the name: ink on accent, the light-mode weight device
        pw = w + 36
        px = x - 18 if anchor == "start" else (x - pw / 2 if anchor == "middle" else x - w - 18)
        c.rect(px, y_name - size * 0.78, pw, size * 1.02, acc, 1.0, 4)
        name_col = p["bg"] if contrast(p["bg"], acc) >= contrast(ink, acc) else ink
    if style == "split":
        off = 3
        c.text(x - off, y_name, name, size, acc, kind, 700, anchor, ls, 0.85)
        c.text(x + off, y_name, name, size, acc2, kind, 700, anchor, ls, 0.85)
    if style == "outline":
        c.text(x, y_name, name, size, "none", kind, 700, anchor, ls, 1.0,
               so(acc, 1, 2))
        # the fill="none" text above draws the stroke; draw the ink copy slightly offset
        c.text(x + 4, y_name + 4, name, size, name_col, kind, 700, anchor, ls)
    elif style == "stencil":
        c.text(x, y_name, name, size, name_col, kind, 700, anchor, ls, 1.0, attrs)
        bx = x - 14 if anchor == "start" else (x - w / 2 - 14 if anchor == "middle" else x - w - 14)
        c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="none" %s/>' % (
            f(bx), f(y_name - size * 0.82), f(w + 28), f(size * 1.08), so(acc, 0.9, 2.5)))
    else:
        c.text(x, y_name, name, size, name_col, kind, 700, anchor, ls, 1.0, attrs)

    c.text(x, y_handle, HANDLE, h.get("handle_size", 42), handle_col, "mono", 700, anchor)
    if show_tag:
        c.text(x, y_tag, TAGLINE, MIN_FONT, tag_col, h.get("tag_font", "mono"), 400, anchor,
               h.get("tag_ls", 0))
    if h.get("cursor"):
        hw = width(HANDLE, "mono", 700, h.get("handle_size", 42))
        cx = x + hw + 10 if anchor == "start" else x + hw / 2 + 10
        M.cursor(c, p, cx, y_handle - 32, 16, 38, acc)


# --------------------------------------------------------------------------- hero

def hero(theme, variant):
    p = palette(theme, variant)
    spec = theme["hero"]
    c = Canvas(HERO_H, "%s, GitHub handle itxcrusher. %s theme." % (NAME, theme["name"]),
               seed="%s:%s:hero" % (theme["slug"], variant))
    box = (0, 0, 900, HERO_H)
    bgspec = _kw(spec.get("bg", {}), variant)
    kind = bgspec.pop("kind", "gradient")
    if kind == "gradient":
        M.gradient_bg(c, p, box, **bgspec)
    elif kind == "flat":
        c.rect(0, 0, 900, HERO_H, bgspec.get("colour", p["bg"]))
    _run_motifs(c, p, box, spec, variant, "back")
    dev = spec.get("device", {}).get(variant) if isinstance(spec.get("device"), dict) else spec.get("device")
    if dev:
        _device(c, p, box, dev)
    _run_motifs(c, p, box, spec, variant, "mid")
    sh = spec.get("shade", True)
    if sh and spec.get("type") != "console":
        M.shade(c, p, box, **(sh if isinstance(sh, dict) else {}))
    type_block(c, p, theme, box)
    _run_motifs(c, p, box, spec, variant, "front")
    _hem(c, p, HERO_H)
    return c.render()


def _device(c, p, box, dev):
    """Weight devices, used mostly by light variants so they read as designed, not bleached."""
    name, kw = (dev, {}) if isinstance(dev, str) else dev
    if name == "rail":
        M.rail(c, p, box, **kw)
    elif name == "band":
        M.band(c, p, box, **kw)
    elif name == "frame":
        M.frame(c, p, box, **kw)
    elif name == "letterbox":
        M.letterbox(c, p, box, **kw)
    elif name == "plate":
        x, y, w, h = box
        c.rect(0, 0, kw.get("w", 560), h, kw.get("colour", p["acc"]), kw.get("op", 1.0))


# -------------------------------------------------------------------------- header

def header(theme, variant, key):
    p = palette(theme, variant)
    label = theme["labels"][key]
    hs = theme.get("header", {})
    style = hs.get("style", "rule")
    c = Canvas(HEAD_H, label, seed="%s:%s:%s" % (theme["slug"], variant, key))
    box = (0, 0, 900, HEAD_H)
    dark = variant == "dark"
    ink, acc, acc2, muted, bg = p["ink"], p["acc"], p["acc2"], p["muted"], p["bg"]
    idx = SECTIONS.index(key) + 1 if key in SECTIONS else 0
    y = 54
    kind = hs.get("font", "mono")
    weight = hs.get("weight", 700)
    ls = hs.get("ls", 0)
    text = label
    if hs.get("case") == "upper":
        text = text.upper()
    if hs.get("index") == "bracket":
        text = "[ %d ]  %s" % (idx, text)
    elif hs.get("index") == "hex":
        text = "0x%d  %s" % (idx, text)
    elif hs.get("index") == "hash":
        text = "#%d  %s" % (idx, text)
    elif hs.get("index") == "roman":
        text = "%s. %s" % ("I" * idx, text)
    elif hs.get("index") == "dot":
        text = "%d. %s" % (idx, text)

    if hs.get("bg", True):
        # a faint ground so the strip reads as a designed element on either page colour
        M.gradient_bg(c, p, box, top=bg, bottom=p["bg2"], horizontal=True)
    if style == "hazard":
        M.hazard(c, p, box, 0, 8, acc, ink if not dark else bg, 45, 10)
        M.hazard(c, p, box, HEAD_H - 8, 8, acc, ink if not dark else bg, 45, 10)
    if style == "band":
        c.rect(0, 0, 900, HEAD_H, acc if dark else p["ink"], 1.0)
        ink = bg if dark else p["bg"]

    size, w, _ = fit(text, kind, weight, 640, 46, ls=ls)
    x = LEFT

    if style == "prompt":
        c.text(x, y, text, size, ink, "mono", 700)
        M.cursor(c, p, x + w + 10, y - 30, 14, 36, acc, 1.0)
        # dotted leader
        c.add('<line x1="%s" y1="%s" x2="%s" y2="%s" %s stroke-dasharray="2 8" stroke-linecap="round"/>' % (
            f(x + w + 40), f(y - 12), f(870), f(y - 12), so(acc2, 0.6, 2)))
    elif style == "bracket":
        c.text(x, y, text, size, ink, kind, weight, ls=ls)
        M.draw_line(c, p, x + w + 24, y - 12, 872, y - 12, acc, 2, 0.9, 0.1, 0.9)
        M.ticks(c, p, box, acc2, 28, 14, 5, 0.55)
        c.add('<rect x="%s" y="%s" width="10" height="10" %s/>' % (f(868), f(y - 17), fo(acc, 1)))
    elif style == "trace":
        c.text(x, y, text, size, ink, kind, weight, ls=ls)
        x0 = x + w + 26
        d = "M%s,%s h60 l24,-14 h%s" % (f(x0), f(y - 12), f(860 - x0 - 84))
        L = 860 - x0 + 10
        name, cls = c.uid("k"), c.uid("a")
        c.keyframes(name, "to{stroke-dashoffset:0}")
        c.anim_class(cls, "stroke-dasharray:%s;stroke-dashoffset:%s;animation:%s 1.2s ease-out .1s forwards" % (f(L), f(L), name))
        gl = c.glow(2, acc, 0.6)
        c.add('<path d="%s" fill="none" %s class="%s" stroke-linejoin="round" filter="%s"/>' % (d, so(acc, 0.9, 2), cls, gl))
        c.add('<circle cx="%s" cy="%s" r="4.5" %s/><circle cx="%s" cy="%s" r="2" %s/>' % (
            f(866), f(y - 26), fo(acc, 1), f(866), f(y - 26), fo(bg, 1)))
    elif style == "chain":
        pw = w + 30
        c.rect(x - 14, y - 38, pw, 52, acc, 0.16 if dark else 0.14, 6)
        c.add('<rect x="%s" y="%s" width="%s" height="52" rx="6" fill="none" %s/>' % (f(x - 14), f(y - 38), f(pw), so(acc, 0.9, 1.8)))
        c.text(x, y, text, size, ink, kind, weight, ls=ls)
        cx = x + pw + 4
        cls = M._opacity_class(c, "0%,100%{opacity:.35}50%{opacity:1}", 3)
        i = 0
        while cx < 860:
            c.add('<rect x="%s" y="%s" width="26" height="14" rx="7" fill="none" %s class="%s" style="animation-delay:-%ss"/>' % (
                f(cx), f(y - 19), so(acc, 0.9, 2), cls, f(i * 0.3)))
            cx += 22
            i += 1
    elif style == "glow":
        gl = c.glow(6, acc, 0.9 if dark else 0.3)
        c.text(x, y, text, size, ink if not dark else lighten(acc, 0.55), kind, weight, ls=ls, extra='filter="%s"' % gl)
        g = c.lin_grad([(0, acc, 0.95), (1, acc2, 0)], 0, 0, 1, 0)
        c.add('<rect x="%s" y="%s" width="%s" height="3" rx="1.5" fill="%s"/>' % (f(x + w + 24), f(y - 14), f(860 - x - w - 24), g))
    elif style == "plate":
        # brass / engraved nameplate
        pw = w + 44
        g = c.lin_grad([(0, lighten(acc, 0.25), 1), (1, darken(acc, 0.25), 1)], 0, 0, 0, 1)
        c.add('<rect x="%s" y="%s" width="%s" height="54" rx="4" fill="%s" %s/>' % (f(x - 20), f(y - 39), f(pw), g, so(darken(acc, 0.5), 0.9, 1.5)))
        for sx in (x - 10, x - 20 + pw - 10):
            c.add('<circle cx="%s" cy="%s" r="3.5" %s/>' % (f(sx), f(y - 12), fo(darken(acc, 0.55), 1)))
        c.text(x + 2, y, text, size, darken(acc, 0.75), kind, weight, ls=ls)
        c.line(x + pw - 6, y - 12, 872, y - 12, acc, 0.8, 2)
    elif style == "hazard" or style == "band":
        c.text(x, y, text, size, ink, kind, weight, ls=ls)
        M.chevrons(c, p, box, y - 12, 4, acc if style == "hazard" else (bg if dark else p["bg"]), 12)
    elif style == "ribbon":
        # a tapered banner strip behind the label
        c.poly([(x - 20, y - 36), (x + w + 34, y - 36), (x + w + 22, y - 12), (x + w + 34, y + 12), (x - 20, y + 12)], acc, 1.0)
        c.text(x, y, text, size, bg if contrast(bg, acc) > contrast(ink, acc) else ink, kind, weight, ls=ls)
        c.line(x + w + 50, y - 12, 872, y - 12, acc, 0.5, 1.5)
    else:  # rule
        c.text(x, y, text, size, ink, kind, weight, ls=ls)
        M.draw_line(c, p, x + w + 22, y - 12, 872, y - 12, acc, 1.6, 1.0, 0.1, 0.75)
        orn = hs.get("ornament")
        if orn:
            _ornament(c, p, orn, 872 - 10, y - 12, acc)
    return c.render()


def _ornament(c, p, kind, cx, cy, col):
    """Small motif-shaped punctuation at the end of a header rule."""
    if kind == "drop":
        c.path("M%s,%s c-6,10 -8,14 -8,18 a8,8 0 0 0 16,0 c0,-4 -2,-8 -8,-18 Z" % (f(cx), f(cy - 12)), col, 0.95)
    elif kind == "flake":
        for a in range(0, 180, 60):
            x0, y0 = M.polar(cx, cy, 10, a)
            x1, y1 = M.polar(cx, cy, 10, a + 180)
            c.line(x0, y0, x1, y1, col, 0.95, 2)
    elif kind == "leaf":
        c.path("M%s,%s c14,-2 22,8 20,20 c-12,2 -22,-6 -20,-20 Z" % (f(cx - 10), f(cy - 10)), col, 0.95)
    elif kind == "sun":
        c.circle(cx, cy, 6, col)
        for a in range(0, 360, 45):
            x0, y0 = M.polar(cx, cy, 9, a)
            x1, y1 = M.polar(cx, cy, 13, a)
            c.line(x0, y0, x1, y1, col, 0.95, 2)
    elif kind == "star":
        c.poly([M.polar(cx, cy, 9 if i % 2 == 0 else 4, -90 + i * 36) for i in range(10)], col, 0.95)
    elif kind == "dot":
        c.circle(cx, cy, 5, col)
    elif kind == "diamond":
        c.poly([(cx, cy - 8), (cx + 8, cy), (cx, cy + 8), (cx - 8, cy)], col, 0.95)
    elif kind == "bolt":
        c.poly([(cx + 2, cy - 12), (cx - 6, cy + 2), (cx, cy + 2), (cx - 2, cy + 12), (cx + 6, cy - 2), (cx, cy - 2)], col, 0.95)
    elif kind == "gear":
        M.gears(c, p, (cx - 12, cy - 12, 24, 24), col, [(cx, cy, 11, 8, 12)])
    elif kind == "wave":
        c.path(M.wave_path(cx - 14, cx + 14, cy, 4, 14, samples=16), "none", 1, col, 0.95, 2)
    elif kind == "block":
        c.add('<rect x="%s" y="%s" width="14" height="14" rx="2" fill="none" %s/>' % (f(cx - 7), f(cy - 7), so(col, 0.95, 2)))
    elif kind == "node":
        c.circle(cx, cy, 5, col)
        c.add('<circle cx="%s" cy="%s" r="10" fill="none" %s/>' % (f(cx), f(cy), so(col, 0.7, 1.5)))
    elif kind == "flame":
        c.path("M%s,%s c-8,10 -8,16 -3,22 c2,-4 4,-4 6,-8 c4,4 6,8 2,12 c8,-4 10,-12 4,-20 c-2,4 -4,4 -4,2 c1,-4 0,-6 -5,-8 Z" % (f(cx), f(cy - 12)), col, 0.95)
    elif kind == "mountain":
        c.poly([(cx - 14, cy + 8), (cx - 4, cy - 8), (cx + 2, cy), (cx + 8, cy - 6), (cx + 16, cy + 8)], col, 0.95)
    elif kind == "cloud":
        c.path("M%s,%s a7,7 0 0 1 12,-6 a8,8 0 0 1 15,4 a6,6 0 0 1 -1,12 h-24 a5,5 0 0 1 -2,-10 Z" % (f(cx - 14), f(cy + 2)), col, 0.95)
    elif kind == "moon":
        M.moon(c, p, (cx - 12, cy - 12, 24, 24), cx, cy, 9, col, 0, True)


def _hem(c, p, h, depth=44):
    """Fade the last few units to the page ground.

    The motif pieces are separate images stacked against the drawn page, and the drawn
    page is a flat p["bg"]. Without this the hero's warm glow stopped dead at its own
    bottom edge and the join read as a band across the page.
    """
    g = c.lin_grad([(0, p["bg"], 0), (1, p["bg"], 1)], x1=0, y1=0, x2=0, y2=1)
    c.add('<rect x="0" y="%s" width="900" height="%s" fill="%s"/>'
          % (f(h - depth), f(depth), g))


# -------------------------------------------------------------------------- sign-off

def signoff(theme, variant):
    p = palette(theme, variant)
    text = theme["signoff"]
    hs = theme.get("header", {})
    c = Canvas(SIGN_H, text, seed="%s:%s:signoff" % (theme["slug"], variant))
    box = (0, 0, 900, SIGN_H)
    # Vertical, not horizontal. This band sits directly on top of the drawn contact
    # slice, which is a flat p["bg"]. A left-to-right gradient leaves the bottom edge at
    # bg2 on one side and bg on the other, and the join showed as a step across the page.
    # Ending the gradient at bg means the two images meet on the same colour.
    M.gradient_bg(c, p, box, top=p["bg2"], bottom=p["bg"])
    kind = hs.get("font", "mono")
    size, w, _ = fit(text, kind, 700, 500, 42)
    c.text(450, 42, text, size, p["muted"], kind, 700, "middle")
    c.line(40, 32, 450 - w / 2 - 24, 32, p["acc"], 0.6, 1.5)
    c.line(450 + w / 2 + 24, 32, 860, 32, p["acc"], 0.6, 1.5)
    if hs.get("ornament"):
        _ornament(c, p, hs["ornament"], 450 + w / 2 + 24 + 10, 32, p["acc"])
        _ornament(c, p, hs["ornament"], 450 - w / 2 - 24 - 10, 32, p["acc"])
    return c.render()


def build_theme(theme):
    """The two motif pieces, {filename: svg}.

    The section headings used to be built here too. The drawn page sets its own section
    bands now, in the same type and rhythm as the rest of the composition, so a separate
    heading image would only be a second style competing with it.

    The hero and the sign-off stayed, because flattening them into the page cost them
    their motifs: the embers, the glow, the ornament beside the rule. Those two are the
    page's only real ornament and they were worse for being redrawn plainly."""
    out = {}
    for v in ("dark", "light"):
        out["hero-%s.svg" % v] = hero(theme, v)
        out["signoff-%s.svg" % v] = signoff(theme, v)
    return out


def contrast_report(theme):
    """Objective check that both variants have weight: ink on bg, accent on bg."""
    rows = []
    for v in ("dark", "light"):
        p = palette(theme, v)
        rows.append((v, round(contrast(p["ink"], p["bg"]), 1), round(contrast(p["acc"], p["bg"]), 1),
                     round(contrast(p["muted"], p["bg"]), 1)))
    return rows
