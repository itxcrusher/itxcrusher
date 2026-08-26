"""Motif library: reusable, seeded, text-free SVG scenery for theme composition.

Every motif has the signature  motif(c, p, box, **kw)
  c    Canvas (themes.svg.Canvas)
  p    palette dict: bg, bg2, ink, muted, acc, acc2, variant ('dark'|'light')
  box  (x, y, w, h) region to draw in

Motifs never render text, so R8 (no facts inside images) holds by construction.
Motion is slow and low-amplitude on purpose: prefers-reduced-motion is not honoured
inside an <img>-loaded SVG by any engine, so nothing here may flash hard or loop fast.
"""
import math

from .svg import (f, fo, so, mix, lighten, darken, pts, smooth_path, ridge, wave_path,
                  polar, arc)


def _dark(p):
    return p["variant"] == "dark"


def _clip_group(c, box, inner, extra=""):
    x, y, w, h = box
    clip = c.clip_rect(x, y, w, h)
    c.group(inner, 'clip-path="%s" %s' % (clip, extra))


def loop_translate(c, inner, dx, dy, dur, box=None, delay=0.0, ease="linear"):
    """Wrap `inner` in a group that translates from (0,0) to (dx,dy) forever."""
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "from{transform:translate(0,0)}to{transform:translate(%spx,%spx)}"
                % (f(dx), f(dy)))
    c.anim_class(cls, "animation:%s %ss %s %ss infinite" % (name, f(dur), ease, f(-delay)))
    g = '<g class="%s">%s</g>' % (cls, inner)
    if box:
        _clip_group(c, box, g)
    else:
        c.add(g)


def _opacity_class(c, values, dur, ease="ease-in-out"):
    """A reusable opacity keyframe class; elements set their own delay inline."""
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, values)
    c.anim_class(cls, "animation:%s %ss %s infinite" % (name, f(dur), ease))
    return cls


def _delay(rng, dur):
    return 'style="animation-delay:-%ss"' % f(rng.uniform(0, dur))


# ------------------------------------------------------------------------ backgrounds

def gradient_bg(c, p, box, top=None, bottom=None, horizontal=False):
    x, y, w, h = box
    top = top or p["bg"]
    bottom = bottom or p["bg2"]
    g = c.lin_grad([(0, top, 1), (1, bottom, 1)], 0, 0, (1 if horizontal else 0),
                   (0 if horizontal else 1))
    c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (
        f(x), f(y), f(w), f(h), g))


def vignette(c, p, box, strength=0.55, colour=None):
    x, y, w, h = box
    col = colour or ("#000000" if _dark(p) else p["bg2"])
    g = c.rad_grad([(0.45, col, 0), (1, col, strength)], 0.5, 0.5, 0.75)
    c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (
        f(x), f(y), f(w), f(h), g))


def band(c, p, box, y, h, colour=None, op=1.0):
    x, _, w, _ = box
    c.rect(x, y, w, h, colour or p["acc"], op)


def rail(c, p, box, side="left", w=16, colour=None):
    x, y, bw, h = box
    col = colour or p["acc"]
    if side == "left":
        c.rect(x, y, w, h, col)
    elif side == "right":
        c.rect(x + bw - w, y, w, h, col)
    elif side == "bottom":
        c.rect(x, y + h - w, bw, w, col)
    else:
        c.rect(x, y, bw, w, col)


def frame(c, p, box, inset=10, colour=None, w=2, op=1.0, rx=0):
    x, y, bw, h = box
    c.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" %s/>' % (
        f(x + inset), f(y + inset), f(bw - 2 * inset), f(h - 2 * inset), f(rx),
        so(colour or p["acc"], op, w)))


def speckle(c, p, box, n=220, colour=None, op=0.18, rmax=1.4):
    x, y, w, h = box
    col = colour or (p["ink"] if _dark(p) else p["muted"])
    r = c.rng
    out = []
    for _ in range(n):
        out.append('<circle cx="%s" cy="%s" r="%s" %s/>' % (
            f(r.uniform(x, x + w)), f(r.uniform(y, y + h)), f(r.uniform(0.4, rmax)),
            fo(col, r.uniform(op * 0.4, op))))
    c.add("<g>" + "".join(out) + "</g>")


def glow_spot(c, p, box, cx, cy, r, colour=None, op=0.6):
    col = colour or p["acc"]
    g = c.rad_grad([(0, col, op), (1, col, 0)], 0.5, 0.5, 0.5)
    c.add('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(cx), f(cy), f(r), g))


def fog(c, p, box, y, h, colour=None, op=0.35, drift=60, dur=26):
    x, _, w, _ = box
    col = colour or (p["ink"] if _dark(p) else "#ffffff")
    b = c.blur(18)
    inner = '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s filter="%s"/>' % (
        f(x - 80), f(y), f(w + 160 + drift), f(h), f(h / 2), fo(col, op), b)
    loop_translate(c, inner, -drift, 0, dur, box, ease="ease-in-out")
    # ease-in-out loop returns to start abruptly; use an alternate class instead
    c.css[-1] = c.css[-1].replace("infinite", "infinite alternate")


# --------------------------------------------------------------------------- weather

def rain(c, p, box, layers=3, density=1.0, angle=9, colour=None, base_op=0.5):
    x, y, w, h = box
    col = colour or (p["acc2"] if _dark(p) else p["ink"])
    r = c.rng
    t = math.tan(math.radians(angle))
    for li in range(layers):
        depth = (li + 1) / layers                       # 1 = nearest
        n = int((18 + 22 * depth) * density)
        length = 18 + 30 * depth
        sw = 0.8 + 1.3 * depth
        op = base_op * (0.35 + 0.65 * depth)
        speed = 2.6 - 1.5 * depth                       # seconds per box height
        segs = []
        for _ in range(n):
            px, py = r.uniform(x - 40, x + w + 40), r.uniform(y, y + h)
            for oy in (0, -h):
                segs.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (
                    f(px), f(py + oy), f(px + length * t), f(py + oy + length)))
        inner = '<g %s stroke-linecap="round">%s</g>' % (so(col, op, sw), "".join(segs))
        loop_translate(c, inner, h * t, h, speed, box)


def snow(c, p, box, layers=3, density=1.0, colour=None, base_op=0.9):
    x, y, w, h = box
    col = colour or ("#ffffff" if _dark(p) else p["acc2"])
    r = c.rng
    for li in range(layers):
        depth = (li + 1) / layers
        n = int((14 + 16 * depth) * density)
        rad = 1.2 + 2.4 * depth
        op = base_op * (0.35 + 0.65 * depth)
        dur = 14 - 7 * depth
        dots = []
        for _ in range(n):
            px, py = r.uniform(x, x + w), r.uniform(y, y + h)
            for oy in (0, -h):
                dots.append('<circle cx="%s" cy="%s" r="%s"/>' % (f(px), f(py + oy), f(rad)))
        sway = c.uid("k")
        c.keyframes(sway, "0%%,100%%{transform:translateX(0)}50%%{transform:translateX(%spx)}"
                    % f(10 + 14 * depth))
        swc = c.uid("a")
        c.anim_class(swc, "animation:%s %ss ease-in-out infinite" % (sway, f(dur * 0.6)))
        inner = '<g class="%s" %s>%s</g>' % (swc, fo(col, op), "".join(dots))
        loop_translate(c, inner, 0, h, dur, box)


def clouds(c, p, box, n=5, colour=None, layers=2, op=None, y_frac=(0.15, 0.6)):
    x, y, w, h = box
    r = c.rng
    for li in range(layers):
        depth = (li + 1) / layers
        col = colour or (lighten(p["bg2"], 0.18 * depth) if _dark(p)
                         else "#ffffff")
        o = op if op is not None else (0.3 if _dark(p) else 0.9)
        parts = []
        for _ in range(n):
            cx = r.uniform(x, x + w)
            cy = y + h * r.uniform(*y_frac)
            scale = 0.7 + 0.8 * depth
            blobs = []
            for k in range(5):
                bx = cx + (k - 2) * 26 * scale + r.uniform(-8, 8)
                by = cy + r.uniform(-6, 6) * scale
                rr = (18 + r.uniform(0, 14)) * scale * (1.25 if k == 2 else 1)
                blobs.append('<circle cx="%s" cy="%s" r="%s"/>' % (f(bx), f(by), f(rr)))
            for ox in (0, w + 200):
                parts.append('<g transform="translate(%s,0)">%s</g>' % (f(ox), "".join(blobs)))
        inner = '<g %s>%s</g>' % (fo(col, o * (0.5 + 0.5 * depth)), "".join(parts))
        loop_translate(c, inner, -(w + 200), 0, 70 - 25 * depth, box)


def lightning(c, p, box, bolts=2, colour=None):
    x, y, w, h = box
    col = colour or ("#eaf6ff" if _dark(p) else p["acc"])
    r = c.rng
    for b in range(bolts):
        dur = 9 + 4 * b
        name, cls = c.uid("k"), c.uid("a")
        c.keyframes(name, "0%%,86%%{opacity:0}87%%{opacity:1}89%%{opacity:.25}"
                          "91%%{opacity:.9}93%%,100%%{opacity:0}")
        c.anim_class(cls, "animation:%s %ss linear %ss infinite" % (name, f(dur), f(-r.uniform(0, dur))))
        sx = x + w * r.uniform(0.15, 0.85)
        seg = [(sx, y)]
        cy = y
        while cy < y + h * 0.85:
            cy += r.uniform(14, 30)
            seg.append((sx + r.uniform(-22, 22), cy))
            sx = seg[-1][0]
        d = "M" + " L".join("%s,%s" % (f(a), f(bb)) for a, bb in seg)
        branch = seg[len(seg) // 2]
        bd = "M%s,%s L%s,%s L%s,%s" % (f(branch[0]), f(branch[1]), f(branch[0] + 26),
                                       f(branch[1] + 22), f(branch[0] + 40), f(branch[1] + 50))
        gl = c.glow(6, col, 0.9)
        c.add('<g class="%s"><rect x="%s" y="%s" width="%s" height="%s" %s/>'
              '<path d="%s" fill="none" %s stroke-linejoin="round" filter="%s"/>'
              '<path d="%s" fill="none" %s filter="%s"/></g>' % (
                  cls, f(x), f(y), f(w), f(h), fo(col, 0.08),
                  d, so(col, 0.95, 2.4), gl, bd, so(col, 0.7, 1.4), gl))


def sun(c, p, box, cx, cy, r, colour=None, glow=0.5, rays=0):
    col = colour or p["acc"]
    if glow:
        glow_spot(c, p, box, cx, cy, r * 3.2, col, glow)
    if rays:
        rays_motif(c, p, box, cx, cy, n=rays, colour=col, r0=r * 1.3, r1=r * 3.6, op=0.18)
    c.circle(cx, cy, r, col)


def moon(c, p, box, cx, cy, r, colour=None, glow=0.35, crescent=True):
    col = colour or ("#f4f1e6" if _dark(p) else p["acc2"])
    if glow:
        glow_spot(c, p, box, cx, cy, r * 3.4, col, glow)
    if crescent:
        cid = c.uid("m")
        c.defs_add('<mask id="%s"><circle cx="%s" cy="%s" r="%s" fill="#fff"/>'
                   '<circle cx="%s" cy="%s" r="%s" fill="#000"/></mask>' % (
                       cid, f(cx), f(cy), f(r), f(cx + r * 0.42), f(cy - r * 0.22), f(r * 0.86)))
        c.add('<circle cx="%s" cy="%s" r="%s" fill="%s" mask="url(#%s)"/>' % (
            f(cx), f(cy), f(r), col, cid))
    else:
        c.circle(cx, cy, r, col)


def rays_motif(c, p, box, cx, cy, n=14, colour=None, r0=40, r1=200, op=0.2, dur=90):
    col = colour or p["acc"]
    parts = []
    for i in range(n):
        a = 360 * i / n
        x0, y0 = polar(cx, cy, r0, a - 3)
        x1, y1 = polar(cx, cy, r1, a - 6)
        x2, y2 = polar(cx, cy, r1, a + 6)
        x3, y3 = polar(cx, cy, r0, a + 3)
        parts.append('<polygon points="%s"/>' % pts([(x0, y0), (x1, y1), (x2, y2), (x3, y3)]))
    g = c.lin_grad([(0, col, op), (1, col, 0)], 0, 0, 1, 0)
    c.add('<g fill="%s">%s<animateTransform attributeName="transform" type="rotate" '
          'from="0 %s %s" to="360 %s %s" dur="%ss" repeatCount="indefinite"/></g>' % (
              g, "".join(parts), f(cx), f(cy), f(cx), f(cy), f(dur)))


def light_shafts(c, p, box, n=4, colour=None, op=0.16):
    x, y, w, h = box
    col = colour or ("#fff6c8" if _dark(p) else p["acc"])
    r = c.rng
    g = c.lin_grad([(0, col, op), (1, col, 0)], 0, 0, 0, 1)
    cls = _opacity_class(c, "0%,100%{opacity:.6}50%{opacity:1}", 7)
    parts = []
    for _ in range(n):
        tx = r.uniform(x + w * 0.25, x + w * 0.95)
        wd = r.uniform(30, 70)
        parts.append('<polygon points="%s" class="%s" %s/>' % (
            pts([(tx, y - 10), (tx + wd, y - 10), (tx - 90, y + h + 10), (tx - 90 - wd * 2.2, y + h + 10)]),
            cls, _delay(r, 7)))
    c.add('<g fill="%s">%s</g>' % (g, "".join(parts)))


# ------------------------------------------------------------------------ cosmic

def stars(c, p, box, n=90, colour=None, twinkle=True, rmax=1.8):
    x, y, w, h = box
    col = colour or ("#ffffff" if _dark(p) else p["acc2"])
    r = c.rng
    cls = _opacity_class(c, "0%,100%{opacity:.2}50%{opacity:1}", 3.2) if twinkle else ""
    parts = []
    for _ in range(n):
        d = (' class="%s" style="animation-delay:-%ss;animation-duration:%ss"' % (
            cls, f(r.uniform(0, 4)), f(r.uniform(2.2, 4.8)))) if twinkle and r.random() < 0.6 else ""
        parts.append('<circle cx="%s" cy="%s" r="%s" %s%s/>' % (
            f(r.uniform(x, x + w)), f(r.uniform(y, y + h)), f(r.uniform(0.5, rmax)),
            fo(col, r.uniform(0.35, 0.95)), d))
    c.add("<g>" + "".join(parts) + "</g>")


def nebula(c, p, box, colours=None, blobs=4, op=0.5):
    x, y, w, h = box
    cols = colours or [p["acc"], p["acc2"], mix(p["acc"], p["acc2"], 0.5)]
    r = c.rng
    b = c.blur(34)
    parts = []
    for i in range(blobs):
        col = cols[i % len(cols)]
        parts.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" %s/>' % (
            f(r.uniform(x + 80, x + w - 80)), f(r.uniform(y + 20, y + h - 20)),
            f(r.uniform(120, 260)), f(r.uniform(40, 90)), fo(col, op * r.uniform(0.5, 1))))
    inner = '<g filter="%s">%s</g>' % (b, "".join(parts))
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "0%,100%{transform:translate(0,0)}50%{transform:translate(-26px,8px)}")
    c.anim_class(cls, "animation:%s 40s ease-in-out infinite" % name)
    _clip_group(c, box, '<g class="%s">%s</g>' % (cls, inner))


def planet(c, p, box, cx, cy, r, colour=None, ring=False):
    col = colour or p["acc"]
    g = c.rad_grad([(0, lighten(col, 0.35), 1), (0.7, col, 1), (1, darken(col, 0.6), 1)],
                   0.35, 0.3, 0.75)
    glow_spot(c, p, box, cx, cy, r * 1.9, col, 0.35)
    c.add('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(cx), f(cy), f(r), g))
    if ring:
        c.add('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" %s/>' % (
            f(cx), f(cy), f(r * 1.7), f(r * 0.42), so(lighten(col, 0.4), 0.7, 3)))


def craters(c, p, box, n=12, colour=None, y_from=0.55):
    x, y, w, h = box
    r = c.rng
    base = colour or p["bg2"]
    parts = []
    for _ in range(n):
        cx, cy = r.uniform(x, x + w), r.uniform(y + h * y_from, y + h)
        rr = r.uniform(8, 30)
        parts.append('<circle cx="%s" cy="%s" r="%s" %s/>' % (f(cx), f(cy), f(rr), fo(darken(base, 0.35), 0.8)))
        parts.append('<circle cx="%s" cy="%s" r="%s" %s/>' % (f(cx + rr * 0.18), f(cy + rr * 0.18), f(rr * 0.8), fo(lighten(base, 0.12), 0.9)))
    c.add("<g>" + "".join(parts) + "</g>")


def eclipse(c, p, box, cx, cy, r, colour=None):
    col = colour or p["acc"]
    b = c.blur(14)
    cls = _opacity_class(c, "0%,100%{opacity:.75}50%{opacity:1}", 6)
    c.add('<circle cx="%s" cy="%s" r="%s" fill="none" %s filter="%s" class="%s"/>' % (
        f(cx), f(cy), f(r * 1.06), so(col, 0.95, r * 0.35), b, cls))
    c.add('<circle cx="%s" cy="%s" r="%s" fill="none" %s/>' % (f(cx), f(cy), f(r * 1.02), so(lighten(col, 0.5), 0.9, 2)))
    c.circle(cx, cy, r, p["bg"] if _dark(p) else p["ink"])


# ------------------------------------------------------------------------- terrain

def mountains(c, p, box, layers=3, snowline=True, colour=None, bias=0.45, peak=0.42):
    """Ridges rising toward the right so the type block on the left stays clear.
    bias: amplitude multiplier at the left edge (1.0 at the right)."""
    x, y, w, h = box
    r = c.rng
    base = colour or (p["bg2"] if _dark(p) else p["muted"])
    for li in range(layers):
        depth = (li + 1) / layers                       # 1 = front
        amp = h * peak * (0.55 + 0.45 * depth)
        ybase = y + h * (0.86 + 0.06 * depth)
        rid = ridge(r, x - 40, x + w + 40, ybase, amp, 10 + li * 3, seed_phase=li * 1.7, jag=0.3)
        rid = [(px, ybase - (ybase - py) * (bias + (1 - bias) * max(0.0, (px - x) / w))) for px, py in rid]
        col = mix(base, p["bg"] if _dark(p) else "#ffffff", 0.55 * (1 - depth))
        col = darken(col, 0.25 * depth) if _dark(p) else col
        if snowline and li == layers - 1:
            snow_col = "#ffffff" if _dark(p) else "#f7fbff"
            c.poly(rid + [(x + w + 40, y + h + 10), (x - 40, y + h + 10)], snow_col, 0.95)
            drop = [(px, py + 14 + 10 * abs(math.sin(i * 1.3))) for i, (px, py) in enumerate(rid)]
            c.poly(drop + [(x + w + 40, y + h + 10), (x - 40, y + h + 10)], col, 1.0)
        else:
            c.poly(rid + [(x + w + 40, y + h + 10), (x - 40, y + h + 10)], col, 1.0)


def dunes(c, p, box, layers=3, colour=None):
    x, y, w, h = box
    base = colour or p["acc"]
    for li in range(layers):
        depth = (li + 1) / layers
        ybase = y + h * (0.55 + 0.15 * li)
        d = wave_path(x - 20, x + w + 20, ybase, h * 0.09 * (1 + li * 0.3), w * (0.55 + 0.25 * li),
                      phase=li * 1.9, close_to=y + h + 10)
        col = darken(base, 0.18 * (layers - li)) if _dark(p) else lighten(base, 0.28 * (layers - li - 1))
        c.path(d, col, 1.0)
        # wind-side shading line
        c.path(wave_path(x - 20, x + w + 20, ybase + 2, h * 0.09 * (1 + li * 0.3), w * (0.55 + 0.25 * li),
                         phase=li * 1.9), "none", 1, lighten(col, 0.25) if _dark(p) else darken(col, 0.18), 0.7, 1.2)


def strata(c, p, box, bands=7, colour=None, jag=6):
    x, y, w, h = box
    r = c.rng
    base = colour or p["bg2"]
    step = h / bands
    for i in range(bands):
        top = y + i * step
        seq = []
        n = 18
        for k in range(n + 1):
            seq.append((x + w * k / n, top + r.uniform(-jag, jag)))
        pl = seq + [(x + w, y + h + 4), (x, y + h + 4)]
        t = (i % 3) * 0.16
        col = lighten(base, t) if _dark(p) else darken(base, t)
        c.poly(pl, col, 1.0)
        c.add('<polyline points="%s" fill="none" %s/>' % (pts(seq), so(lighten(base, 0.3) if _dark(p) else darken(base, 0.35), 0.5, 1)))
    speckle(c, p, box, n=160, op=0.14)


def cracked_earth(c, p, box, y0, colour=None, n=14):
    x, y, w, h = box
    col = colour or (p["bg"] if _dark(p) else p["ink"])
    r = c.rng
    parts = []
    for _ in range(n):
        px = r.uniform(x, x + w)
        py = y0 + r.uniform(0, (y + h) - y0)
        seg = [(px, py)]
        for _k in range(r.randint(2, 4)):
            seg.append((seg[-1][0] + r.uniform(-40, 40), seg[-1][1] + r.uniform(-12, 18)))
        parts.append('<polyline points="%s" fill="none" %s stroke-linejoin="round"/>' % (
            pts(seg), so(col, 0.55, 1.4)))
    c.add("<g>" + "".join(parts) + "</g>")


def trees(c, p, box, n=26, layers=2, colour=None):
    x, y, w, h = box
    r = c.rng
    base = colour or p["bg2"]
    for li in range(layers):
        depth = (li + 1) / layers
        col = mix(base, p["bg"], 0.35 * (1 - depth)) if _dark(p) else mix(base, "#ffffff", 0.45 * (1 - depth))
        parts = []
        for _ in range(int(n * (0.6 + 0.4 * depth))):
            tx = r.uniform(x - 20, x + w + 20)
            th = h * r.uniform(0.35, 0.75) * (0.7 + 0.5 * depth)
            tw = th * r.uniform(0.28, 0.4)
            base_y = y + h + 6
            tiers = []
            for k in range(3):
                ty = base_y - th * (0.35 + 0.3 * k)
                tiers.append('<polygon points="%s"/>' % pts([
                    (tx, ty - th * 0.36), (tx + tw * (1 - 0.22 * k), ty + th * 0.1), (tx - tw * (1 - 0.22 * k), ty + th * 0.1)]))
            parts.append('<g>%s<rect x="%s" y="%s" width="%s" height="%s"/></g>' % (
                "".join(tiers), f(tx - tw * 0.05), f(base_y - th * 0.3), f(tw * 0.1), f(th * 0.3)))
        c.add('<g %s>%s</g>' % (fo(col, 1.0), "".join(parts)))


def fireflies(c, p, box, n=14, colour=None):
    x, y, w, h = box
    col = colour or ("#f6ff9a" if _dark(p) else p["acc"])
    r = c.rng
    cls = _opacity_class(c, "0%,100%{opacity:0}45%{opacity:1}", 4.5)
    gl = c.glow(3, col, 0.8)
    parts = []
    for _ in range(n):
        parts.append('<circle cx="%s" cy="%s" r="%s" class="%s" style="animation-delay:-%ss;animation-duration:%ss"/>' % (
            f(r.uniform(x + 20, x + w - 20)), f(r.uniform(y + 20, y + h - 20)), f(r.uniform(1.4, 2.6)),
            cls, f(r.uniform(0, 6)), f(r.uniform(3.5, 6.5))))
    c.add('<g fill="%s" filter="%s">%s</g>' % (col, gl, "".join(parts)))


def petals(c, p, box, n=26, colour=None, shape="petal"):
    x, y, w, h = box
    r = c.rng
    col = colour or p["acc"]
    parts = []
    for _ in range(n):
        px, py = r.uniform(x, x + w), r.uniform(y, y + h)
        s = r.uniform(0.6, 1.3)
        rot = r.uniform(0, 360)
        for oy in (0, -h):
            if shape == "leaf":
                d = "M0,-9 C6,-6 8,2 0,9 C-8,2 -6,-6 0,-9 Z"
            else:
                d = "M0,-7 C5,-7 7,-1 0,7 C-7,-1 -5,-7 0,-7 Z"
            parts.append('<path d="%s" transform="translate(%s,%s) rotate(%s) scale(%s)" %s>'
                         '<animateTransform attributeName="transform" type="rotate" additive="sum" '
                         'from="0" to="360" dur="%ss" repeatCount="indefinite"/></path>' % (
                             d, f(px), f(py + oy), f(rot), f(s), fo(col, r.uniform(0.55, 0.95)), f(r.uniform(5, 11))))
    inner = "<g>" + "".join(parts) + "</g>"
    sway = c.uid("k")
    c.keyframes(sway, "0%,100%{transform:translateX(0)}50%{transform:translateX(-40px)}")
    swc = c.uid("a")
    c.anim_class(swc, "animation:%s 9s ease-in-out infinite" % sway)
    loop_translate(c, '<g class="%s">%s</g>' % (swc, inner), 0, h, 16, box)


def waves(c, p, box, layers=3, colour=None, amp=9, y_frac=0.55):
    x, y, w, h = box
    base = colour or p["acc2"]
    for li in range(layers):
        depth = (li + 1) / layers
        yy = y + h * (y_frac + 0.14 * li)
        period = w * (0.5 - 0.1 * li)
        col = mix(base, p["bg"], 0.45 * (1 - depth)) if _dark(p) else mix(base, "#ffffff", 0.5 * (1 - depth))
        d = wave_path(x - period, x + w + period, yy, amp * (0.6 + 0.6 * depth), period,
                      phase=li * 1.3, samples=120, close_to=y + h + 20)
        inner = '<path d="%s" %s/>' % (d, fo(col, 0.9))
        loop_translate(c, inner, period, 0, 9 - 2 * li, box)


def bubbles(c, p, box, n=22, colour=None):
    x, y, w, h = box
    col = colour or (p["acc2"] if _dark(p) else p["acc"])
    r = c.rng
    parts = []
    for _ in range(n):
        px, py = r.uniform(x, x + w), r.uniform(y, y + h)
        rr = r.uniform(1.5, 5)
        for oy in (0, h):
            parts.append('<circle cx="%s" cy="%s" r="%s" fill="none" %s/>' % (
                f(px), f(py + oy), f(rr), so(col, r.uniform(0.3, 0.8), 1)))
    loop_translate(c, "<g>" + "".join(parts) + "</g>", 0, -h, 14, box)


def aurora(c, p, box, curtains=3, colours=None):
    x, y, w, h = box
    cols = colours or [p["acc"], p["acc2"], mix(p["acc"], p["acc2"], 0.5)]
    r = c.rng
    b = c.blur(9)
    for i in range(curtains):
        col = cols[i % len(cols)]
        g = c.lin_grad([(0, col, 0), (0.35, col, 0.75), (1, col, 0)], 0, 0, 0, 1)
        top = y + h * r.uniform(0.02, 0.15)
        bot = y + h * r.uniform(0.55, 0.85)
        seq = []
        n = 12
        for k in range(n + 1):
            px = x - 60 + (w + 120) * k / n
            seq.append((px, top + 18 * math.sin(k * 1.1 + i)))
        d = smooth_path(seq)
        under = list(reversed([(px, bot + 22 * math.sin(k * 0.8 + i * 2)) for k, (px, _) in enumerate(seq)]))
        d2 = smooth_path(under)
        path = d + " " + d2.replace("M", "L", 1) + " Z"
        name, cls = c.uid("k"), c.uid("a")
        c.keyframes(name, "0%%,100%%{transform:translateX(0) skewX(0)}50%%{transform:translateX(%spx) skewX(%sdeg)}"
                    % (f(r.uniform(-30, 30)), f(r.uniform(-6, 6))))
        c.anim_class(cls, "animation:%s %ss ease-in-out infinite" % (name, f(r.uniform(14, 22))))
        c.add('<path d="%s" fill="%s" filter="%s" class="%s"/>' % (path, g, b, cls))


def embers(c, p, box, n=36, colour=None):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    cls = _opacity_class(c, "0%{opacity:0}20%{opacity:1}100%{opacity:0}", 5, "linear")
    parts = []
    for _ in range(n):
        px = r.uniform(x, x + w)
        py = r.uniform(y + h * 0.3, y + h)
        rr = r.uniform(1, 2.6)
        for oy in (0, h):
            parts.append('<circle cx="%s" cy="%s" r="%s" class="%s" style="animation-delay:-%ss;animation-duration:%ss"/>' % (
                f(px), f(py + oy), f(rr), cls, f(r.uniform(0, 5)), f(r.uniform(3.5, 6))))
    gl = c.glow(2.5, col, 0.9)
    loop_translate(c, '<g fill="%s" filter="%s">%s</g>' % (col, gl, "".join(parts)), 0, -h, 8, box)


def lava(c, p, box, cracks=6, colour=None):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    cls = _opacity_class(c, "0%,100%{opacity:.55}50%{opacity:1}", 4)
    gl = c.glow(7, col, 1.0)
    parts = []
    for _ in range(cracks):
        px, py = r.uniform(x, x + w), r.uniform(y + h * 0.15, y + h * 0.9)
        seg = [(px, py)]
        for _k in range(r.randint(4, 8)):
            seg.append((seg[-1][0] + r.uniform(20, 70), seg[-1][1] + r.uniform(-30, 30)))
        parts.append('<polyline points="%s" fill="none" %s stroke-linejoin="round" stroke-linecap="round" class="%s" %s/>' % (
            pts(seg), so(col, 0.95, r.uniform(2, 4)), cls, _delay(r, 4)))
    c.add('<g filter="%s">%s</g>' % (gl, "".join(parts)))


def drips(c, p, box, n=9, colour=None):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    parts = []
    for _ in range(n):
        px = r.uniform(x + 10, x + w - 10)
        ln = r.uniform(h * 0.15, h * 0.6)
        wd = r.uniform(6, 14)
        parts.append('<path d="M%s,%s h%s v%s a%s,%s 0 0 1 -%s,0 Z"/>' % (
            f(px - wd / 2), f(y - 2), f(wd), f(ln), f(wd / 2), f(wd / 2), f(wd)))
    c.add('<g %s>%s</g>' % (fo(col, 0.85), "".join(parts)))
    bubbles(c, p, box, n=10, colour=col)


def crystals(c, p, box, n=12, colour=None):
    x, y, w, h = box
    col = colour or p["acc2"]
    r = c.rng
    cls = _opacity_class(c, "0%,100%{opacity:.3}50%{opacity:.9}", 5)
    parts = []
    for _ in range(n):
        px = r.uniform(x, x + w)
        base_y = y + h + 4
        ht = r.uniform(h * 0.3, h * 0.9)
        wd = r.uniform(18, 48)
        lean = r.uniform(-20, 20)
        g = c.lin_grad([(0, lighten(col, 0.6), 0.9), (1, col, 0.5)], 0, 0, 0, 1)
        parts.append('<polygon points="%s" fill="%s" %s class="%s" %s/>' % (
            pts([(px + lean, base_y - ht), (px + wd / 2, base_y), (px - wd / 2, base_y)]), g,
            so(lighten(col, 0.7), 0.5, 1), cls, _delay(r, 5)))
    c.add("<g>" + "".join(parts) + "</g>")


def dust(c, p, box, n=60, colour=None, op=0.5):
    x, y, w, h = box
    col = colour or p["muted"]
    r = c.rng
    parts = []
    for _ in range(n):
        px, py = r.uniform(x, x + w), r.uniform(y, y + h)
        for ox in (0, w):
            parts.append('<circle cx="%s" cy="%s" r="%s" %s/>' % (
                f(px + ox), f(py), f(r.uniform(0.6, 1.8)), fo(col, r.uniform(op * 0.3, op))))
    loop_translate(c, "<g>" + "".join(parts) + "</g>", -w, 0, 30, box)


# ---------------------------------------------------------------------------- tech

def grid_floor(c, p, box, horizon=0.5, colour=None, rows=9, cols=16, glow=True):
    x, y, w, h = box
    col = colour or p["acc2"]
    hy = y + h * horizon
    cx = x + w / 2
    parts = []
    # verticals converging on a vanishing point above the horizon
    vp_y = hy - h * 0.6
    for i in range(-cols, cols + 1):
        bx = cx + i * (w / cols) * 1.6
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(cx + (bx - cx) * 0.12), f(hy), f(bx), f(y + h)))
    # horizontals: spacing grows toward the viewer; animate by scrolling one period
    lines = []
    for k in range(rows * 2):
        t = (k / rows)
        yy = hy + (y + h - hy) * (t * t) / 4
        lines.append(yy)
    hor = "".join('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(x), f(yy), f(x + w), f(yy)) for yy in lines)
    gl = c.glow(1.6, col, 0.6) if glow else ""
    c.add('<g %s%s>%s</g>' % (so(col, 0.55, 1), (' filter="%s"' % gl) if gl else "", "".join(parts)))
    _clip_group(c, (x, hy, w, y + h - hy), '<g %s>%s<animateTransform attributeName="transform" type="scale" '
                'from="1 1" to="1 1.36" dur="3s" repeatCount="indefinite" additive="sum"/></g>' % (so(col, 0.6, 1), hor))
    # horizon glow line
    c.add('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (f(x), f(hy), f(x + w), f(hy), so(col, 0.9, 2)))


def scanlines(c, p, box, spacing=4, op=0.10, sweep=True, colour=None):
    x, y, w, h = box
    col = colour or ("#000000" if _dark(p) else p["ink"])
    pat = c.pattern(spacing, spacing, '<rect width="%s" height="1" %s/>' % (f(spacing), fo(col, op)))
    c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(w), f(h), pat))
    if sweep:
        sc = p["acc2"] if _dark(p) else p["acc"]
        g = c.lin_grad([(0, sc, 0), (0.5, sc, 0.16 if _dark(p) else 0.1), (1, sc, 0)], 0, 0, 0, 1)
        inner = '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y - 60), f(w), 60, g)
        loop_translate(c, inner, 0, h + 60, 5.5, box)


def sweep(c, p, box, colour=None, period=4.6, width=90):
    x, y, w, h = box
    col = colour or p["acc"]
    g = c.lin_grad([(0, col, 0), (0.85, col, 0.22), (1, col, 0.85)], 0, 0, 1, 0)
    inner = ('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
             '<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (
                 f(x - width), f(y), f(width), f(h), g, f(x), f(y), f(x), f(y + h), so(col, 0.9, 1.5)))
    loop_translate(c, inner, w + width, 0, period, box)


def brackets(c, p, box, colour=None, size=26, inset=12, sw=2.5):
    x, y, w, h = box
    col = colour or p["acc"]
    s = size
    X0, Y0, X1, Y1 = x + inset, y + inset, x + w - inset, y + h - inset
    d = ("M%s,%s v-%s h%s M%s,%s h%s v%s M%s,%s v%s h-%s M%s,%s h-%s v-%s" % (
        f(X0), f(Y0 + s), f(s), f(s), f(X1 - s), f(Y0), f(s), f(s), f(X1), f(Y1 - s), f(s), f(s),
        f(X0 + s), f(Y1), f(s), f(s)))
    c.path(d, "none", 1, col, 0.95, sw)


def ticks(c, p, box, colour=None, every=30, y=None, length=6, op=0.6):
    x, by, w, h = box
    col = colour or p["acc2"]
    yy = by + (y if y is not None else 8)
    parts = []
    i = 0
    px = x + 14
    while px < x + w - 14:
        ln = length * (2 if i % 5 == 0 else 1)
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(px), f(yy), f(px), f(yy + ln)))
        px += every
        i += 1
    c.add('<g %s>%s</g>' % (so(col, op, 1), "".join(parts)))


def eqbars(c, p, box, x0, y0, n=5, colour=None, bw=8, bh=34, gap=5):
    col = colour or p["acc2"]
    r = c.rng
    parts = []
    for i in range(n):
        bx = x0 + i * (bw + gap)
        hs = [r.uniform(0.25, 1) for _ in range(4)]
        vals = ";".join(f(bh * v) for v in hs + [hs[0]])
        ys = ";".join(f(y0 + bh - bh * v) for v in hs + [hs[0]])
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" %s>'
                     '<animate attributeName="height" values="%s" dur="%ss" repeatCount="indefinite"/>'
                     '<animate attributeName="y" values="%s" dur="%ss" repeatCount="indefinite"/></rect>' % (
                         f(bx), f(y0), f(bw), f(bh * hs[0]), fo(col, 0.85), vals, f(2.2 + i * 0.35), ys, f(2.2 + i * 0.35)))
    c.add("<g>" + "".join(parts) + "</g>")


def traces(c, p, box, n=14, colour=None, draw=True, pads=True, y_from=0.0):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    parts = []
    gl = c.glow(2, col, 0.5)
    for i in range(n):
        px, py = r.uniform(x, x + w), r.uniform(y + h * y_from, y + h)
        seg = [(px, py)]
        L = 0
        for _k in range(r.randint(2, 5)):
            horizontal = (_k % 2 == 0)
            d = r.choice([-1, 1]) * r.uniform(40, 160)
            nx, ny = (seg[-1][0] + d, seg[-1][1]) if horizontal else (seg[-1][0], seg[-1][1] + d * 0.5)
            L += abs(d) if horizontal else abs(d * 0.5)
            seg.append((nx, ny))
        cls = ""
        if draw:
            name, cls = c.uid("k"), c.uid("a")
            c.keyframes(name, "to{stroke-dashoffset:0}")
            c.anim_class(cls, "stroke-dasharray:%s;stroke-dashoffset:%s;animation:%s %ss ease-out %ss forwards" % (
                f(L + 2), f(L + 2), name, f(1.2 + L / 260), f(0.15 * i)))
        parts.append('<polyline points="%s" fill="none" %s class="%s" stroke-linejoin="round" stroke-linecap="round"/>' % (
            pts(seg), so(col, 0.8, 1.6), cls))
        if pads:
            ex, ey = seg[-1]
            parts.append('<circle cx="%s" cy="%s" r="3.2" %s/>' % (f(ex), f(ey), fo(col, 0.9)))
            parts.append('<circle cx="%s" cy="%s" r="1.4" %s/>' % (f(ex), f(ey), fo(p["bg"], 1)))
            parts.append('<circle cx="%s" cy="%s" r="2.4" fill="none" %s/>' % (f(px), f(py), so(col, 0.9, 1.2)))
    c.add('<g filter="%s">%s</g>' % (gl, "".join(parts)))


def nodes(c, p, box, n=24, k=2, colour=None, pulse=True):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    P = [(r.uniform(x + 20, x + w - 20), r.uniform(y + 16, y + h - 16)) for _ in range(n)]
    edges = set()
    for i, (px, py) in enumerate(P):
        near = sorted(range(n), key=lambda j: (P[j][0] - px) ** 2 + (P[j][1] - py) ** 2)[1:k + 1]
        for j in near:
            edges.add((min(i, j), max(i, j)))
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "to{stroke-dashoffset:-40}")
    c.anim_class(cls, "stroke-dasharray:6 34;animation:%s 3s linear infinite" % name)
    e = "".join('<line x1="%s" y1="%s" x2="%s" y2="%s"/>' % (f(P[i][0]), f(P[i][1]), f(P[j][0]), f(P[j][1])) for i, j in edges)
    c.add('<g %s>%s</g>' % (so(col, 0.28, 1), e))
    c.add('<g %s class="%s">%s</g>' % (so(lighten(col, 0.3), 0.9, 1.4), cls, e))
    dots = []
    for i, (px, py) in enumerate(P):
        rr = r.uniform(2.2, 4.5)
        an = ('<animate attributeName="r" values="%s;%s;%s" dur="%ss" repeatCount="indefinite"/>' % (
            f(rr), f(rr * 1.7), f(rr), f(r.uniform(2.5, 5)))) if pulse else ""
        dots.append('<circle cx="%s" cy="%s" r="%s" %s>%s</circle>' % (f(px), f(py), f(rr), fo(col, 0.95), an))
    gl = c.glow(3, col, 0.7)
    c.add('<g filter="%s">%s</g>' % (gl, "".join(dots)))


def blocks(c, p, box, n=6, colour=None, y0=None, size=44):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    yy = y0 if y0 is not None else y + h * 0.5 - size / 2
    gap = (w - 40 - n * size) / (n - 1)
    cls = _opacity_class(c, "0%,100%{opacity:.35}50%{opacity:1}", 4)
    parts = []
    for i in range(n):
        bx = x + 20 + i * (size + gap)
        ticks_ = "".join('<rect x="%s" y="%s" width="%s" height="3"/>' % (
            f(bx + 8), f(yy + 9 + k * 7), f(r.uniform(8, size - 16))) for k in range(4))
        parts.append('<g class="%s" style="animation-delay:-%ss"><rect x="%s" y="%s" width="%s" height="%s" rx="5" fill="none" %s/>'
                     '<g %s>%s</g></g>' % (cls, f(i * 0.6), f(bx), f(yy), f(size), f(size), so(col, 0.95, 1.8),
                                           fo(col, 0.9), ticks_))
        if i < n - 1:
            lx0, lx1 = bx + size, bx + size + gap
            parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (f(lx0), f(yy + size / 2), f(lx1), f(yy + size / 2), so(col, 0.6, 1.6)))
            parts.append('<circle cx="%s" cy="%s" r="2.6" %s/>' % (f((lx0 + lx1) / 2), f(yy + size / 2), fo(col, 0.9)))
    c.add("<g>" + "".join(parts) + "</g>")


def datarain(c, p, box, cols=30, colour=None):
    """Digital rain built from small rects (no text, so R6/R8 cannot bite)."""
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    step = w / cols
    speeds = [4.5, 6.5, 9.0]
    classes = []
    for sp in speeds:
        name, cls = c.uid("k"), c.uid("a")
        c.keyframes(name, "from{transform:translateY(0)}to{transform:translateY(%spx)}" % f(h))
        c.anim_class(cls, "animation:%s %ss linear infinite" % (name, f(sp)))
        classes.append(cls)
    parts = []
    for i in range(cols):
        cx = x + step * (i + 0.5)
        start = r.uniform(0, h)
        n = r.randint(7, 15)
        segs = []
        for k in range(n):
            op = 1.0 if k == 0 else max(0.12, 0.85 - k * 0.06)
            segs.append('<rect x="%s" y="%s" width="4" height="8" rx="1" %s/>' % (
                f(cx - 2), f(start + k * 11), fo(lighten(col, 0.6) if k == 0 else col, op)))
        gid = c.uid("d")
        parts.append('<g class="%s" style="animation-delay:-%ss"><g id="%s">%s</g><use href="#%s" y="%s"/></g>' % (
            classes[i % 3], f(r.uniform(0, 9)), gid, "".join(segs), gid, f(-h)))
    _clip_group(c, box, "<g>" + "".join(parts) + "</g>")


def rack(c, p, box, rows=4, cols=20, colour=None):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    # rails
    for rx in (x + 22, x + w - 22):
        c.rect(rx - 4, y + 10, 8, h - 20, p["muted"], 0.45)
        for k in range(int((h - 30) / 14)):
            c.rect(rx - 2, y + 18 + k * 14, 4, 4, p["bg"], 0.9, 1)
    cls_on = _opacity_class(c, "0%,49%{opacity:1}50%,100%{opacity:.15}", 1.2, "steps(1)")
    parts = []
    cw = (w - 120) / cols
    for rr in range(rows):
        yy = y + 24 + rr * ((h - 48) / max(1, rows - 1) if rows > 1 else 0)
        c.rect(x + 40, yy - 9, w - 80, 22, p["bg2"] if _dark(p) else lighten(p["muted"], 0.6), 0.9, 3)
        for cc in range(cols):
            cx = x + 52 + cc * cw
            lit = r.random() < 0.7
            colr = col if r.random() < 0.8 else p["acc2"]
            parts.append('<rect x="%s" y="%s" width="6" height="6" rx="1.5" %s class="%s" style="animation-delay:-%ss;animation-duration:%ss"/>' % (
                f(cx), f(yy - 2), fo(colr if lit else p["muted"], 0.95 if lit else 0.3), cls_on if lit else "",
                f(r.uniform(0, 3)), f(r.uniform(0.8, 3.5))))
    c.add("<g>" + "".join(parts) + "</g>")


def radar(c, p, box, cx, cy, rad, colour=None, dur=5):
    col = colour or p["acc"]
    r = c.rng
    for k in range(1, 4):
        c.add('<circle cx="%s" cy="%s" r="%s" fill="none" %s/>' % (f(cx), f(cy), f(rad * k / 3), so(col, 0.4, 1)))
    c.line(cx - rad, cy, cx + rad, cy, col, 0.35, 1)
    c.line(cx, cy - rad, cx, cy + rad, col, 0.35, 1)
    g = c.lin_grad([(0, col, 0.75), (1, col, 0)], 0, 0, 1, 0)
    wedge = "M%s,%s L%s,%s A%s,%s 0 0 0 %s,%s Z" % (f(cx), f(cy), f(cx + rad), f(cy), f(rad), f(rad),
                                                   *[f(v) for v in polar(cx, cy, rad, -46)])
    c.add('<path d="%s" fill="%s"><animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="360 %s %s" dur="%ss" repeatCount="indefinite"/></path>' % (
        wedge, g, f(cx), f(cy), f(cx), f(cy), f(dur)))
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "0%{opacity:1}60%,100%{opacity:0}")
    c.anim_class(cls, "animation:%s %ss linear infinite" % (name, f(dur)))
    for _ in range(4):
        a = r.uniform(0, 360)
        bx, by = polar(cx, cy, r.uniform(rad * 0.3, rad * 0.9), a)
        c.add('<circle cx="%s" cy="%s" r="3" %s class="%s" style="animation-delay:%ss"/>' % (
            f(bx), f(by), fo(lighten(col, 0.4), 1), cls, f(dur * (a / 360.0))))


def gears(c, p, box, colour=None, spec=None):
    col = colour or p["acc"]
    x, y, w, h = box
    spec = spec or [(x + w - 120, y + h * 0.55, 62, 12, 24), (x + w - 205, y + h * 0.3, 40, 9, -16), (x + w - 40, y + h * 0.15, 30, 8, -12)]
    for (cx, cy, R, teeth, dur) in spec:
        path = []
        for i in range(teeth * 2):
            a0 = 360 * i / (teeth * 2)
            a1 = 360 * (i + 1) / (teeth * 2)
            rr = R if i % 2 == 0 else R * 0.8
            path.append(polar(cx, cy, rr, a0))
            path.append(polar(cx, cy, rr, a1))
        g = c.rad_grad([(0, lighten(col, 0.3), 1), (1, darken(col, 0.3), 1)], 0.4, 0.35, 0.7)
        c.add('<g><polygon points="%s" fill="%s" %s/><circle cx="%s" cy="%s" r="%s" fill="none" %s/>'
              '<circle cx="%s" cy="%s" r="%s" %s/>'
              '<animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="%s %s %s" dur="%ss" repeatCount="indefinite"/></g>' % (
                  pts(path), g, so(darken(col, 0.4), 0.8, 1.2), f(cx), f(cy), f(R * 0.5), so(darken(col, 0.45), 0.9, 3),
                  f(cx), f(cy), f(R * 0.14), fo(darken(col, 0.5), 1), f(cx), f(cy), "360" if dur > 0 else "-360", f(cx), f(cy), f(abs(dur))))


def beacon(c, p, box, cx, cy, colour=None, dur=4):
    col = colour or p["acc"]
    g = c.lin_grad([(0, col, 0.55), (1, col, 0)], 0, 0, 1, 0)
    c.add('<g><polygon points="%s" fill="%s"/><polygon points="%s" fill="%s"/>'
          '<animateTransform attributeName="transform" type="rotate" from="0 %s %s" to="360 %s %s" dur="%ss" repeatCount="indefinite"/></g>' % (
              pts([(cx, cy), (cx + 420, cy - 70), (cx + 420, cy + 70)]), g,
              pts([(cx, cy), (cx - 420, cy - 70), (cx - 420, cy + 70)]), g, f(cx), f(cy), f(cx), f(cy), f(dur)))
    glow_spot(c, p, box, cx, cy, 40, col, 0.8)
    c.circle(cx, cy, 8, lighten(col, 0.5))


def blinds(c, p, box, n=7, colour=None, angle=-10, op=None):
    x, y, w, h = box
    col = colour or ("#ffffff" if _dark(p) else p["ink"])
    o = op if op is not None else (0.09 if _dark(p) else 0.08)
    step = h / n
    parts = []
    for i in range(n + 2):
        yy = y - step + i * step
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (f(x - 100), f(yy), f(w + 200), f(step * 0.45), fo(col, o)))
    inner = '<g transform="rotate(%s %s %s)">%s</g>' % (f(angle), f(x + w / 2), f(y + h / 2), "".join(parts))
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "0%,100%{transform:translateY(0)}50%{transform:translateY(6px)}")
    c.anim_class(cls, "animation:%s 12s ease-in-out infinite" % name)
    _clip_group(c, box, '<g class="%s">%s</g>' % (cls, inner))


def hazard(c, p, box, y, h, colour=None, back=None, angle=45, stripe=16):
    x, _, w, _ = box
    col = colour or p["acc"]
    bk = back or (p["bg"] if _dark(p) else p["ink"])
    pat = c.pattern(stripe * 2, stripe * 2, '<rect width="%s" height="%s" fill="%s"/><rect width="%s" height="%s" fill="%s"/>' % (
        f(stripe * 2), f(stripe * 2), bk, f(stripe), f(stripe * 2), col))
    c.defs[-1] = c.defs[-1].replace('patternUnits="userSpaceOnUse"', 'patternUnits="userSpaceOnUse" patternTransform="rotate(%s)"' % f(angle))
    c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(w), f(h), pat))


def rivets(c, p, box, colour=None, inset=14, every=44):
    x, y, w, h = box
    col = colour or p["muted"]
    parts = []
    for px in [x + inset + i * every for i in range(int((w - 2 * inset) / every) + 1)]:
        for py in (y + inset, y + h - inset):
            parts.append('<circle cx="%s" cy="%s" r="4" %s/><circle cx="%s" cy="%s" r="1.6" %s/>' % (
                f(px), f(py), fo(col, 0.9), f(px - 1), f(py - 1), fo(lighten(col, 0.5), 0.9)))
    c.add("<g>" + "".join(parts) + "</g>")


def rust(c, p, box, n=6, colour=None):
    x, y, w, h = box
    col = colour or p["acc"]
    r = c.rng
    b = c.blur(12)
    parts = []
    for _ in range(n):
        parts.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" %s/>' % (
            f(r.uniform(x, x + w)), f(r.uniform(y, y + h)), f(r.uniform(30, 90)), f(r.uniform(14, 40)), fo(col, r.uniform(0.25, 0.5))))
    c.add('<g filter="%s">%s</g>' % (b, "".join(parts)))
    speckle(c, p, box, n=120, colour=col, op=0.35)


def scratches(c, p, box, n=14, colour=None):
    x, y, w, h = box
    col = colour or (p["ink"] if _dark(p) else p["muted"])
    r = c.rng
    parts = []
    for _ in range(n):
        px, py = r.uniform(x, x + w), r.uniform(y, y + h)
        parts.append('<line x1="%s" y1="%s" x2="%s" y2="%s" %s/>' % (
            f(px), f(py), f(px + r.uniform(20, 120)), f(py + r.uniform(-12, 12)), so(col, r.uniform(0.08, 0.25), r.uniform(0.6, 1.4))))
    c.add("<g>" + "".join(parts) + "</g>")


def woodgrain(c, p, box, lines=20, knots=2, colour=None):
    x, y, w, h = box
    col = colour or (lighten(p["bg2"], 0.18) if _dark(p) else darken(p["bg2"], 0.18))
    r = c.rng
    parts = []
    for i in range(lines):
        yy = y + h * (i + 0.5) / lines
        seq = []
        n = 16
        for k in range(n + 1):
            seq.append((x + w * k / n, yy + 4 * math.sin(k * 0.9 + i) + r.uniform(-2, 2)))
        parts.append('<path d="%s" fill="none" %s/>' % (smooth_path(seq), so(col, r.uniform(0.25, 0.6), r.uniform(0.8, 2.2))))
    for _ in range(knots):
        kx, ky = r.uniform(x + 60, x + w - 60), r.uniform(y + 20, y + h - 20)
        for k in range(4):
            parts.append('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" %s/>' % (
                f(kx), f(ky), f(6 + k * 7), f(3 + k * 4), so(col, 0.5, 1.2)))
    c.add("<g>" + "".join(parts) + "</g>")


def panels(c, p, box, colour=None):
    x, y, w, h = box
    col = colour or p["muted"]
    r = c.rng
    plates = [(x + 10, y + 10, w * 0.62, h - 20), (x + w * 0.62 + 24, y + 10, w * 0.38 - 34, h * 0.5 - 16),
              (x + w * 0.62 + 24, y + h * 0.5 + 6, w * 0.38 - 34, h * 0.5 - 16)]
    for (px, py, pw, ph) in plates:
        cut = 14
        c.path("M%s,%s h%s l%s,%s v%s l-%s,%s h-%s l-%s,-%s v-%s Z" % (
            f(px + cut), f(py), f(pw - 2 * cut), f(cut), f(cut), f(ph - 2 * cut), f(cut), f(cut), f(pw - 2 * cut), f(cut), f(cut), f(ph - 2 * cut)),
            p["bg2"], 0.9, col, 0.7, 1.5)
        for (bx, by) in ((px + 22, py + 22), (px + pw - 22, py + 22), (px + 22, py + ph - 22), (px + pw - 22, py + ph - 22)):
            c.add('<circle cx="%s" cy="%s" r="5" %s/><circle cx="%s" cy="%s" r="2" %s/>' % (
                f(bx), f(by), fo(col, 0.9), f(bx), f(by), fo(p["bg"], 1)))
    # piston
    py = y + h * 0.75
    px = x + w * 0.62 + 40
    c.rect(px, py - 7, 70, 14, col, 0.8, 3)
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "0%,100%{transform:translateX(0)}50%{transform:translateX(26px)}")
    c.anim_class(cls, "animation:%s 2.6s ease-in-out infinite" % name)
    c.add('<g class="%s"><rect x="%s" y="%s" width="60" height="8" rx="2" %s/><rect x="%s" y="%s" width="16" height="22" rx="2" %s/></g>' % (
        cls, f(px + 60), f(py - 4), fo(lighten(col, 0.3), 1), f(px + 118), f(py - 11), fo(p["acc"], 1)))
    # status LEDs
    cls_on = _opacity_class(c, "0%,49%{opacity:1}50%,100%{opacity:.2}", 1.4, "steps(1)")
    for i in range(5):
        c.add('<circle cx="%s" cy="%s" r="4" %s class="%s" style="animation-delay:-%ss"/>' % (
            f(x + w * 0.62 + 44 + i * 16), f(y + 30), fo(p["acc2"] if i % 2 else p["acc"], 1), cls_on, f(r.uniform(0, 1.4))))


def letterbox(c, p, box, bar=26, colour="#000000"):
    x, y, w, h = box
    c.rect(x, y, w, bar, colour)
    c.rect(x, y + h - bar, w, bar, colour)


def flare(c, p, box, yy, colour=None):
    x, y, w, h = box
    col = colour or p["acc2"]
    b = c.blur(6)
    g = c.lin_grad([(0, col, 0), (0.5, col, 0.9), (1, col, 0)], 0, 0, 1, 0)
    inner = ('<rect x="%s" y="%s" width="%s" height="3" fill="%s" filter="%s"/>'
             '<rect x="%s" y="%s" width="%s" height="1.2" fill="%s"/>' % (
                 f(x - 100), f(yy - 1.5), f(w * 0.7), g, b, f(x - 100), f(yy - 0.6), f(w * 0.7), g))
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "0%%,100%%{transform:translateX(0)}50%%{transform:translateX(%spx)}" % f(w * 0.45))
    c.anim_class(cls, "animation:%s 16s ease-in-out infinite" % name)
    _clip_group(c, box, '<g class="%s">%s</g>' % (cls, inner))
    glow_spot(c, p, box, x + w * 0.25, yy, 46, lighten(col, 0.4), 0.7)


def vapor_sun(c, p, box, cx, cy, r, colours=None):
    cols = colours or [p["acc"], p["acc2"]]
    g = c.lin_grad([(0, cols[0], 1), (1, cols[1], 1)], 0, 0, 0, 1)
    mid = c.uid("m")
    cuts = "".join('<rect x="%s" y="%s" width="%s" height="%s" fill="#000"/>' % (
        f(cx - r), f(cy + r * (0.15 + k * 0.2)), f(r * 2), f(r * (0.04 + k * 0.03))) for k in range(4))
    c.defs_add('<mask id="%s"><circle cx="%s" cy="%s" r="%s" fill="#fff"/>%s</mask>' % (mid, f(cx), f(cy), f(r), cuts))
    glow_spot(c, p, box, cx, cy, r * 2.2, cols[0], 0.45)
    c.add('<circle cx="%s" cy="%s" r="%s" fill="%s" mask="url(#%s)"/>' % (f(cx), f(cy), f(r), g, mid))


def horizon(c, p, box, yy, colour=None, glow=True):
    x, _, w, _ = box
    col = colour or p["acc"]
    if glow:
        g = c.lin_grad([(0, col, 0), (1, col, 0.35)], 0, 0, 0, 1)
        c.add('<rect x="%s" y="%s" width="%s" height="40" fill="%s"/>' % (f(x), f(yy - 40), f(w), g))
    c.line(x, yy, x + w, yy, col, 0.9, 1.5)


def glitch_bars(c, p, box, n=6, colour=None):
    x, y, w, h = box
    col = colour or p["acc2"]
    r = c.rng
    cls = _opacity_class(c, "0%,92%{opacity:0}93%,96%{opacity:.8}97%,100%{opacity:0}", 4.2, "steps(1)")
    parts = []
    for _ in range(n):
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" %s class="%s" style="animation-delay:-%ss;animation-duration:%ss"/>' % (
            f(r.uniform(x, x + w * 0.7)), f(r.uniform(y, y + h)), f(r.uniform(60, 300)), f(r.uniform(2, 6)), fo(col, 0.85), cls,
            f(r.uniform(0, 4)), f(r.uniform(3.2, 6.5))))
    c.add("<g>" + "".join(parts) + "</g>")


def tumbleweed(c, p, box, colour=None):
    x, y, w, h = box
    col = colour or p["muted"]
    r = c.rng
    cy = y + h - 30
    seg = []
    for k in range(40):
        a = k * 137.5
        rr = r.uniform(8, 22)
        seg.append(polar(0, 0, rr, a))
    d = smooth_path(seg)
    inner = ('<g><path d="%s" fill="none" %s/><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite"/></g>' % (
        d, so(col, 0.8, 1.3)))
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "0%%{transform:translate(%spx,%spx)}100%%{transform:translate(%spx,%spx)}" % (f(x - 40), f(cy), f(x + w + 40), f(cy - 4)))
    c.anim_class(cls, "animation:%s 22s linear infinite" % name)
    _clip_group(c, box, '<g class="%s">%s</g>' % (cls, inner))


def halftone(c, p, box, spacing=11, colour=None, op=0.35):
    x, y, w, h = box
    col = colour or p["acc"]
    pat = c.pattern(spacing, spacing, '<circle cx="%s" cy="%s" r="%s" %s/>' % (f(spacing / 2), f(spacing / 2), f(spacing * 0.22), fo(col, op)))
    g = c.lin_grad([(0, "#ffffff", 1), (1, "#ffffff", 0)], 0, 0, 1, 0)
    mid = c.uid("m")
    c.defs_add('<mask id="%s"><rect x="%s" y="%s" width="%s" height="%s" fill="%s"/></mask>' % (mid, f(x), f(y), f(w), f(h), g))
    c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s" mask="url(#%s)"/>' % (f(x), f(y), f(w), f(h), pat, mid))


def chevrons(c, p, box, y, n=6, colour=None, size=18):
    x, _, w, _ = box
    col = colour or p["acc"]
    parts = []
    px = x + w - 30
    for i in range(n):
        parts.append('<polyline points="%s" fill="none" %s stroke-linejoin="round"/>' % (
            pts([(px - size, y - size), (px, y), (px - size, y + size)]), so(col, 0.9 - i * 0.12, 3)))
        px -= size * 1.2
    c.add("<g>" + "".join(parts) + "</g>")


def cursor(c, p, x, y, w=20, h=44, colour=None, period=1.1):
    col = colour or p["acc"]
    cls = _opacity_class(c, "0%,49%{opacity:1}50%,100%{opacity:0}", period, "steps(1)")
    c.add('<rect x="%s" y="%s" width="%s" height="%s" %s class="%s"/>' % (f(x), f(y), f(w), f(h), fo(col, 0.95), cls))


def draw_line(c, p, x1, y1, x2, y2, colour=None, sw=2, dur=1.1, delay=0.15, op=1.0):
    """A rule that draws itself in once on load."""
    col = colour or p["acc"]
    L = math.hypot(x2 - x1, y2 - y1)
    name, cls = c.uid("k"), c.uid("a")
    c.keyframes(name, "to{stroke-dashoffset:0}")
    c.anim_class(cls, "stroke-dasharray:%s;stroke-dashoffset:%s;animation:%s %ss cubic-bezier(.2,.7,.3,1) %ss forwards" % (
        f(L), f(L), name, f(dur), f(delay)))
    c.add('<line x1="%s" y1="%s" x2="%s" y2="%s" %s stroke-linecap="round" class="%s"/>' % (
        f(x1), f(y1), f(x2), f(y2), so(col, op, sw), cls))


def reveal_clip(c, x, y, w, h, dur=0.9, delay=0.2):
    """Returns an attribute string: clip-path that widens once from 0 to w (typewriter-ish)."""
    cid = c.uid("c")
    name, cls = c.uid("k"), c.uid("a")
    c.defs_add('<clipPath id="%s"><rect class="%s" x="%s" y="%s" width="0" height="%s"/></clipPath>' % (cid, cls, f(x), f(y), f(h)))
    c.keyframes(name, "to{width:%spx}" % f(w))
    c.anim_class(cls, "animation:%s %ss steps(24) %ss forwards" % (name, f(dur), f(delay)))
    return 'clip-path="url(#%s)"' % cid


def hexgrid(c, p, box, size=26, colour=None, op=0.18):
    x, y, w, h = box
    col = colour or p["acc"]
    hw = size * math.sqrt(3)
    hexa = " ".join("%s,%s" % (f(v[0]), f(v[1])) for v in [polar(hw / 2, size, size, a) for a in range(30, 390, 60)])
    pat = c.pattern(hw, size * 3, '<polygon points="%s" fill="none" %s/><polygon points="%s" fill="none" %s transform="translate(%s,%s)"/>' % (
        hexa, so(col, op, 1), hexa, so(col, op, 1), f(hw / 2), f(size * 1.5)))
    c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(w), f(h), pat))


def oscilloscope(c, p, box, yy, colour=None, amp=18, period=90):
    x, y, w, h = box
    col = colour or p["acc"]
    d = wave_path(x - period, x + w + period, yy, amp, period, samples=160)
    gl = c.glow(3, col, 0.8)
    inner = '<path d="%s" fill="none" %s filter="%s"/>' % (d, so(col, 0.95, 2), gl)
    loop_translate(c, inner, period, 0, 2.2, box)


def wires(c, p, box, n=5, colour=None):
    x, y, w, h = box
    col = colour or p["acc2"]
    r = c.rng
    parts = []
    for i in range(n):
        x0, x1 = r.uniform(x, x + w * 0.4), r.uniform(x + w * 0.6, x + w)
        y0, y1 = r.uniform(y, y + h * 0.3), r.uniform(y, y + h * 0.3)
        sag = r.uniform(40, 120)
        parts.append('<path d="M%s,%s Q%s,%s %s,%s" fill="none" %s/>' % (
            f(x0), f(y0), f((x0 + x1) / 2), f(max(y0, y1) + sag), f(x1), f(y1), so(col, 0.7, 2)))
    c.add("<g>" + "".join(parts) + "</g>")


def window_chrome(c, p, box, colour=None, inset=8, rx=10):
    """Terminal window frame with a title bar and three lights. No text."""
    x, y, w, h = box
    col = colour or p["muted"]
    bar_h = 24
    c.add('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" %s/>' % (
        f(x + inset), f(y + inset), f(w - 2 * inset), f(h - 2 * inset), f(rx), so(col, 0.55, 1.5)))
    c.rect(x + inset, y + inset, w - 2 * inset, bar_h, col, 0.12, rx)
    c.rect(x + inset, y + inset + bar_h - 6, w - 2 * inset, 6, col, 0.12)
    c.line(x + inset, y + inset + bar_h, x + w - inset, y + inset + bar_h, col, 0.45, 1)
    for i, lc in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        c.circle(x + inset + 18 + i * 20, y + inset + bar_h / 2, 5.5, lc, 0.95)


def punchcard(c, p, box, cols=40, rows=6, colour=None, op=0.5):
    x, y, w, h = box
    col = colour or p["acc2"]
    r = c.rng
    parts = []
    cw = (w - 40) / cols
    rh = (h - 30) / rows
    for i in range(cols):
        for j in range(rows):
            if r.random() < 0.28:
                parts.append('<rect x="%s" y="%s" width="%s" height="%s" rx="1" %s/>' % (
                    f(x + 20 + i * cw + cw * 0.3), f(y + 15 + j * rh + rh * 0.25), f(cw * 0.4), f(rh * 0.5),
                    fo(col, op * r.uniform(0.5, 1))))
    c.add("<g>" + "".join(parts) + "</g>")
    # the card's cut corner
    c.poly([(x + w - 40, y), (x + w, y), (x + w, y + 40)], col, 0.25)


def pixels(c, p, box, colour=None, size=8):
    """8-bit scenery: blocky clouds, a ground row of blocks, chunky stars."""
    x, y, w, h = box
    col = colour or p["acc"]
    col2 = p["acc2"]
    r = c.rng
    parts = []
    for _ in range(26):
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (
            f(x + int(r.uniform(0, w) / size) * size), f(y + int(r.uniform(0, h * 0.5) / size) * size),
            f(size * 0.5), f(size * 0.5), fo(col2, r.uniform(0.4, 0.9))))
    ground_y = y + h - size * 2
    for i in range(int(w / size) + 1):
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (
            f(x + i * size), f(ground_y), f(size - 1), f(size - 1), fo(col, 0.9 if i % 2 else 0.7)))
        parts.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (
            f(x + i * size), f(ground_y + size), f(size - 1), f(size - 1), fo(darken(col, 0.35), 0.9)))
    for _ in range(3):
        cx = x + int(r.uniform(w * 0.68, w - 80) / size) * size
        cy = y + int(r.uniform(16, h * 0.5) / size) * size
        for (dx, dy, ww) in ((0, 0, 7), (1, -1, 5), (2, -2, 2), (-1, 1, 10)):
            for k in range(ww):
                parts.append('<rect x="%s" y="%s" width="%s" height="%s" %s/>' % (
                    f(cx + (dx + k) * size), f(cy + dy * size), f(size - 1), f(size - 1), fo(p["ink"], 0.85)))
    cls = _opacity_class(c, "0%,100%{opacity:1}50%{opacity:.3}", 1.6, "steps(2)")
    c.add('<g class="%s">%s</g>' % (cls, "".join(parts[:10])))
    c.add("<g>" + "".join(parts[10:]) + "</g>")


def lamp_post(c, p, box, x0, colour=None, light=None):
    x, y, w, h = box
    col = colour or p["ink"]
    lc = light or p["acc"]
    glow_spot(c, p, box, x0, y + 54, 200, lc, 0.5)
    c.rect(x0 - 3, y + 60, 6, h - 60, col, 0.85)
    c.rect(x0 - 26, y + 40, 52, 8, col, 0.9, 2)
    c.path("M%s,%s l-18,-22 h36 Z" % (f(x0), f(y + 40)), col, 0.9)
    c.circle(x0, y + 54, 9, lighten(lc, 0.5), 1.0)


def shade(c, p, box, strength=None, extent=0.68, side="left"):
    """A soft plate of page colour behind the type block so names stay legible over
    busy scenery. Fades to nothing before the focal area."""
    x, y, w, h = box
    st = strength if strength is not None else (0.72 if _dark(p) else 0.66)
    col = p["bg"]
    if side == "left":
        g = c.lin_grad([(0, col, st), (0.55, col, st * 0.85), (1, col, 0)], 0, 0, 1, 0)
        c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(w * extent), f(h), g))
    else:
        g = c.lin_grad([(0, col, 0), (0.45, col, st * 0.85), (1, col, st)], 0, 0, 1, 0)
        c.add('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x + w * (1 - extent)), f(y), f(w * extent), f(h), g))
