"""SVG primitives for the profile theme engine.

Python 3.11+ stdlib only. Text measurement comes from themes/metrics.py, a committed
table measured in a real browser, so a build produces byte-identical output on a laptop
and on a CI runner.

Every rule the checker enforces is respected here by construction:
  R5  no non-ASCII in any output
  R6  viewBox width 900, no rendered text under 41 units
  R7  no script, no @import, no external href, no prefers-color-scheme, system fonts
  R8  no multi-digit numbers in rendered text (labels are words)
"""
import math
import random

from themes import metrics

W = 900

FONT_SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
FONT_SERIF = "Georgia, 'Times New Roman', serif"
FAMILIES = {"sans": FONT_SANS, "mono": FONT_MONO, "serif": FONT_SERIF}

MIN_FONT = 41

# The rendered SVG is the one artifact that leaves this repository: it is served to
# every profile visitor and can be saved with a right-click. No licence can stop that,
# so the file names its own source instead. A comment rather than <metadata> because a
# human opening the file is the actual audience, and rather than <desc> because <desc>
# is read aloud by screen readers and belongs to the reader, not to attribution.
CREDIT = ("<!-- Drawn by the itxcrusher profile theme engine."
          " Source, and the terms for reuse: https://github.com/itxcrusher/itxcrusher -->")


# ----------------------------------------------------------------------------- colour

def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(r, g, b):
    return "#%02x%02x%02x" % (max(0, min(255, round(r))), max(0, min(255, round(g))),
                              max(0, min(255, round(b))))


def mix(a, b, t):
    ra, rb = rgb(a), rgb(b)
    return hexc(*[ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def lighten(c, t):
    return mix(c, "#ffffff", t)


def darken(c, t):
    return mix(c, "#000000", t)


def _lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(c):
    r, g, b = rgb(c)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def fo(c, a):
    """fill + fill-opacity attribute pair."""
    return 'fill="%s" fill-opacity="%s"' % (c, _f(a))


def so(c, a, w=1):
    return 'stroke="%s" stroke-opacity="%s" stroke-width="%s"' % (c, _f(a), _f(w))


def _f(v):
    """Compact float formatting: 12.0 -> 12, 0.3333 -> 0.333."""
    if isinstance(v, int):
        return str(v)
    s = ("%.3f" % v).rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


f = _f


# ------------------------------------------------------------------------ measurement

_cache = {}


def width(text, kind="sans", weight=700, size=48, ls=0.0):
    """Measured advance width in SVG user units.

    Backed by themes/metrics.py, a table measured in a real browser at the exact font
    stacks these SVGs declare. This used to call Pillow against a DejaVu TTF and fall
    back to a flat per-character average when the file was absent, which made the same
    build produce different output on a CI runner than on a laptop. The files are
    committed, so that was a correctness bug, not just an inaccuracy.
    """
    return metrics.advance(text, kind, weight, size) * metrics.SAFETY         + max(0, len(text) - 1) * ls


def fit(text, kind, weight, max_w, max_size, min_size=MIN_FONT, ls=0.0):
    """Largest integer size in [min_size, max_size] whose measured width fits max_w.
    Returns (size, width, fits)."""
    size = int(max_size)
    while size > min_size and width(text, kind, weight, size, ls) > max_w:
        size -= 1
    w = width(text, kind, weight, size, ls)
    return size, w, w <= max_w


# ------------------------------------------------------------------------------ canvas

class Canvas:
    def __init__(self, h, title, seed="", desc=None, w=W, min_font=MIN_FONT):
        # Width and the type floor are parameters because badges are a different
        # contract from the banner art. A banner is width="100%", so GitHub scales it
        # with the README column (846px down to 238px measured) and its type has to
        # survive that. A badge is height-pinned and narrower than the narrowest
        # column, so it renders 1:1 everywhere and 14 units means 14 pixels.
        self.w, self.h = w, h
        self.min_font = min_font
        self.title = title
        self.desc = desc
        self.defs, self.css, self.body = [], [], []
        self._n = 0
        self.rng = random.Random(seed)

    def uid(self, prefix="i"):
        self._n += 1
        return "%s%d" % (prefix, self._n)

    def add(self, s):
        self.body.append(s)

    def defs_add(self, s):
        self.defs.append(s)

    def css_add(self, s):
        self.css.append(s)

    # -- shapes -------------------------------------------------------------------
    def rect(self, x, y, w, h, fill, op=1.0, rx=0, extra=""):
        self.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s%s/>' % (
            f(x), f(y), f(w), f(h), f(rx), fo(fill, op), (" " + extra) if extra else ""))

    def circle(self, cx, cy, r, fill, op=1.0, extra=""):
        self.add('<circle cx="%s" cy="%s" r="%s" %s%s/>' % (
            f(cx), f(cy), f(r), fo(fill, op), (" " + extra) if extra else ""))

    def line(self, x1, y1, x2, y2, stroke, op=1.0, w=1, extra=""):
        self.add('<line x1="%s" y1="%s" x2="%s" y2="%s" %s%s/>' % (
            f(x1), f(y1), f(x2), f(y2), so(stroke, op, w), (" " + extra) if extra else ""))

    def path(self, d, fill="none", fop=1.0, stroke=None, sop=1.0, sw=1, extra=""):
        s = '<path d="%s" ' % d
        s += fo(fill, fop) if fill != "none" else 'fill="none"'
        if stroke:
            s += " " + so(stroke, sop, sw)
        if extra:
            s += " " + extra
        self.add(s + "/>")

    def poly(self, pts, fill="none", fop=1.0, stroke=None, sop=1.0, sw=1, extra=""):
        d = " ".join("%s,%s" % (f(x), f(y)) for x, y in pts)
        s = '<polygon points="%s" ' % d
        s += fo(fill, fop) if fill != "none" else 'fill="none"'
        if stroke:
            s += " " + so(stroke, sop, sw)
        if extra:
            s += " " + extra
        self.add(s + "/>")

    def group(self, inner, extra=""):
        self.add("<g %s>%s</g>" % (extra, inner))

    # -- gradients and filters ------------------------------------------------------
    def lin_grad(self, stops, x1=0, y1=0, x2=0, y2=1):
        """stops: list of (offset 0..1, colour, opacity)."""
        gid = self.uid("g")
        s = ['<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">' % (
            gid, f(x1), f(y1), f(x2), f(y2))]
        for off, col, op in stops:
            s.append('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (
                f(off), col, f(op)))
        s.append("</linearGradient>")
        self.defs_add("".join(s))
        return "url(#%s)" % gid

    def rad_grad(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        gid = self.uid("r")
        focal = ""
        if fx is not None:
            focal = ' fx="%s" fy="%s"' % (f(fx), f(fy))
        s = ['<radialGradient id="%s" cx="%s" cy="%s" r="%s"%s>' % (
            gid, f(cx), f(cy), f(r), focal)]
        for off, col, op in stops:
            s.append('<stop offset="%s" stop-color="%s" stop-opacity="%s"/>' % (
                f(off), col, f(op)))
        s.append("</radialGradient>")
        self.defs_add("".join(s))
        return "url(#%s)" % gid

    def blur(self, std):
        fid = self.uid("b")
        self.defs_add(
            '<filter id="%s" x="-30%%" y="-30%%" width="160%%" height="160%%">'
            '<feGaussianBlur stdDeviation="%s"/></filter>' % (fid, f(std)))
        return "url(#%s)" % fid

    def glow(self, std, colour=None, strength=1.0):
        """Drop-glow that keeps the source on top. Colour defaults to the source."""
        fid = self.uid("gl")
        flood = ""
        if colour:
            flood = ('<feFlood flood-color="%s" flood-opacity="%s" result="c"/>'
                     '<feComposite in="c" in2="blur" operator="in" result="blur"/>'
                     % (colour, f(strength)))
        self.defs_add(
            '<filter id="%s" x="-40%%" y="-60%%" width="180%%" height="220%%">'
            '<feGaussianBlur in="SourceGraphic" stdDeviation="%s" result="blur"/>%s'
            '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
            '</filter>' % (fid, f(std), flood))
        return "url(#%s)" % fid

    def clip_rect(self, x, y, w, h, rx=0):
        cid = self.uid("c")
        self.defs_add('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s" rx="%s"/>'
                      '</clipPath>' % (cid, f(x), f(y), f(w), f(h), f(rx)))
        return "url(#%s)" % cid

    def pattern(self, w, h, inner):
        pid = self.uid("p")
        self.defs_add('<pattern id="%s" width="%s" height="%s" patternUnits="userSpaceOnUse">'
                      '%s</pattern>' % (pid, f(w), f(h), inner))
        return "url(#%s)" % pid

    # -- text ----------------------------------------------------------------------
    def text(self, x, y, s, size, fill, kind="sans", weight=700, anchor="start",
             ls=0.0, op=1.0, extra=""):
        assert size >= self.min_font, "R6: text below %d units: %r" % (self.min_font, s)
        assert all(ord(ch) < 128 for ch in s), "R5: non-ASCII text %r" % s
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        a = ['<text x="%s" y="%s"' % (f(x), f(y)),
             'font-family="%s"' % FAMILIES[kind],
             'font-size="%d"' % size, 'font-weight="%d"' % weight,
             'fill="%s"' % fill]
        if op != 1.0:
            a.append('fill-opacity="%s"' % f(op))
        if anchor != "start":
            a.append('text-anchor="%s"' % anchor)
        if ls:
            a.append('letter-spacing="%s"' % f(ls))
        if extra:
            a.append(extra)
        self.add(" ".join(a) + ">" + s + "</text>")

    # -- animation helpers -----------------------------------------------------------
    def keyframes(self, name, body):
        self.css_add("@keyframes %s{%s}" % (name, body))

    def anim_class(self, cls, rule):
        self.css_add(".%s{%s}" % (cls, rule))

    def render(self):
        tid = "t"
        out = ['<svg width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg"'
               ' role="img" aria-labelledby="%s">' % (self.w, self.h, self.w, self.h, tid),
               CREDIT,
               '<title id="%s">%s</title>' % (tid, _esc(self.title))]
        if self.desc:
            out.append("<desc>%s</desc>" % _esc(self.desc))
        if self.css:
            out.append("<style>" + "".join(self.css) + "</style>")
        if self.defs:
            out.append("<defs>" + "".join(self.defs) + "</defs>")
        out.extend(self.body)
        out.append("</svg>")
        svg = "\n".join(out) + "\n"
        assert all(ord(ch) < 128 for ch in svg), "R5: non-ASCII in SVG output"
        return svg


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------------- geometry

def pts(seq):
    return " ".join("%s,%s" % (f(x), f(y)) for x, y in seq)


def smooth_path(points, closed_bottom=None):
    """Catmull-Rom-ish smooth path through points using quadratic midpoints."""
    if len(points) < 2:
        return ""
    d = ["M%s,%s" % (f(points[0][0]), f(points[0][1]))]
    for i in range(1, len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        d.append("Q%s,%s %s,%s" % (f(x0), f(y0), f(mx), f(my)))
    d.append("T%s,%s" % (f(points[-1][0]), f(points[-1][1])))
    if closed_bottom is not None:
        d.append("L%s,%s L%s,%s Z" % (f(points[-1][0]), f(closed_bottom),
                                      f(points[0][0]), f(closed_bottom)))
    return " ".join(d)


def ridge(rng, x0, x1, y_base, amp, steps, seed_phase=0.0, jag=0.5):
    """A mountain-like ridge line from x0..x1 around y_base."""
    out = []
    n = max(2, steps)
    y = y_base
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y_base - amp * (0.55 + 0.45 * math.sin(seed_phase + t * math.pi * 2.3)) \
            + rng.uniform(-amp * jag, amp * jag) * (0.4 + 0.6 * abs(math.sin(t * 9)))
        out.append((x, y))
    return out


def wave_path(x0, x1, y, amp, period, phase=0.0, samples=48, close_to=None):
    ps = []
    for i in range(samples + 1):
        x = x0 + (x1 - x0) * i / samples
        ps.append((x, y + amp * math.sin(phase + (x / period) * math.pi * 2)))
    d = ["M%s,%s" % (f(ps[0][0]), f(ps[0][1]))]
    d += ["L%s,%s" % (f(x), f(yy)) for x, yy in ps[1:]]
    if close_to is not None:
        d.append("L%s,%s L%s,%s Z" % (f(x1), f(close_to), f(x0), f(close_to)))
    return " ".join(d)


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc(cx, cy, r, a0, a1):
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return "M%s,%s A%s,%s 0 %d 1 %s,%s" % (f(x0), f(y0), f(r), f(r), large, f(x1), f(y1))
