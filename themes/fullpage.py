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


def sizes_for(base):
    return {k: max(1, int(round(base * v))) for k, v in SCALE.items()}


def allowed_sizes(base):
    return set(sizes_for(base).values())


class Flow:
    def __init__(self, theme, variant, band):
        self.t = theme
        self.p = theme[variant]
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

    def box(self, top, bot, tint, rail=True, radius=None):
        rx = self.base * 0.2 if radius is None else radius
        ground = mix(self.p["bg"], self.p["bg2"], tint)
        self.bg.append(lambda c: c.rect(self.x, top, self.inner, bot - top, ground, 1, rx))
        self.bg.append(lambda c: c.add(
            '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" %s/>'
            % (f(self.x + 0.75), f(top + 0.75), f(self.inner - 1.5), f(bot - top - 1.5),
               f(max(0, rx - 0.75)), so(self.p["acc"], 0.45, 1.4))))
        if rail:
            self.bg.append(lambda c: c.rect(self.x, top, max(3, self.base / 7.0),
                                            bot - top, self.p["acc"], 0.9))

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
        self.space(self.base * 1.6)
        size = self._fit(label, 700, self.s["head"], self.inner * 0.7, self.s["lead"])
        base_y = self.y
        self.text(label, size, self.p["acc"], 700)
        tw = width(label, self.font, 700, size)
        ry = base_y + size * 0.66
        gx = self.x + tw + self.base * 0.7
        self.bg.append(lambda c: c.line(gx, ry, self.x + self.inner, ry,
                                        self.p["acc"], 0.5, max(1.5, self.base / 13.0)))
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
        for ln in lines:
            for piece in _break_mono(ln, mono, avail):
                y = self.y + mono
                self.fg.append(lambda c, piece=piece, y=y:
                               c.text(self.x + cpad, y, piece, mono, self.p["ink"], "mono", 400))
                self.y = y + mono * 0.55
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

    def card(self, name, desc, meta):
        top = self.y
        pad = self.base * 0.7
        self.y += pad
        sx, si = self.x, self.inner
        self.x += pad
        self.inner -= pad * 2
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
        for op in self.bg:
            op(c)
        for op in self.fg:
            op(c)
        return c.render()
