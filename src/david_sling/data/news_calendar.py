"""L2 data/news_calendar - deterministic high-impact economic calendar (G43).

Replaces the old random 2%-per-tick news flag with rule-based windows:
  - NFP: every Friday 12:30-14:00 UTC (first Friday of the month, approx)
  - CPI: monthly, weekday between the 8th and 15th, 12:30-14:00 UTC
  - FOMC: Wednesday 18:00-19:00 UTC, roughly mid-month (day 10-20)
  - config override: news.calendar_dates = ["2026-01-28 13:30", ...] in any yaml
"""
from __future__ import annotations

from datetime import datetime, timedelta

WINDOW = timedelta(minutes=30)


def is_high_impact(now: datetime, extra_dates: list[str] | None = None) -> bool:
    if now.tzinfo is None:
        from datetime import UTC

        now = now.replace(tzinfo=UTC)
    # explicit calendar entries first
    for item in extra_dates or []:
        try:
            ev = datetime.fromisoformat(item)
        except ValueError:
            continue
        if ev.tzinfo is None:
            from datetime import UTC

            ev = ev.replace(tzinfo=UTC)
        if abs(now - ev) <= WINDOW:
            return True
    wd = now.weekday()  # Mon=0 .. Sun=6
    hh = now.hour + now.minute / 60.0
    # NFP: first Friday of month 12:30-14:00 UTC
    if wd == 4 and now.day <= 7 and 12.5 <= hh <= 14.0:
        return True
    # CPI: monthly mid-month weekday 12:30-14:00 UTC
    if wd < 5 and 8 <= now.day <= 15 and 12.5 <= hh <= 14.0:
        return True
    # FOMC: Wednesday ~mid-month 18:00-19:00 UTC
    return wd == 2 and 10 <= now.day <= 20 and 18.0 <= hh <= 19.0
