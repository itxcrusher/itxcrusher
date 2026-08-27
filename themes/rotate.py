"""Which theme today? Deterministic, so a re-run on the same day is a no-op.

Modes
  daily          a date-seeded pick from the whole pool, never the same as yesterday
  weekly         one theme per ISO week
  seasonal       the pool is filtered by month first (northern hemisphere), then daily
  fixed:<slug>   always that theme

An explicit override (workflow_dispatch input, or PROFILE_THEME in the environment)
beats the mode. The stamp written into README.md records which one applied.
"""
import datetime
import hashlib

from .catalog import ACTIVE, BY_SLUG

MODE = "daily"
SALT = "itxcrusher-profile"

# Seasonal pools: tech themes are always eligible; nature ones follow the calendar.
SEASON_OF_MONTH = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
                   6: "summer", 7: "summer", 8: "monsoon", 9: "monsoon", 10: "autumn", 11: "autumn"}
SEASON_THEMES = {
    "winter": {"frost", "glacier", "aurora", "mountain", "lunar", "noir"},
    "spring": {"sakura", "forest", "cloudy", "sunny", "ocean", "meadow"},
    "summer": {"desert", "sunny", "ocean", "wasteland", "western", "lava", "ember"},
    "monsoon": {"monsoon", "storm", "cloudy", "abyss", "forest"},
    "autumn": {"autumn", "timber", "ember", "steampunk", "granite", "survival"},
}


def pool():
    return [t["slug"] for t in ACTIVE]


def _raw(date, slugs, salt=SALT):
    h = hashlib.sha256(("%s:%s" % (salt, date.isoformat())).encode()).hexdigest()
    return slugs[int(h, 16) % len(slugs)]


# A handful of days get their own small pool. Verified rather than invented: the
# account anniversary is github.com/itxcrusher's real created_at, 2022-04-12.
# Each pool is drawn from deterministically like any other day, so two consecutive
# Halloweens do not have to look the same. Add a date here and it just works.
SPECIAL_DAYS = {
    (10, 31): ("halloween", ["noir", "eclipse", "toxic", "wasteland"]),
    (12, 31): ("new-year", ["aurora", "space", "synthwave"]),
    (1, 1):   ("new-year", ["aurora", "space", "synthwave"]),
    (4, 12):  ("anniversary", ["crt", "pixel", "mainframe"]),
}


EPOCH = datetime.date(2026, 8, 1)
WINDOW = 7          # a theme cannot come back within a week


def _daily(date, slugs):
    """Simulate the draw from a fixed epoch so every day's pick is a pure function of
    the date and the pool: a date-seeded raw draw, moved to the next free slug when it
    fell inside the no-repeat window."""
    if date < EPOCH:
        return _raw(date, slugs)
    recent = []
    d = EPOCH
    while True:
        raw = _raw(d, slugs)
        i = slugs.index(raw)
        while slugs[i] in recent:
            i = (i + 1) % len(slugs)
        slug = slugs[i]
        if d == date:
            return slug
        recent.append(slug)
        recent = recent[-(min(WINDOW, len(slugs) - 1)):]
        d += datetime.timedelta(days=1)


def pick(date=None, mode=None, override=None):
    """Return (slug, mode_label)."""
    date = date or datetime.date.today()
    mode = mode or MODE
    slugs = pool()
    if override:
        if override not in BY_SLUG:
            raise SystemExit("unknown theme %r; known: %s" % (override, ", ".join(sorted(BY_SLUG))))
        return override, "override"
    special = SPECIAL_DAYS.get((date.month, date.day))
    if special and not mode.startswith("fixed:"):
        label, pool_ = special
        eligible = [s for s in pool_ if s in BY_SLUG and s in slugs]
        if eligible:
            return _raw(date, eligible), "special:" + label
    if mode.startswith("fixed:"):
        slug = mode.split(":", 1)[1]
        if slug not in BY_SLUG:
            raise SystemExit("unknown fixed theme %r" % slug)
        return slug, mode
    if mode == "weekly":
        iso = date.isocalendar()
        monday = datetime.date.fromisocalendar(iso[0], iso[1], 1)
        return _daily(monday, slugs), "weekly"
    if mode == "seasonal":
        season = SEASON_OF_MONTH[date.month]
        seasonal = [s for s in slugs if s in SEASON_THEMES[season] or BY_SLUG[s]["family"] == "tech"]
        return _daily(date, seasonal or slugs), "seasonal:" + season
    return _daily(date, slugs), "daily"


def schedule(start, days, mode=None):
    """The next N picks, for inspection."""
    out = []
    for i in range(days):
        d = start + datetime.timedelta(days=i)
        out.append((d.isoformat(), pick(d, mode)[0]))
    return out
