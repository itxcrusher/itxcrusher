"""The whole page as themed artwork: a few long SVGs instead of a markdown document.

Why this shape. GitHub's sanitizer strips `style` and `class`, so an SVG is the only
surface on a README that can hold a colour. Probed against GitHub's own markdown
endpoint: inline `<svg>`, `<object>`, `<embed>`, `<td bgcolor>`, `<font color>` and
`<map>`/`<area>` are all removed. `usemap` survives on the img but its map does not, so
clickable REGIONS inside one image are impossible. A whole image can be a link; a part
of one cannot.

That decides the architecture:

  * the page body is drawn as long SVGs rather than assembled from many small pieces, so
    the composition is continuous and the theme is unbroken;
  * every destination is collected into a themed link strip underneath, because a link
    cannot live inside the artwork;
  * the same words follow as collapsed markdown, so nothing on the page exists only as
    pixels. R3 enforces that.

Sizing follows what textpanel established: one image per viewport band. The README
column was measured on the live profile from 846px down to 238px, a 3.5x range that no
single canvas survives, so each band carries its own canvas width, type scale and line
breaks.

Drawing happens in two passes. Canvas needs its height up front and a card's background
has to sit behind text that was measured before the card's height was known, so blocks
queue closures into `bg` and `fg` lists rather than drawing immediately. When the flow
is finished the height is known, the Canvas is made, and the two lists run in order.
"""
from themes import motifs as M
from themes.svg import Canvas, contrast, f, mix, so, width
from themes.textpanel import BAND_BY_KEY

# Type scale as multiples of the band's base size. Deliberately a short fixed set: the
# rendering contract verifies that every font-size in a generated page belongs to it,
# which is what stops a stray hand-tuned size from shipping at 6px on a phone.
SCALE = {"micro": 0.85, "body": 1.0, "lead": 1.2, "sub": 1.45, "head": 1.75, "hero": 2.3}

PAD = {"xs": 18, "sm": 26, "md": 32, "lg": 44}


def _break_mono(line, size, maxw):
    """Wrap a shell command to the available width, breaking inside a long token.

    A clone URL is one token with no spaces, and on the narrow band it is wider than the
    whole column. Shrinking the type to make it fit is what the size floor exists to
    prevent, so it wraps instead."""
    out, cur = [], ""
    for ch in line:
        if width(cur + ch, "mono", 400, size) > maxw and cur:
            out.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out or [""]


# Field motifs that read as atmosphere at low opacity anywhere on a tall canvas.
# Anything anchored to a horizon or an edge (mountains, dunes, waves, letterbox) is
# excluded on purpose: mid-page it stops being weather and starts being furniture.
AMBIENT_SAFE = {"stars", "speckle", "rain", "snow", "dust", "embers", "bubbles",
                "petals", "fireflies", "scanlines", "hexgrid", "halftone", "crystals"}
AMBIENT_FALLBACK = {"tech": ("hexgrid", {"op": 0.5}), "nature": ("speckle", {"n": 90}),
                    "elemental": ("dust", {"n": 40}), "gritty": ("speckle", {"n": 60})}


def ambient_spec(theme):
    """What falls, drifts or glows behind this theme's page body.

    Prefers whatever field motif the hero already uses, so the page continues the same
    weather rather than inventing a second kind; falls back per family."""
    for stage in ("mid", "back"):
        for item in theme["hero"].get(stage, []) or []:
            name = item if isinstance(item, str) else item[0]
            if name in AMBIENT_SAFE:
                kw = {} if isinstance(item, str) else dict(item[1])
                for k in ("region", "skip", "dark", "light"):
                    kw.pop(k, None)
                return name, kw
    return AMBIENT_FALLBACK[theme["family"]]


def family_geom(family, base):
    """How a family shapes a box. The pills already differ by family; until now every
    card and callout was the same rounded rectangle with the same rail, so 47 looks
    shared one silhouette. radius, rail width, and whether tech corner ticks are drawn.
    """
    if family == "gritty":
        return 0, max(4, base / 4.0), False
    if family == "nature":
        return base * 0.55, max(3, base / 7.0), False
    if family == "tech":
        return base * 0.1, max(3, base / 7.0), True
    return base * 0.24, max(3, base / 6.0), False


def sizes_for(base):
    return {k: max(1, int(round(base * v))) for k, v in SCALE.items()}


def allowed_sizes(base):
    return set(sizes_for(base).values())


class Flow:
    def __init__(self, theme, variant, band):
        from themes.render import palette
        self.t = theme
        # Through render.palette, not theme[variant] raw: it stamps the variant into the
        # dict (motifs test _dark(p) with it) and fills the muted/acc2 defaults.
        self.p = palette(theme, variant)
        self.variant = variant
        self.band = band
        self.key, _media, self.w, self.base = BAND_BY_KEY[band]
        self.s = sizes_for(self.base)
        self.pad = PAD[band]
        self.x = self.pad
        self.inner = self.w - self.pad * 2
        self.y = 0.0
        self.bg = []
        self.fg = []
        self.font = theme["header"].get("font", "sans")

    # -- primitives ---------------------------------------------------------------

    def space(self, n):
        self.y += n

    def _fit(self, s, weight, size, maxw, floor):
        """Step DOWN THROUGH THE SCALE, never between its rungs.

        The contract verifies that every font-size in a page belongs to the scale set,
        which is what stops a hand-tuned size from shipping at 6px on a phone. Shrinking
        by one unit at a time would break that, so a title that will not fit takes the
        next rung down instead."""
        rungs = sorted(set(self.s.values()), reverse=True)
        for r in rungs:
            if r > size or r < floor:
                continue
            if width(s, self.font, weight, r) <= maxw:
                return r
        return max(floor, min(rungs))

    def text(self, s, size, colour, weight=400, anchor="start", op=1.0, x=None):
        y = self.y + size
        xx = self.x if x is None else x
        self.fg.append(lambda c: c.text(xx, y, s, size, colour, self.font, weight, anchor, op=op))
        self.y = y + size * 0.32
        return y

    def run(self, segments, size):
        """One line built from (text, colour, weight, kind) segments, measured end to
        end. This is how a line gets two colours: SVG has no spans, only positions."""
        y = self.y + size
        x = self.x
        for txt, colour, weight, kind in segments:
            k = kind or self.font
            self.fg.append(lambda c, txt=txt, x=x, y=y, colour=colour, weight=weight, k=k:
                           c.text(x, y, txt, size, colour, k, weight))
            x += width(txt, k, weight, size)
        self.y = y + size * 0.32

    def wrap(self, body, size, colour, weight=400, lead=1.45):
        lines, line = [], ""
        for wd in body.split():
            trial = (line + " " + wd).strip()
            if line and width(trial, self.font, weight, size) > self.inner:
                lines.append(line)
                line = wd
            else:
                line = trial
        if line:
            lines.append(line)
        step = size * lead
        for ln in lines:
            y = self.y + size
            self.fg.append(lambda c, ln=ln, y=y: c.text(self.x, y, ln, size, colour,
                                                        self.font, weight))
            self.y = y + (step - size)
        return len(lines)

    def paras(self, items, size, colour, weight=400):
        for i, para in enumerate(items):
            if i:
                self.space(size * 0.75)
            self.wrap(para, size, colour, weight)

    def box(self, top, bot, tint, rail=True):
        rx, rail_w, ticks = family_geom(self.t["family"], self.base)
        ground = mix(self.p["bg"], self.p["bg2"], tint)
        self.bg.append(lambda c: c.rect(self.x, top, self.inner, bot - top, ground, 1, rx))
        self.bg.append(lambda c: c.add(
            '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" %s/>'
            % (f(self.x + 0.75), f(top + 0.75), f(self.inner - 1.5), f(bot - top - 1.5),
               f(max(0, rx - 0.75)), so(self.p["acc"], 0.45, 1.4))))
        if rail:
            self.bg.append(lambda c: c.rect(self.x, top, rail_w, bot - top, self.p["acc"], 0.9))
        if ticks:
            t_len = self.base * 1.1
            t_w = max(2, self.base / 10.0)
            x2, y2 = self.x + self.inner, bot
            self.bg.append(lambda c: (
                c.line(x2 - t_len, top, x2, top, self.p["acc"], 0.9, t_w),
                c.line(x2, top, x2, top + t_len, self.p["acc"], 0.9, t_w),
                c.line(self.x, y2 - t_len, self.x, y2, self.p["acc"], 0.9, t_w),
                c.line(self.x, y2, self.x + t_len, y2, self.p["acc"], 0.9, t_w)))

    # -- blocks -------------------------------------------------------------------

    def hero(self, name, handle):
        self.space(self.pad * 1.2)
        size = self._fit(name, 700, self.s["hero"], self.inner, self.s["sub"])
        self.text(name, size, self.p["ink"], 700)
        self.space(self.base * 0.1)
        self.text(handle, self.s["head"], self.p["acc"], 700)
        self.space(self.base * 0.35)
        y = self.y
        self.bg.append(lambda c: c.line(self.x, y, self.x + self.inner * 0.42, y,
                                        self.p["acc"], 0.8, max(2, self.base / 9.0)))
        self.space(self.base * 1.1)

    def section(self, label):
        """A section heading in the theme's own register.

        The catalog has always carried header.style and header.case; the retired heading
        images honoured them and the first drawn page did not, which is a big part of why
        47 looks felt like one design wearing different colours. prompt themes get a
        shell prompt and a blinking cursor, bracket themes get HUD brackets, hazard
        themes get a striped rule, plate themes set the label on a filled block, glow
        themes glow (dark only; on light, density does the work, per R14's philosophy)."""
        style = self.t["header"].get("style", "rule")
        if self.t["header"].get("case") == "upper":
            label = label.upper()
        prefix = "> " if style == "prompt" else ("[ " if style == "bracket" else "")
        suffix = " ]" if style == "bracket" else ""
        shown = prefix + label + suffix
        ls = self.base * 0.09 if self.t["header"].get("case") == "upper" else 0
        self.space(self.base * 1.6)
        size = self._fit(shown, 700, self.s["head"], self.inner * 0.72, self.s["lead"])
        base_y = self.y
        y = base_y + size
        tw = width(shown, self.font, 700, size) + ls * max(0, len(shown) - 1)
        ry = base_y + size * 0.66

        use_glow = style == "glow" and self.variant == "dark"
        def draw_label(c):
            extra = 'letter-spacing="%s"' % f(ls) if ls else ""
            if use_glow:
                extra = (extra + " " if extra else "") + 'filter="%s"' % c.glow(
                    self.base / 5.0, self.p["acc"], 0.8)
            c.text(self.x, y, shown, size, self.p["acc"], self.font, 700, extra=extra)
        self.fg.append(draw_label)
        self.y = y + size * 0.32

        if style == "plate" or style == "band" or style == "ribbon":
            ground = mix(self.p["bg"], self.p["bg2"], 0.85)
            self.bg.append(lambda c: c.rect(self.x - self.base * 0.4, base_y - self.base * 0.25,
                                            tw + self.base * 1.1, size * 1.55, ground, 1,
                                            0 if self.t["family"] == "gritty" else self.base * 0.14))

        orn = self.t["header"].get("ornament")
        gx = self.x + tw + self.base * 0.7
        end = self.x + self.inner - (self.base * 1.1 if orn else 0)
        if style == "hazard":
            hb = max(4, self.base / 3.0)
            self.bg.append(lambda c: M.hazard(c, self.p, (gx, 0, end - gx, 0),
                                              ry - hb / 2, hb, stripe=self.base * 0.55))
        elif style == "trace":
            mid = gx + (end - gx) * 0.6
            self.bg.append(lambda c: (
                c.line(gx, ry, mid, ry, self.p["acc"], 0.6, max(1.5, self.base / 13.0)),
                c.add('<circle cx="%s" cy="%s" r="%s" fill="%s">'
                      '<animate attributeName="opacity" values=".4;1;.4" dur="3s" '
                      'repeatCount="indefinite"/></circle>'
                      % (f(mid), f(ry), f(max(3, self.base / 5.5)), self.p["acc"])),
                c.line(mid, ry, end, ry, self.p["acc"], 0.35, max(1.5, self.base / 13.0))))
        elif style == "chain":
            step = self.base * 1.05
            def links(c, gx=gx, end=end, ry=ry):
                x = gx
                while x + step * 0.7 <= end:
                    c.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" %s/>'
                          % (f(x), f(ry - self.base * 0.16), f(step * 0.62),
                             f(self.base * 0.32), f(self.base * 0.1),
                             so(self.p["acc"], 0.55, max(1.2, self.base / 16.0))))
                    x += step
            self.bg.append(links)
        else:
            self.bg.append(lambda c: c.line(gx, ry, end, ry,
                                            self.p["acc"], 0.5, max(1.5, self.base / 13.0)))
        if style == "prompt":
            cx = self.x + tw + self.base * 0.35
            self.bg.append(lambda c: M.cursor(c, self.p, cx, base_y + size * 0.12,
                                              max(4, size * 0.14), size * 0.9, self.p["acc"]))
        if orn:
            from themes.render import _ornament
            ox = self.x + self.inner - self.base * 0.5
            k = self.base / 44.0
            self.bg.append(lambda c: (
                c.add('<g transform="translate(%s,%s) scale(%s)">' % (f(ox), f(ry), f(k))),
                _ornament(c, self.p, orn, 0, 0, self.p["acc"]),
                c.add("</g>")))
        self.space(self.base * 0.5)

    def note(self, title, body, lines, after):
        """The trust block: a callout the theme owns, instead of GitHub's fixed colour."""
        top = self.y
        pad = self.base * 0.85
        self.y += pad
        sx, si = self.x, self.inner
        self.x += pad
        self.inner -= pad * 2
        self.text(title, self.s["lead"], self.p["acc"], 700)
        self.space(self.base * 0.15)
        self.wrap(body, self.s["micro"], self.p["ink"])
        self.space(self.base * 0.4)
        ctop = self.y
        cpad = self.base * 0.5
        self.y += cpad
        mono = self.s["micro"]
        avail = self.inner - cpad * 2
        last_end = None
        for ln in lines:
            for piece in _break_mono(ln, mono, avail):
                y = self.y + mono
                self.fg.append(lambda c, piece=piece, y=y:
                               c.text(self.x + cpad, y, piece, mono, self.p["ink"], "mono", 400))
                last_end = (self.x + cpad + width(piece, "mono", 400, mono), y)
                self.y = y + mono * 0.55
        if last_end and self.font == "mono":
            # The command box belongs to a terminal-voiced theme, so it gets the one
            # blinking cursor on the page: a single live point, not scattered effects.
            cx2, cy2 = last_end
            self.fg.append(lambda c: M.cursor(c, self.p, cx2 + mono * 0.4,
                                              cy2 - mono * 0.8, max(3, mono * 0.5),
                                              mono, self.p["acc"]))
        self.y += cpad
        cbot = self.y
        cground = mix(self.p["bg"], "#000000", 0.35) if self.variant == "dark" \
            else mix(self.p["bg"], "#ffffff", 0.55)
        self.bg.append(lambda c: c.rect(self.x, ctop, self.inner, cbot - ctop, cground, 1,
                                        self.base * 0.15))
        self.space(self.base * 0.4)
        self.wrap(after, self.s["micro"], self.p["muted"])
        self.x, self.inner = sx, si
        self.y += pad
        self.box(top, self.y, 0.7)
        self.space(self.base * 0.5)

    def pill(self, label, x, y, filled):
        s = self.s["micro"]
        padx = self.base * 0.48
        w = width(label, self.font, 700 if filled else 500, s) + padx * 2
        h = s * 2.0
        fam = self.t["family"]
        rx = h / 2.0 if fam == "nature" else (0 if fam == "gritty" else self.base * 0.13)
        if filled:
            ink = self.p["bg"] if contrast(self.p["bg"], self.p["acc"]) >= 4.5 else self.p["ink"]
            self.bg.append(lambda c: c.rect(x, y, w, h, self.p["acc"], 1, rx))
            self.fg.append(lambda c: c.text(x + padx, y + h / 2.0 + s * 0.36, label, s,
                                            ink, self.font, 700))
        else:
            g = mix(self.p["bg"], self.p["bg2"], 0.8)
            self.bg.append(lambda c: c.rect(x, y, w, h, g, 1, rx))
            self.bg.append(lambda c: c.add(
                '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" %s/>'
                % (f(x + 0.75), f(y + 0.75), f(w - 1.5), f(h - 1.5), f(max(0, rx - 0.75)),
                   so(self.p["acc"], 0.5, 1.2))))
            self.fg.append(lambda c: c.text(x + padx, y + h / 2.0 + s * 0.36, label, s,
                                            self.p["ink"], self.font, 500))
        return w, h

    def pill_rows(self, groups):
        s = self.s["micro"]
        h = s * 2.0
        gap = self.base * 0.3
        for label, values in groups:
            x = self.x
            w, _ = self.pill(label, x, self.y, True)
            x += w + gap
            for v in values:
                vw = width(v, self.font, 500, s) + self.base * 0.48 * 2
                if x + vw > self.x + self.inner:
                    self.y += h + gap
                    x = self.x
                w2, _ = self.pill(v, x, self.y, False)
                x += w2 + gap
            self.y += h + gap * 1.4

    def card(self, name, desc, meta, index=0):
        """One repository. The name line leads with the theme's row register, another
        piece of catalogued personality (text.rows) that died in the rewrite: numbered
        themes count their work like operations, ls themes prefix mode bits, tasks
        themes tick a box, quotes themes speak in blockquotes (their rail is the quote
        bar, so they carry no marker)."""
        rows = self.t["text"].get("rows", "list")
        top = self.y
        pad = self.base * 0.7
        self.y += pad
        sx, si = self.x, self.inner
        self.x += pad
        self.inner -= pad * 2
        mark = ""
        if rows == "numbered":
            mark = "%02d " % index
        elif rows == "ls":
            mark = "drwxr-xr-x "
        elif rows == "tasks":
            mark = "[x] "
        if mark:
            msize = self.s["micro"]
            y = self.y + self.s["lead"]
            self.fg.append(lambda c, mark=mark, y=y: c.text(
                self.x, y - (self.s["lead"] - msize) * 0.35, mark.rstrip() + " ",
                msize, self.p["muted"], "mono", 500))
            moff = width(mark, "mono", 500, msize)
            self.fg.append(lambda c, name=name, y=y, moff=moff: c.text(
                self.x + moff, y, name, self.s["lead"], self.p["acc"], self.font, 700))
            self.y = y + self.s["lead"] * 0.32
        else:
            self.text(name, self.s["lead"], self.p["acc"], 700)
        self.space(self.base * 0.08)
        self.wrap(desc, self.s["micro"], self.p["ink"])
        self.space(self.base * 0.12)
        self.text(meta, self.s["micro"], self.p["muted"], 500)
        self.x, self.inner = sx, si
        self.y += pad
        self.box(top, self.y, 0.42)
        self.space(self.base * 0.42)

    def render(self, title, desc=None):
        h = int(round(self.y + self.pad))
        c = Canvas(h, title, seed="%s:%s:%s:page" % (self.t["slug"], self.variant, self.key),
                   w=self.w, min_font=min(self.s.values()), desc=desc)
        # Flat, not a gradient. The page is three separate images stacked with no gap, and
        # a gradient restarts inside each one, so the joins showed as lighter horizontal
        # bands across the page. A single ground makes the seams disappear; the depth comes
        # from the panels and cards drawn on top of it.
        c.add('<rect x="0" y="0" width="%s" height="%s" fill="%s"/>' % (f(self.w), f(h), self.p["bg"]))
        # The theme's weather continues behind the page at low opacity: the same rain,
        # stars or embers the hero opens with, quiet enough that the prose stays the
        # loudest thing. This is what stops the body reading as a flat grey document
        # pinned under a decorated banner. Edges stay exactly bg (the layer is faded,
        # never the ground), so the seam-free stacking is untouched.
        name, kw = ambient_spec(self.t)
        gid = "amb"
        c.add('<g opacity="%s">' % f(0.14 if self.variant == "dark" else 0.09))
        try:
            getattr(M, name)(c, self.p, (0, 0, self.w, h), **kw)
        except TypeError:
            getattr(M, name)(c, self.p, (0, 0, self.w, h))
        c.add("</g>")
        for op in self.bg:
            op(c)
        for op in self.fg:
            op(c)
        return c.render()
