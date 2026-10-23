"""Date math for a planner. A "day" is a (year, month, day) tuple; undated planners use year 'u'."""
import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
WEEKDAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
RANGES = {"2027": (date(2027, 1, 1), date(2027, 12, 31)),
          "2027-2028": (date(2027, 1, 1), date(2028, 12, 31))}


def year_dest(y): return f"year-{y}"
def month_dest(y, m): return f"m-{y}-{m:02d}"
def week_dest(n): return f"w-{n:03d}"
def day_dest(y, m, d): return f"d-{y}-{m:02d}-{d:02d}"
def habit_dest(y, m): return f"habit-{y}-{m:02d}"
def budget_dest(y, m): return f"budget-{y}-{m:02d}"


def ws_index(week_start):
    """Python weekday() of the first day of the week."""
    return 0 if week_start == "mon" else 6


def weekday_order(week_start):
    s = ws_index(week_start)
    return [(s + i) % 7 for i in range(7)]


def undated_weeks(m):
    return range((m - 1) * 52 // 12 + 1, m * 52 // 12 + 1)


@dataclass
class Week:
    num: int
    days: list          # 7 slots: (y, m, d) or None
    home: tuple         # (y, m) the week is filed under
    start: date = None  # dated only


@dataclass
class Plan:
    set_key: str
    week_start: str
    dated: bool
    years: list
    months: list                      # [(y, m)]
    weeks: list                       # [Week]
    days: list                        # [(y, m, d)] in order
    week_of: dict = field(default_factory=dict)   # day -> week num

    def in_range(self, day):
        return day in self.week_of

    def weeks_in(self, ym):
        return [w for w in self.weeks if w.home == ym]


def make_plan(set_key, week_start):
    if set_key == "undated":
        months = [("u", m) for m in range(1, 13)]
        days = [("u", m, d) for m in range(1, 13) for d in range(1, 32)]
        weeks, week_of = [], {}
        for m in range(1, 13):
            nums = list(undated_weeks(m))
            for i, n in enumerate(nums):
                slots = [("u", m, i * 7 + j + 1) if i * 7 + j + 1 <= 31 else None for j in range(7)]
                weeks.append(Week(n, slots, ("u", m)))
            for d in range(1, 32):
                week_of[("u", m, d)] = nums[min((d - 1) // 7, len(nums) - 1)]
        return Plan(set_key, week_start, False, ["u"], months, weeks, days, week_of)

    first, last = RANGES[set_key]
    days, d = [], first
    while d <= last:
        days.append((d.year, d.month, d.day))
        d += timedelta(1)
    months = sorted({(y, m) for y, m, _ in days})
    start = first - timedelta((first.weekday() - ws_index(week_start)) % 7)
    weeks, week_of, n = [], {}, 1
    while start <= last:
        slots = [start + timedelta(i) for i in range(7)]
        home = max((start.year, start.month), months[0])
        weeks.append(Week(n, [(s.year, s.month, s.day) for s in slots], home, start))
        for s in slots:
            if first <= s <= last:
                week_of[(s.year, s.month, s.day)] = n
        start += timedelta(7)
        n += 1
    return Plan(set_key, week_start, True, sorted({y for y, _ in months}), months, weeks, days, week_of)


def month_grid(y, m, week_start):
    """6x7 list of (y, m, d) for a dated month view, starting at the week start on/before the 1st."""
    first = date(y, m, 1)
    start = first - timedelta((first.weekday() - ws_index(week_start)) % 7)
    return [[_t(start + timedelta(r * 7 + c)) for c in range(7)] for r in range(6)]


def _t(d): return (d.year, d.month, d.day)


def days_in_month(y, m):
    return 31 if y == "u" else calendar.monthrange(y, m)[1]


def weekday_of(day):
    return date(*day).weekday()


if __name__ == "__main__":
    for s in ("2027", "2027-2028", "undated"):
        for ws in ("mon", "sun"):
            p = make_plan(s, ws)
            assert len(p.weeks) == len({w.num for w in p.weeks}) and p.weeks[-1].num == len(p.weeks)
            assert all(p.week_of[d] for d in p.days)
            print(s, ws, len(p.months), len(p.weeks), len(p.days))
    p = make_plan("undated", "mon")
    assert len(p.weeks) == 52 and len(p.days) == 372 and p.week_of[("u", 3, 15)] == 11
    p = make_plan("2027", "mon")
    assert p.weeks[0].home == (2027, 1) and p.weeks[0].start == date(2026, 12, 28)
    assert p.week_of[(2027, 1, 4)] == 2
