"""The theme catalog. One dict per theme; the engine does the rest.

Adding a theme: append a T(...) entry, run `python scripts/profile_theme.py build`,
look at assets/themes/<slug>/ and the gallery, commit. The daily picker includes every
entry that is not marked disabled=True.

Palette keys per variant: bg, bg2 (gradient end), ink (type), muted (secondary type),
acc (primary accent), acc2 (secondary accent).

Text-level styling (all native GitHub markdown, zero images):
  rows   list | table | tasks | numbered | quotes | ls
  chip   plain | code | kbd
  fence  the code-fence language for the stack block (native syntax colours)
  alert  NOTE | TIP | IMPORTANT | WARNING | CAUTION (the CTA callout colour)
  sep    ASCII separator between the header links
"""
from .svg import mix, lighten, darken, contrast

FAMILIES = {
    "tech": "Tech",
    "nature": "Nature and weather",
    "elemental": "Elemental and cosmic",
    "gritty": "Gritty and cinematic",
}


def T(slug, name, family, tagline, dark, light, hero, header, labels, signoff, text,
      snake=None, disabled=False):
    return dict(slug=slug, name=name, family=family, tagline=tagline, dark=dark, light=light,
                hero=hero, header=header, labels=labels, signoff=signoff, text=text,
                snake=snake, disabled=disabled)


def snake_colours(theme, variant):
    """Contribution-snake palette derived from the theme unless overridden.
    Returns (snake_colour, [empty, level1..level4])."""
    if theme.get("snake") and theme["snake"].get(variant):
        return theme["snake"][variant]
    p = theme[variant]
    if variant == "dark":
        empty = p["bg2"]
        levels = [mix(empty, p["acc"], t) for t in (0.3, 0.55, 0.8, 1.0)]
        return p["acc2"], [empty] + levels
    empty = mix(p["bg"], p["muted"], 0.18)
    levels = [mix(empty, p["acc"], t) for t in (0.3, 0.55, 0.8, 1.0)]
    return p["ink"], [empty] + levels


THEMES = [
    # ------------------------------------------------------------------ TECH
    T("cyberpunk", "Cyberpunk", "tech", "Neon grid, chromatic type, a scanline sweep.",
      dark=dict(bg="#07060f", bg2="#160b30", ink="#f7f3ff", muted="#9b90c9", acc="#ff2bd6", acc2="#22e5ff"),
      light=dict(bg="#f4f0ff", bg2="#e2d6ff", ink="#14082e", muted="#5b4b8a", acc="#c2009f", acc2="#0084b0"),
      hero=dict(type="split", font="sans", case="upper", ls=2, name_size=54,
                back=[("grid_floor", dict(horizon=0.6)), ("nebula", dict(blobs=2, op=0.35, light=dict(skip=True)))],
                mid=[("scanlines", dict(op=0.08))],
                front=[("glitch_bars", dict(n=5))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="glow", font="mono", case="upper", ls=2, index="hex"),
      labels=dict(public="public", stack="stack", snake="traffic"),
      signoff="END OF LINE",
      text=dict(rows="table", chip="kbd", fence="yaml", alert="TIP", sep="//")),

    T("operator", "Operator", "tech", "A terminal session. Green phosphor, blinking cursor, ls output.",
      dark=dict(bg="#05070a", bg2="#0b1016", ink="#d7e6d5", muted="#6f8a7a", acc="#3dff8f", acc2="#9be7ff"),
      light=dict(bg="#f3f6f2", bg2="#e0e8dc", ink="#0f1a12", muted="#4f6656", acc="#0a7f3f", acc2="#1b6fa8"),
      hero=dict(type="console",
                back=[("scanlines", dict(op=0.07, sweep=True))],
                front=[("window_chrome", {})]),
      header=dict(style="prompt", font="mono"),
      labels=dict(public="$ ls ~/public", stack="$ cat ~/.stack", snake="$ tail -f contributions"),
      signoff="$ exit",
      text=dict(rows="ls", chip="code", fence="bash", alert="TIP", sep="|")),

    T("hud", "HUD", "tech", "Cyan and amber instrument panel. Brackets, tick marks, a sweep.",
      dark=dict(bg="#041016", bg2="#062634", ink="#e6fbff", muted="#6aa3b5", acc="#ffb02e", acc2="#21d4f5"),
      light=dict(bg="#eefaf9", bg2="#cfeae7", ink="#04262e", muted="#3f6f7a", acc="#b85c00", acc2="#0b7f95"),
      hero=dict(type="plain", font="sans", case="upper", ls=4, name_size=50, reserve=210,
                back=[("hexgrid", dict(size=22, op=0.12)), ("ticks", dict(every=24, y=10)), ("sweep", dict(period=5))],
                front=[("brackets", {}), ("eqbars", dict(x0=760, y0=150, n=6))]),
      header=dict(style="bracket", font="sans", case="upper", ls=2, index="bracket"),
      labels=dict(public="what is public", stack="operating stack", snake="telemetry"),
      signoff="END OF TRANSMISSION",
      text=dict(rows="table", chip="kbd", fence="ini", alert="NOTE", sep="::")),

    T("circuit", "Circuit", "tech", "Traces draw themselves across the board. Pads pulse.",
      dark=dict(bg="#04140f", bg2="#062218", ink="#e8fff5", muted="#5f9c86", acc="#2bff9a", acc2="#ffd166"),
      light=dict(bg="#f6f8f4", bg2="#e3e9df", ink="#0b2a1f", muted="#4c6f61", acc="#123f8f", acc2="#1f8f4a"),
      hero=dict(type="plain", font="sans", reserve=250,
                back=[("traces", dict(n=16, region=(0.56, 0, 0.44, 1))), ("traces", dict(n=6, region=(0, 0.86, 0.6, 0.14), pads=False))]),
      header=dict(style="trace", font="mono"),
      labels=dict(public="net: public", stack="net: stack", snake="net: activity"),
      signoff="EOF",
      text=dict(rows="list", chip="code", fence="hcl", alert="TIP", sep="-")),

    T("neural", "Neural", "tech", "A node graph breathing. Signals travel the edges.",
      dark=dict(bg="#0a0716", bg2="#180c33", ink="#f2ecff", muted="#8c7fb8", acc="#b48cff", acc2="#ff7ad9"),
      light=dict(bg="#f7f4ff", bg2="#e6ddff", ink="#1a0f3d", muted="#5d4f8a", acc="#6a3ff0", acc2="#d1287f"),
      hero=dict(type="glow", font="sans", reserve=300,
                back=[("nodes", dict(n=26, region=(0.55, 0.02, 0.45, 0.96)))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="node"),
      labels=dict(public="what is public", stack="the stack", snake="activity"),
      signoff="end of inference",
      text=dict(rows="list", chip="kbd", fence="python", alert="TIP", sep="+")),

    T("ledger", "Ledger", "tech", "Hash-chained blocks along the top. The chain is intact.",
      dark=dict(bg="#05080f", bg2="#0a1426", ink="#e9f0ff", muted="#6c7fa3", acc="#4f8cff", acc2="#7ee0c3"),
      light=dict(bg="#f4f7fc", bg2="#e0e7f5", ink="#0b1a33", muted="#4b5d80", acc="#1f4fd6", acc2="#0e8f6a"),
      hero=dict(type="plain", font="mono", name_size=50,
                back=[("hexgrid", dict(size=18, op=0.08)), ("blocks", dict(n=8, y0=14, size=34))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="chain", font="mono"),
      labels=dict(public="block: public", stack="block: stack", snake="block: activity"),
      signoff="chain intact",
      text=dict(rows="numbered", chip="code", fence="json", alert="NOTE", sep="->")),

    T("crt", "CRT", "tech", "Phosphor green behind curved glass. It flickers a little.",
      dark=dict(bg="#061006", bg2="#0b1c0b", ink="#b8ffb8", muted="#4f9a4f", acc="#35ff5a", acc2="#9dff9d"),
      light=dict(bg="#eaf6e4", bg2="#cfe6c6", ink="#0b2e12", muted="#3c6b47", acc="#157a2e", acc2="#3aa653"),
      hero=dict(type="glow", font="mono", name_size=50, cursor=True,
                back=[("scanlines", dict(spacing=3, op=0.16))],
                front=[("vignette", dict(strength=0.65)), ("frame", dict(inset=6, w=3, rx=18, op=0.6))]),
      header=dict(style="glow", font="mono"),
      labels=dict(public="> public", stack="> stack", snake="> activity"),
      signoff="NO SIGNAL",
      text=dict(rows="list", chip="code", fence="bash", alert="TIP", sep=">")),

    T("matrix", "Matrix", "tech", "Data rain. The name sits on a dark plate so it stays readable.",
      dark=dict(bg="#000000", bg2="#02130a", ink="#d8ffe0", muted="#3f8f5c", acc="#00ff66", acc2="#b6ffcf"),
      light=dict(bg="#f1f7f2", bg2="#d9e9dc", ink="#062814", muted="#3e6a4e", acc="#0a7a3e", acc2="#59b37f"),
      hero=dict(type="glow", font="mono", name_size=50, shade=False,
                back=[("datarain", dict(cols=30))],
                device=dict(dark=("plate", dict(colour="#000000", op=0.72, w=640)), light=("plate", dict(colour="#f1f7f2", op=0.86, w=640)))),
      header=dict(style="glow", font="mono", index="hex"),
      labels=dict(public="public", stack="stack", snake="activity"),
      signoff="there is no spoon",
      text=dict(rows="list", chip="code", fence="diff", alert="TIP", sep="|")),

    T("synthwave", "Synthwave", "tech", "Sun on the horizon, grid rolling toward you, eighties gradients.",
      dark=dict(bg="#12062b", bg2="#33104f", ink="#ffe9ff", muted="#b07cc9", acc="#ff4fa3", acc2="#21d7ff"),
      light=dict(bg="#fff1f7", bg2="#ffd3e6", ink="#2b0a3d", muted="#8a5a9a", acc="#d61a6c", acc2="#0b83c9"),
      hero=dict(type="glow", font="sans", case="upper", ls=3, name_size=50, reserve=200,
                back=[("stars", dict(n=50, region=(0, 0, 1, 0.5))), ("vapor_sun", dict(cx=740, cy=112, r=68, colours=["#ffb347", "#ff3d7f"])),
                      ("grid_floor", dict(horizon=0.6))]),
      header=dict(style="glow", font="sans", case="upper", ls=3),
      labels=dict(public="public", stack="stack", snake="activity"),
      signoff="DRIVE SAFE",
      text=dict(rows="table", chip="kbd", fence="toml", alert="TIP", sep="~")),

    T("datacenter", "Datacenter", "tech", "Rack rails and a wall of blinking LEDs. Nothing glamorous, everything up.",
      dark=dict(bg="#0b0f14", bg2="#161d26", ink="#e6edf3", muted="#7d8b99", acc="#3ddc84", acc2="#58a6ff"),
      light=dict(bg="#f6f8fa", bg2="#e1e7ee", ink="#0d1117", muted="#57606a", acc="#1a7f37", acc2="#0969da"),
      hero=dict(type="plain", font="mono", name_size=48, reserve=340,
                back=[("rack", dict(rows=4, cols=16, region=(0.6, 0.04, 0.4, 0.92)))],
                device=dict(light=("rail", dict(side="left", w=14, colour="#0d1117")))),
      header=dict(style="rule", font="mono", ornament="block"),
      labels=dict(public="rack: public", stack="rack: stack", snake="rack: activity"),
      signoff="lights out",
      text=dict(rows="table", chip="code", fence="yaml", alert="NOTE", sep="|")),

    T("hologram", "Hologram", "tech", "Blue projection with slice glitches and a scan band.",
      dark=dict(bg="#030a14", bg2="#071d33", ink="#dff6ff", muted="#5f8fb0", acc="#35c8ff", acc2="#8effff"),
      light=dict(bg="#eef8ff", bg2="#d2e8fa", ink="#06243d", muted="#3f6d8f", acc="#0a78c2", acc2="#0aa0d8"),
      hero=dict(type="glow", font="sans", ls=1,
                back=[("hexgrid", dict(size=20, op=0.1)), ("glow_spot", dict(cx=450, cy=262, r=330, op=0.45)), ("scanlines", dict(op=0.05))],
                front=[("glitch_bars", dict(n=7))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="glow", font="sans"),
      labels=dict(public="holo: public", stack="holo: stack", snake="holo: activity"),
      signoff="end projection",
      text=dict(rows="list", chip="kbd", fence="json", alert="NOTE", sep="/")),

    T("radar", "Radar", "tech", "A sweep finds four contacts. Green on near-black.",
      dark=dict(bg="#04140b", bg2="#082418", ink="#dcffe9", muted="#4f9370", acc="#4dff9e", acc2="#b8ffd6"),
      light=dict(bg="#eff7f1", bg2="#d6e8db", ink="#072415", muted="#3a6b4f", acc="#0d7a45", acc2="#0f9f5b"),
      hero=dict(type="plain", font="mono", name_size=48, reserve=270,
                back=[("speckle", dict(n=140, op=0.12)), ("ticks", dict(every=30, y=8)), ("radar", dict(cx=752, cy=120, rad=104))]),
      header=dict(style="bracket", font="mono", index="bracket"),
      labels=dict(public="contact: public", stack="contact: stack", snake="contact: activity"),
      signoff="sweep complete",
      text=dict(rows="table", chip="code", fence="ini", alert="NOTE", sep="::")),

    T("mech", "Mech", "tech", "Armour plates, hex bolts, a piston, warning amber. Robotic.",
      dark=dict(bg="#101214", bg2="#1d2126", ink="#eef0f2", muted="#8a929c", acc="#ffb000", acc2="#4fd1ff"),
      light=dict(bg="#eceff3", bg2="#d3d9e2", ink="#12171d", muted="#4d5866", acc="#c77800", acc2="#0b7fb6"),
      hero=dict(type="stencil", font="sans", case="upper", ls=2, name_size=48, reserve=330,
                back=[("panels", {})],
                front=[("hazard", dict(y=224, h=16, stripe=12))]),
      header=dict(style="hazard", font="sans", case="upper", ls=2),
      labels=dict(public="unit: public", stack="unit: stack", snake="unit: activity"),
      signoff="SERVO IDLE",
      text=dict(rows="tasks", chip="kbd", fence="toml", alert="TIP", sep="+")),

    T("mainframe", "Mainframe", "tech", "Punch cards and green-bar paper. Batch job complete.",
      dark=dict(bg="#0d1a12", bg2="#13271b", ink="#dfe9d3", muted="#7d9a78", acc="#9ee493", acc2="#e2c98c"),
      light=dict(bg="#f4f7ec", bg2="#e0ead0", ink="#1d2a1c", muted="#5b6f58", acc="#2f7a3a", acc2="#8a6d2b"),
      hero=dict(type="plain", font="mono", name_size=50,
                back=[("blinds", dict(n=8, angle=0, op=0.07)), ("punchcard", dict(region=(0.55, 0.05, 0.45, 0.9)))]),
      header=dict(style="rule", font="mono", case="upper", ornament="block"),
      labels=dict(public="job public", stack="job stack", snake="job activity"),
      signoff="END OF JOB",
      text=dict(rows="numbered", chip="code", fence="ini", alert="NOTE", sep="..")),

    T("signal", "Signal", "tech", "An oscilloscope trace rolling under the name.",
      dark=dict(bg="#060a12", bg2="#0c1628", ink="#e8f1ff", muted="#6b83a6", acc="#ffc94a", acc2="#7aa2ff"),
      light=dict(bg="#f5f7fb", bg2="#e0e6f2", ink="#0c1a33", muted="#4c5f80", acc="#b3720b", acc2="#2f5fd0"),
      hero=dict(type="plain", font="mono", name_size=50,
                back=[("hexgrid", dict(size=20, op=0.08)), ("ticks", dict(every=30, y=8))],
                front=[("oscilloscope", dict(yy=206, amp=14, period=96))]),
      header=dict(style="rule", font="mono", ornament="wave"),
      labels=dict(public="channel: public", stack="channel: stack", snake="channel: activity"),
      signoff="signal lost",
      text=dict(rows="list", chip="code", fence="hcl", alert="NOTE", sep="~")),

    T("pixel", "Pixel", "tech", "Eight-bit skies, a block floor, a blinking star field.",
      dark=dict(bg="#0d0d1a", bg2="#1a1a3a", ink="#f0f0ff", muted="#8383a8", acc="#ffd23f", acc2="#4dd0ff"),
      light=dict(bg="#f4f4ff", bg2="#d8dcf5", ink="#14143a", muted="#55558a", acc="#a86600", acc2="#0a8fd0"),
      hero=dict(type="plain", font="mono", name_size=50,
                back=[("pixels", {})]),
      header=dict(style="rule", font="mono", case="upper", ornament="block"),
      labels=dict(public="level public", stack="level stack", snake="bonus stage"),
      signoff="CONTINUE?",
      text=dict(rows="tasks", chip="kbd", fence="json", alert="TIP", sep="+")),

    # ---------------------------------------------------------------- NATURE
    T("monsoon", "Monsoon", "nature", "Rain in three depths under a streetlamp. At noon, an overcast sky.",
      dark=dict(bg="#05080f", bg2="#0c1424", ink="#e8eefc", muted="#7d8cb0", acc="#ffb347", acc2="#8ab4ff"),
      light=dict(bg="#dfe6ee", bg2="#c3cfdc", ink="#10203a", muted="#48587a", acc="#1f5fbf", acc2="#41628f"),
      hero=dict(type="plain", font="sans", reserve=120,
                back=[("lamp_post", dict(x0=800, dark=dict(colour="#1a2236", light="#ffb347"), light=dict(colour="#2b3a52", light="#ffd27a"))),
                      ("clouds", dict(n=5, layers=2, dark=dict(op=0.35), light=dict(op=0.85)))],
                mid=[("rain", dict(layers=3, dark=dict(base_op=0.55), light=dict(base_op=0.45)))],
                front=[("fog", dict(y=176, h=70, op=0.16)), ("horizon", dict(yy=228, glow=True))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="drop"),
      labels=dict(public="what is public", stack="the stack", snake="the rain gauge"),
      signoff="rain check",
      text=dict(rows="quotes", chip="plain", fence="yaml", alert="NOTE", sep="/")),

    T("frost", "Frost", "nature", "A low moon, snow at three depths, fog drifting over a white ridge.",
      dark=dict(bg="#040c1c", bg2="#0e2140", ink="#eef6ff", muted="#8aa3c6", acc="#9fd3ff", acc2="#ffffff"),
      light=dict(bg="#f6fbff", bg2="#dbeaf8", ink="#0d2440", muted="#4e6a8a", acc="#1b6fd1", acc2="#5aa9ff"),
      hero=dict(type="plain", font="sans", reserve=160,
                back=[("stars", dict(n=45, region=(0, 0, 1, 0.55), dark=dict(), light=dict(skip=True))),
                      ("moon", dict(cx=772, cy=70, r=34, glow=0.5)),
                      ("mountains", dict(layers=2, snowline=True, dark=dict(colour="#17304f"), light=dict(colour="#9fb9d4")))],
                mid=[("fog", dict(y=140, h=80, op=0.2)), ("snow", dict(layers=3))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="flake"),
      labels=dict(public="what is public", stack="the stack", snake="the snowfield"),
      signoff="stay warm",
      text=dict(rows="list", chip="plain", fence="yaml", alert="NOTE", sep="+")),

    T("forest", "Forest", "nature", "Pines in two depths, light shafts, fireflies after dusk.",
      dark=dict(bg="#04110a", bg2="#0b2416", ink="#e6f4e8", muted="#7aa287", acc="#62d98a", acc2="#f6ff9a"),
      light=dict(bg="#eef7ea", bg2="#cfe6c4", ink="#0e2a16", muted="#4b6e55", acc="#1c7a3c", acc2="#c99a12"),
      hero=dict(type="plain", font="sans",
                back=[("light_shafts", dict(n=4)), ("trees", dict(n=28, layers=2, dark=dict(colour="#0f2e1c"), light=dict(colour="#3f7a4f")))],
                front=[("fireflies", dict(n=12, dark=dict(), light=dict(skip=True))), ("fog", dict(y=190, h=60, op=0.12))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="leaf"),
      labels=dict(public="in the open", stack="the stack", snake="the undergrowth"),
      signoff="keep growing",
      text=dict(rows="quotes", chip="plain", fence="yaml", alert="TIP", sep="~")),

    T("desert", "Desert", "nature", "Dunes at night under a crescent; midday glare in light mode.",
      dark=dict(bg="#0f0a1a", bg2="#2c1224", ink="#ffe9d6", muted="#a88a82", acc="#ff9a3c", acc2="#ffd9a0"),
      light=dict(bg="#fff3dc", bg2="#f6d59f", ink="#3a2208", muted="#8a6a3a", acc="#c96a12", acc2="#e8a63d"),
      hero=dict(type="plain", font="sans", reserve=120,
                back=[("stars", dict(n=40, region=(0, 0, 1, 0.5), dark=dict(), light=dict(skip=True))),
                      ("moon", dict(cx=780, cy=64, r=30, glow=0.35, dark=dict(), light=dict(skip=True))),
                      ("sun", dict(cx=780, cy=64, r=30, rays=14, glow=0.5, dark=dict(skip=True), light=dict())),
                      ("dunes", dict(layers=3, dark=dict(colour="#6b3a2a"), light=dict(colour="#d9a45a")))],
                front=[("dust", dict(n=40, op=0.35))]),
      header=dict(style="rule", font="sans", ornament="sun"),
      labels=dict(public="visible from the road", stack="the stack", snake="tracks in the sand"),
      signoff="keep moving",
      text=dict(rows="list", chip="plain", fence="toml", alert="TIP", sep="..")),

    T("aurora", "Aurora", "nature", "Curtains of green and violet over a black ridge.",
      dark=dict(bg="#030914", bg2="#082036", ink="#eaf7ff", muted="#7d9fb8", acc="#4dffb0", acc2="#b36bff"),
      light=dict(bg="#edf6fb", bg2="#cfe5f3", ink="#072238", muted="#3f6580", acc="#0e8f5f", acc2="#6c3fc9"),
      hero=dict(type="plain", font="sans",
                back=[("stars", dict(n=70, region=(0, 0, 1, 0.7))), ("aurora", dict(curtains=4)),
                      ("mountains", dict(layers=1, snowline=False, dark=dict(colour="#061421"), light=dict(colour="#5f7e9a")))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="star"),
      labels=dict(public="what is public", stack="the stack", snake="night sky"),
      signoff="northern lights",
      text=dict(rows="list", chip="plain", fence="yaml", alert="TIP", sep="+")),

    T("abyss", "Abyss", "nature", "Bubbles rising through deep water, bioluminescence drifting past.",
      dark=dict(bg="#01060d", bg2="#042138", ink="#d9f1ff", muted="#5c8ea9", acc="#21d0ff", acc2="#7bffe0"),
      light=dict(bg="#e7f4fb", bg2="#bcdcee", ink="#052a40", muted="#386884", acc="#0a6fa6", acc2="#0f9c8e"),
      hero=dict(type="glow", font="sans",
                back=[("light_shafts", dict(n=3, op=0.12)), ("bubbles", dict(n=34))],
                front=[("fireflies", dict(n=9, dark=dict(colour="#7bffe0"), light=dict(skip=True)))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="wave"),
      labels=dict(public="what is public", stack="the stack", snake="deep water"),
      signoff="surface when ready",
      text=dict(rows="quotes", chip="plain", fence="json", alert="NOTE", sep="~")),

    T("sunny", "Sunny", "nature", "Golden hour after dark; full noon in light mode with rays turning.",
      dark=dict(bg="#1f0f05", bg2="#5a2c08", ink="#fff1dc", muted="#c9a070", acc="#ffb020", acc2="#ff6a2a"),
      light=dict(bg="#fff9e6", bg2="#ffe08a", ink="#3d2200", muted="#7a5a1a", acc="#c25a00", acc2="#f5b400"),
      hero=dict(type=dict(dark="plain", light="plate"), font="sans", reserve=200,
                back=[("sun", dict(cx=746, cy=118, r=46, rays=16, glow=0.6, dark=dict(), light=dict(colour="#ff9a1f")))]),
      header=dict(style="rule", font="sans", ornament="sun"),
      labels=dict(public="what is public", stack="the stack", snake="daylight"),
      signoff="have a good one",
      text=dict(rows="list", chip="plain", fence="toml", alert="TIP", sep="-")),

    T("cloudy", "Cloudy", "nature", "Two layers of cloud drifting, one break of warm light behind them.",
      dark=dict(bg="#1a1f2b", bg2="#2f384c", ink="#e7ebf3", muted="#97a1b6", acc="#9fb3d9", acc2="#ffd27a"),
      light=dict(bg="#f0f3f7", bg2="#cbd3df", ink="#1b2433", muted="#5a6577", acc="#3b5b8c", acc2="#c48a1a"),
      hero=dict(type="plain", font="sans",
                back=[("glow_spot", dict(cx=640, cy=250, r=300, colour="#ffd27a", op=0.35)), ("clouds", dict(n=6, layers=2))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="cloud"),
      labels=dict(public="what is public", stack="the stack", snake="weather"),
      signoff="clearing later",
      text=dict(rows="table", chip="plain", fence="yaml", alert="NOTE", sep="|")),

    T("storm", "Storm", "nature", "Rain driven sideways, lightning that fires when it feels like it.",
      dark=dict(bg="#05070d", bg2="#131b2e", ink="#e6ebf5", muted="#7f8aa6", acc="#b7c8ff", acc2="#eaf6ff"),
      light=dict(bg="#dfe4ec", bg2="#b6c1d3", ink="#0e1626", muted="#45516a", acc="#2b4a9e", acc2="#4a6bd6"),
      hero=dict(type="plain", font="sans",
                back=[("clouds", dict(n=6, layers=2, dark=dict(op=0.6), light=dict(colour="#8f9db5", op=0.8)))],
                mid=[("rain", dict(layers=2, angle=18, base_op=0.4)), ("lightning", dict(bolts=2))],
                device=dict(light=("rail", dict(side="left", w=14, colour="#0e1626")))),
      header=dict(style="rule", font="sans", ornament="bolt"),
      labels=dict(public="what is public", stack="the stack", snake="the forecast"),
      signoff="weather it",
      text=dict(rows="list", chip="plain", fence="diff", alert="NOTE", sep="/")),

    T("mountain", "Mountain", "nature", "Three ridges, a snowline, mist in the valley.",
      dark=dict(bg="#0a1220", bg2="#1d2f4d", ink="#edf3ff", muted="#8ea0be", acc="#cfe3ff", acc2="#ffb36b"),
      light=dict(bg="#eef4fb", bg2="#c9dcf0", ink="#10233b", muted="#4a6382", acc="#2f5c9c", acc2="#c9741c"),
      hero=dict(type="plain", font="sans",
                back=[("stars", dict(n=30, region=(0, 0, 1, 0.4), dark=dict(), light=dict(skip=True))),
                      ("sun", dict(cx=700, cy=60, r=22, glow=0.4, dark=dict(skip=True), light=dict(colour="#f2b04a"))),
                      ("mountains", dict(layers=3, snowline=True, dark=dict(colour="#1b2c48"), light=dict(colour="#7f97b8")))],
                front=[("fog", dict(y=150, h=56, op=0.22))]),
      header=dict(style="rule", font="sans", ornament="mountain"),
      labels=dict(public="what is public", stack="the stack", snake="the climb"),
      signoff="keep climbing",
      text=dict(rows="list", chip="plain", fence="yaml", alert="NOTE", sep="/")),

    T("sakura", "Sakura", "nature", "Petals drifting under a spring moon.",
      dark=dict(bg="#1a0a1f", bg2="#361336", ink="#ffe9f2", muted="#b98aaa", acc="#ff9ac8", acc2="#ffd6e6"),
      light=dict(bg="#fff4f8", bg2="#ffd2e2", ink="#3a1030", muted="#8a5a78", acc="#d63c7a", acc2="#ff8fb9"),
      hero=dict(type="plain", font="sans", reserve=120,
                back=[("moon", dict(cx=780, cy=66, r=30, glow=0.4, dark=dict(), light=dict(skip=True)))],
                mid=[("petals", dict(n=28))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="dot"),
      labels=dict(public="what is public", stack="the stack", snake="in bloom"),
      signoff="petals fall",
      text=dict(rows="quotes", chip="plain", fence="yaml", alert="TIP", sep="-")),

    T("autumn", "Autumn", "nature", "Leaves turning and falling through warm light.",
      dark=dict(bg="#1a0f06", bg2="#33190a", ink="#ffe9cf", muted="#b8936a", acc="#ff8a2a", acc2="#ffc857"),
      light=dict(bg="#fff4e6", bg2="#f8d29a", ink="#3a1e05", muted="#8a5a2a", acc="#c6521a", acc2="#d9931a"),
      hero=dict(type="plain", font="sans",
                back=[("light_shafts", dict(n=3, op=0.14))],
                mid=[("petals", dict(n=26, shape="leaf"))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="leaf"),
      labels=dict(public="what is public", stack="the stack", snake="falling leaves"),
      signoff="season's turning",
      text=dict(rows="list", chip="plain", fence="toml", alert="TIP", sep="~")),

    T("ocean", "Ocean", "nature", "Three swells rolling under a moon; bright water by day.",
      dark=dict(bg="#031424", bg2="#053250", ink="#e5f6ff", muted="#6fa3bd", acc="#2fb8ff", acc2="#9ff0ff"),
      light=dict(bg="#e8f6fb", bg2="#b6dbec", ink="#05304a", muted="#3d7590", acc="#0a78b8", acc2="#22b4c8"),
      hero=dict(type="plain", font="sans", reserve=120,
                back=[("stars", dict(n=30, region=(0, 0, 1, 0.45), dark=dict(), light=dict(skip=True))),
                      ("moon", dict(cx=780, cy=64, r=28, glow=0.4, crescent=False, dark=dict(), light=dict(skip=True))),
                      ("sun", dict(cx=780, cy=64, r=26, rays=0, glow=0.5, dark=dict(skip=True), light=dict(colour="#f7c948")))],
                front=[("waves", dict(layers=3, amp=6, y_frac=0.84))]),
      header=dict(style="rule", font="sans", ornament="wave"),
      labels=dict(public="what is public", stack="the stack", snake="the tide"),
      signoff="tide's out",
      text=dict(rows="list", chip="plain", fence="yaml", alert="NOTE", sep="~")),

    T("glacier", "Glacier", "nature", "Ice crystals catching light. Cold blue, very still.",
      dark=dict(bg="#041420", bg2="#0b2f44", ink="#eafaff", muted="#7fb0c4", acc="#7fe3ff", acc2="#cfffff"),
      light=dict(bg="#edfbff", bg2="#c4ebf8", ink="#063040", muted="#3f7a8f", acc="#0a8fb8", acc2="#38c6ea"),
      hero=dict(type="glow", font="sans", reserve=220,
                back=[("crystals", dict(n=12, region=(0.6, 0, 0.4, 1)))],
                mid=[("snow", dict(layers=1, density=0.6))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="flake"),
      labels=dict(public="what is public", stack="the stack", snake="ice core"),
      signoff="frozen solid",
      text=dict(rows="list", chip="plain", fence="json", alert="NOTE", sep="+")),

    # ------------------------------------------------------------- ELEMENTAL
    T("lava", "Lava", "elemental", "Cracks glowing through cooled basalt. Sparks rising.",
      dark=dict(bg="#0b0605", bg2="#1f0c09", ink="#ffe6d6", muted="#b0837a", acc="#ff4d1a", acc2="#ffb347"),
      light=dict(bg="#f7e8e2", bg2="#e6bfae", ink="#2e0d06", muted="#7a4a3a", acc="#c83a0e", acc2="#d9781a"),
      hero=dict(type="glow", font="sans",
                back=[("strata", dict(bands=5, jag=8, dark=dict(colour="#1d0e0c"), light=dict(colour="#d9b3a5"))),
                      ("lava", dict(cracks=7))],
                front=[("embers", dict(n=24))],
                device=dict(light=("band", dict(y=224, h=16)))),
      header=dict(style="glow", font="sans", ornament="flame"),
      labels=dict(public="what is public", stack="the stack", snake="still cooling"),
      signoff="stay cool",
      text=dict(rows="list", chip="plain", fence="diff", alert="NOTE", sep="-")),

    T("space", "Space", "elemental", "A ringed planet, a nebula wash, stars out of phase.",
      dark=dict(bg="#02040c", bg2="#080f2a", ink="#eef2ff", muted="#8390bd", acc="#8ea6ff", acc2="#ff8ad6"),
      light=dict(bg="#eef1fb", bg2="#d3d9f3", ink="#0d1440", muted="#4a5586", acc="#3a4ed6", acc2="#c2338f"),
      hero=dict(type="plain", font="sans", reserve=260,
                back=[("nebula", dict(blobs=4)), ("stars", dict(n=110)), ("planet", dict(cx=772, cy=150, r=68, ring=True))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="star"),
      labels=dict(public="what is public", stack="the stack", snake="orbit"),
      signoff="see you in orbit",
      text=dict(rows="list", chip="code", fence="json", alert="NOTE", sep="+")),

    T("granite", "Granite", "elemental", "Rock strata and grain. The only theme with no motion at all.",
      dark=dict(bg="#15161a", bg2="#26282e", ink="#e9eaee", muted="#9a9da6", acc="#c9ccd4", acc2="#b0b6c4"),
      light=dict(bg="#eeeff2", bg2="#d3d6dd", ink="#1b1d22", muted="#5b606b", acc="#3a3f4b", acc2="#7d8494"),
      hero=dict(type="plain", font="sans", ls=1,
                back=[("strata", dict(bands=7, jag=5))],
                device=dict(light=("band", dict(y=224, h=16, colour="#1b1d22")))),
      header=dict(style="rule", font="sans", ornament="diamond"),
      labels=dict(public="what is public", stack="the stack", snake="bedrock"),
      signoff="set in stone",
      text=dict(rows="table", chip="plain", fence="ini", alert="NOTE", sep="|")),

    T("toxic", "Toxic", "elemental", "Acid drips and hazard stripes. Wash your hands.",
      dark=dict(bg="#060b06", bg2="#0f1f0d", ink="#eaffde", muted="#8bb07a", acc="#a6ff2f", acc2="#ffe83a"),
      light=dict(bg="#f2fae9", bg2="#d6ecbd", ink="#16300a", muted="#4f6e3a", acc="#3f7d00", acc2="#c6a800"),
      hero=dict(type="glow", font="sans", case="upper", ls=2, name_size=50,
                back=[("drips", dict(n=9))],
                front=[("hazard", dict(y=224, h=16, stripe=12))]),
      header=dict(style="hazard", font="sans", case="upper", ls=2),
      labels=dict(public="hazmat: public", stack="hazmat: stack", snake="hazmat: activity"),
      signoff="wash your hands",
      text=dict(rows="tasks", chip="kbd", fence="diff", alert="NOTE", sep="+")),

    T("ember", "Ember", "elemental", "The last of a fire. Sparks lifting off into the dark.",
      dark=dict(bg="#0d0705", bg2="#26120a", ink="#ffe9d9", muted="#b08a76", acc="#ff7a1a", acc2="#ffd07a"),
      light=dict(bg="#fff1e6", bg2="#f6c9a4", ink="#3b1a08", muted="#8a5a3a", acc="#d24e0e", acc2="#e79a2e"),
      hero=dict(type="plain", font="sans",
                back=[("glow_spot", dict(cx=450, cy=270, r=360, op=0.55))],
                mid=[("embers", dict(n=40))],
                front=[("vignette", dict(strength=0.4))],
                device=dict(light=("band", dict(y=224, h=16)))),
      header=dict(style="rule", font="sans", ornament="flame"),
      labels=dict(public="what is public", stack="the stack", snake="the last light"),
      signoff="stay lit",
      text=dict(rows="list", chip="plain", fence="toml", alert="TIP", sep="-")),

    T("lunar", "Lunar", "elemental", "Craters, a grey horizon, Earth small in the sky.",
      dark=dict(bg="#05070c", bg2="#0f131c", ink="#eef0f5", muted="#8d94a4", acc="#d8dce6", acc2="#7fb6ff"),
      light=dict(bg="#eceef3", bg2="#cdd2dc", ink="#151a26", muted="#545b6b", acc="#3d4a63", acc2="#1e5fb3"),
      hero=dict(type="plain", font="sans", reserve=100,
                back=[("stars", dict(n=60, region=(0, 0, 1, 0.7), dark=dict(), light=dict(skip=True))),
                      ("planet", dict(cx=790, cy=56, r=22, colour="#2f7bd6")),
                      ("band", dict(y=202, h=38, dark=dict(colour="#262a33"), light=dict(colour="#aeb4c2"))),
                      ("craters", dict(n=14, y_from=0.86, dark=dict(colour="#262a33"), light=dict(colour="#aeb4c2")))]),
      header=dict(style="rule", font="sans", ornament="moon"),
      labels=dict(public="what is public", stack="the stack", snake="footprints"),
      signoff="one small step",
      text=dict(rows="list", chip="plain", fence="ini", alert="NOTE", sep="..")),

    T("eclipse", "Eclipse", "elemental", "A black disc and its corona. Everything else goes quiet.",
      dark=dict(bg="#04040a", bg2="#0d0a1e", ink="#f3efff", muted="#8f88ad", acc="#ffd28a", acc2="#c9b6ff"),
      light=dict(bg="#f3f0fb", bg2="#dcd5f2", ink="#170f33", muted="#5a5080", acc="#b87a12", acc2="#5b3fc9"),
      hero=dict(type="plain", font="sans", reserve=220,
                back=[("stars", dict(n=50, dark=dict(), light=dict(skip=True))), ("eclipse", dict(cx=760, cy=118, r=64))],
                device=dict(light=("rail", dict(side="left", w=14)))),
      header=dict(style="rule", font="sans", ornament="moon"),
      labels=dict(public="what is public", stack="the stack", snake="totality"),
      signoff="light returns",
      text=dict(rows="quotes", chip="plain", fence="text", alert="NOTE", sep="|")),

    # ------------------------------------------------------- GRITTY / CINEMA
    T("war", "War", "gritty", "Stencil caps, hazard chevrons, sitrep numbering.",
      dark=dict(bg="#0f1108", bg2="#1f2312", ink="#e8e6d6", muted="#9e9b80", acc="#d8b23a", acc2="#b8c0a0"),
      light=dict(bg="#ecebdf", bg2="#d1cdb0", ink="#1b1c10", muted="#5c5b44", acc="#a0741b", acc2="#4a5a2a"),
      hero=dict(type="stencil", font="sans", case="upper", ls=3, name_size=48,
                back=[("speckle", dict(n=200, op=0.12)), ("scratches", dict(n=12))],
                front=[("hazard", dict(y=224, h=16, stripe=14)), ("chevrons", dict(y=60, n=5, size=16))]),
      header=dict(style="hazard", font="sans", case="upper", ls=2, index="hash"),
      labels=dict(public="sitrep: public", stack="loadout", snake="the front"),
      signoff="OVER AND OUT",
      text=dict(rows="tasks", chip="kbd", fence="ini", alert="NOTE", sep="//")),

    T("survival", "Survival", "gritty", "Riveted plate, rust bloom, scratches. Still here.",
      dark=dict(bg="#141210", bg2="#28211a", ink="#efe6d8", muted="#a8977f", acc="#d9772a", acc2="#b7c9a0"),
      light=dict(bg="#efe9df", bg2="#d3c5ad", ink="#2b2117", muted="#6e5e4c", acc="#b05a1a", acc2="#3f5a2a"),
      hero=dict(type="stencil", font="sans", case="upper", ls=2, name_size=48,
                back=[("rust", dict(n=6)), ("scratches", dict(n=16))],
                front=[("rivets", {})],
                device=dict(light=("frame", dict(inset=6, w=6, op=0.9)))),
      header=dict(style="ribbon", font="sans", case="upper", ls=1),
      labels=dict(public="what is public", stack="the kit", snake="the trail"),
      signoff="still here",
      text=dict(rows="tasks", chip="plain", fence="bash", alert="TIP", sep="+")),

    T("timber", "Timber", "gritty", "Wood grain and two knots. No technology in it at all.",
      dark=dict(bg="#1c120b", bg2="#33200f", ink="#f3e6d3", muted="#b39a7c", acc="#e0a25c", acc2="#8fbf6a"),
      light=dict(bg="#f6ead6", bg2="#dfbf8c", ink="#3a2410", muted="#7a5a38", acc="#8c4a1c", acc2="#4a7a2a"),
      hero=dict(type="plain", font="serif", name_size=54,
                back=[("woodgrain", dict(lines=22, knots=2))]),
      header=dict(style="rule", font="serif", ornament="leaf"),
      labels=dict(public="what is public", stack="the workbench", snake="the rings"),
      signoff="measure twice",
      text=dict(rows="quotes", chip="plain", fence="makefile", alert="TIP", sep="-")),

    T("noir", "Noir", "gritty", "Venetian blinds, film grain, pure greyscale.",
      dark=dict(bg="#08080a", bg2="#161618", ink="#f2f2f2", muted="#9a9a9f", acc="#e6e6e6", acc2="#c8c8c8"),
      light=dict(bg="#f4f4f4", bg2="#d6d6d6", ink="#101012", muted="#55555a", acc="#202024", acc2="#6a6a70"),
      hero=dict(type="plain", font="serif", name_size=54,
                back=[("blinds", dict(n=7, angle=-12))],
                front=[("speckle", dict(n=300, op=0.1, rmax=0.9)), ("vignette", dict(strength=0.6))],
                device=dict(light=("band", dict(y=224, h=16, colour="#101012")))),
      header=dict(style="rule", font="serif"),
      labels=dict(public="what is public", stack="the evidence", snake="the case file"),
      signoff="fade to black",
      text=dict(rows="quotes", chip="plain", fence="text", alert="NOTE", sep="|")),

    T("wasteland", "Wasteland", "gritty", "Cracked earth, dust on the wind, a dim sun. The road goes on.",
      dark=dict(bg="#1a1410", bg2="#2e231a", ink="#efe4d2", muted="#a8967e", acc="#e0a15a", acc2="#b9b59a"),
      light=dict(bg="#f1e6d2", bg2="#d6bf98", ink="#2e2010", muted="#75603f", acc="#b86a1e", acc2="#6b6a4a"),
      hero=dict(type="plain", font="sans", case="upper", ls=2, name_size=48,
                back=[("sun", dict(cx=740, cy=70, r=24, glow=0.3, dark=dict(colour="#d97b3a"), light=dict(colour="#e0a15a"))),
                      ("horizon", dict(yy=166, glow=False)), ("cracked_earth", dict(y0=170, n=16))],
                mid=[("dust", dict(n=60))],
                front=[("scratches", dict(n=8))],
                device=dict(light=("band", dict(y=224, h=16, colour="#2e2010")))),
      header=dict(style="rule", font="sans", case="upper", ls=1, ornament="sun"),
      labels=dict(public="what is public", stack="salvage", snake="the road"),
      signoff="keep walking",
      text=dict(rows="list", chip="plain", fence="bash", alert="TIP", sep="..")),

    T("bunker", "Bunker", "gritty", "Concrete, rivets, a red beacon turning. Seal the door.",
      dark=dict(bg="#101214", bg2="#1c1f24", ink="#e6e9ec", muted="#8b929b", acc="#ff3b3b", acc2="#ffb000"),
      light=dict(bg="#e9ebee", bg2="#c9ced6", ink="#15181c", muted="#4f565f", acc="#c81e1e", acc2="#b57a00"),
      hero=dict(type="stencil", font="sans", case="upper", ls=3, name_size=48, reserve=140,
                back=[("speckle", dict(n=260, op=0.14)), ("beacon", dict(cx=800, cy=60, dur=4))],
                front=[("rivets", {}), ("hazard", dict(y=224, h=16, stripe=14, dark=dict(colour="#ffb000"), light=dict(colour="#b57a00")))]),
      header=dict(style="band", font="sans", case="upper", ls=2),
      labels=dict(public="sector: public", stack="sector: stack", snake="sector: activity"),
      signoff="SEAL THE DOOR",
      text=dict(rows="tasks", chip="kbd", fence="ini", alert="NOTE", sep="|")),

    T("western", "Western", "gritty", "A low sun over the mesa, a tumbleweed, sepia by day.",
      dark=dict(bg="#2a1206", bg2="#552910", ink="#ffe8c8", muted="#c09a6e", acc="#ff9d3a", acc2="#e6c48a"),
      light=dict(bg="#f5e9d0", bg2="#dcbe8c", ink="#3a230c", muted="#7f5f38", acc="#a8561a", acc2="#7a6a3a"),
      hero=dict(type="plain", font="serif", name_size=54,
                back=[("sun", dict(cx=700, cy=150, r=58, glow=0.5, rays=0, dark=dict(colour="#ff9d3a"), light=dict(colour="#e9a24a"))),
                      ("dunes", dict(layers=2, dark=dict(colour="#3a1c0c"), light=dict(colour="#b98a55")))],
                front=[("dust", dict(n=40, op=0.4)), ("tumbleweed", {})],
                device=dict(light=("frame", dict(inset=8, w=3, op=0.9)))),
      header=dict(style="rule", font="serif", ornament="star"),
      labels=dict(public="what is public", stack="the outfit", snake="the trail"),
      signoff="so long, partner",
      text=dict(rows="quotes", chip="plain", fence="bash", alert="TIP", sep="-")),

    T("steampunk", "Steampunk", "gritty", "Brass gears turning at three speeds, verdigris, engraved plates.",
      dark=dict(bg="#1a120a", bg2="#33220f", ink="#f4e6cf", muted="#b39a72", acc="#d4a24c", acc2="#7fb7a6"),
      light=dict(bg="#f3e9d8", bg2="#dfc79e", ink="#3a2612", muted="#7a5f3c", acc="#9a6a1e", acc2="#2f7a68"),
      hero=dict(type="plain", font="serif", name_size=54, reserve=250,
                back=[("speckle", dict(n=160, op=0.12)), ("gears", {})],
                front=[("rivets", dict(every=52))],
                device=dict(light=("frame", dict(inset=6, w=4, op=0.9)))),
      header=dict(style="plate", font="serif", index="roman"),
      labels=dict(public="Public Works", stack="The Engine", snake="The Boilers"),
      signoff="full steam ahead",
      text=dict(rows="numbered", chip="plain", fence="makefile", alert="TIP", sep="-")),

    T("vaporwave", "Vaporwave", "gritty", "A cut sun, a cyan grid, pastel everything.",
      dark=dict(bg="#1b0b3a", bg2="#43106a", ink="#ffe6ff", muted="#c39be0", acc="#ff6ad5", acc2="#6ef0ff"),
      light=dict(bg="#fff0fb", bg2="#dbe4ff", ink="#2a0f45", muted="#7d5a9a", acc="#d63fb0", acc2="#12a7c9"),
      hero=dict(type="split", font="sans", case="upper", ls=4, name_size=48, reserve=220,
                back=[("vapor_sun", dict(cx=746, cy=108, r=80, colours=["#ff6ad5", "#ffa86a"])), ("grid_floor", dict(horizon=0.64, glow=False))],
                front=[("halftone", dict(spacing=12, op=0.25, region=(0.5, 0, 0.5, 1)))],
                device=dict(light=("band", dict(y=224, h=16)))),
      header=dict(style="glow", font="sans", case="upper", ls=4),
      labels=dict(public="public", stack="stack", snake="activity"),
      signoff="AESTHETIC",
      text=dict(rows="table", chip="kbd", fence="css", alert="TIP", sep="~")),

    T("anamorphic", "Anamorphic", "gritty", "Letterbox bars and a horizontal lens flare. Cinema.",
      dark=dict(bg="#05070c", bg2="#0e1526", ink="#f1f4fa", muted="#8290ad", acc="#9fc4ff", acc2="#3f8cff"),
      light=dict(bg="#f3f1ec", bg2="#d5d0c4", ink="#15181f", muted="#5c6270", acc="#1f4fa8", acc2="#3f7fdf"),
      hero=dict(type="plain", font="sans", ls=1, name_size=52,
                back=[("stars", dict(n=40, dark=dict(), light=dict(skip=True))), ("flare", dict(yy=120))],
                front=[("vignette", dict(strength=0.5)), ("letterbox", dict(bar=26, dark=dict(colour="#000000"), light=dict(colour="#15181f")))]),
      header=dict(style="rule", font="sans", index="roman", ornament="diamond"),
      labels=dict(public="what is public", stack="the stack", snake="end credits"),
      signoff="fin.",
      text=dict(rows="quotes", chip="plain", fence="text", alert="NOTE", sep="|")),
]

LIGHT_ACCENT_FLOOR = 4.5   # WCAG AA for normal text
LIGHT_ACCENT_AIM = 7.0     # presence, not just legibility


def _enforce_light_accent(themes, floor=LIGHT_ACCENT_FLOOR, aim=LIGHT_ACCENT_AIM):
    """Darken light-variant accents until they carry real weight on a near-white page.

    Measured 2026-08-27 across all 47 themes: accent contrast averaged 10.7:1 on the
    dark variants and 5.1:1 on the light ones, with 21 of 47 below WCAG AA. That gap is
    why the light themes read as washed out next to the dark ones. The dark variants get
    presence from a glow against a deep ground; on white the only equivalent is ink
    density, so the accent has to go darker rather than lighter.

    Darkening toward black preserves hue and saturation, so a theme stays recognisably
    itself. Applied here rather than by hand-editing entries, so a new theme inherits it
    and cannot regress; check_readme.py R14 enforces the floor on what actually ships.
    """
    for t in themes:
        light = t["light"]
        for key in ("acc", "acc2"):
            base = light.get(key)
            if not base or contrast(base, light["bg"]) >= aim:
                continue
            for step in range(1, 41):
                cand = darken(base, step / 40.0)
                light[key] = cand
                if contrast(cand, light["bg"]) >= aim:
                    break
            if contrast(light[key], light["bg"]) < floor:
                raise AssertionError(
                    "%s light %s cannot reach %.1f:1 against %s"
                    % (t["slug"], key, floor, light["bg"]))


UNSAFE_SEPS = {"*", "_"}   # markdown emphasis characters; also read as footnote marks

SAFE_ALERTS = {"NOTE", "TIP"}

# GitHub renders WARNING, CAUTION and IMPORTANT with alarm styling: a warning triangle,
# a red or orange rule. The callout they wrap is the verification invitation, the single
# block on the page whose whole job is to build trust. A friendly "want to check whether
# any of this is real?" inside a red danger box reads as a problem report. Only the two
# informational callouts are allowed.
for _t in THEMES:
    _s = _t["text"].get("sep", "|")
    assert _s not in UNSAFE_SEPS, (
        "%s uses sep=%r; '*' and '_' are emphasis characters and read as footnote "
        "markers between the header links" % (_t["slug"], _s))
    _a = _t["text"].get("alert", "NOTE")
    assert _a in SAFE_ALERTS, (
        "%s uses [!%s]; the CTA callout must be NOTE or TIP" % (_t["slug"], _a))

_enforce_light_accent(THEMES)

BY_SLUG = {t["slug"]: t for t in THEMES}
ACTIVE = [t for t in THEMES if not t.get("disabled")]

assert len(BY_SLUG) == len(THEMES), "duplicate theme slug"
