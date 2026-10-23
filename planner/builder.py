from reportlab import rl_config

rl_config.useA85 = 0  # raw binary streams; ASCII85 would add 25%

import pymupdf  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

from . import calendar_util as cu, fonts  # noqa: E402
from .components import Ctx, Page, background, month_label, nav, tabs  # noqa: E402
from .config import Theme  # noqa: E402
from .pages import budget, cover, day, goals, habits, index, month, notes, week, year  # noqa: E402

DRAW = {"cover": cover.draw, "index": index.draw, "year": year.draw, "month": month.draw,
        "week": week.draw, "day": day.draw, "goals": goals.draw, "habit": habits.draw,
        "budget": budget.draw, "notes-index": notes.draw_index, "notes": notes.draw}


def short(day):
    y, m, d = day
    return f"Month {m} · Day {d}" if y == "u" else f"{cu.MONTHS[m - 1][:3]} {d}, {y}"


def page_sequence(plan):
    y0, m0 = plan.months[0]
    pages = [Page("cover", "cover", y0), Page("index", "index", y0, label="Index")]
    pages += [Page(cu.year_dest(y), "year", y, label=str(y) if y != "u" else "Year") for y in plan.years]
    for y, m in plan.months:
        pages.append(Page(cu.month_dest(y, m), "month", y, m, label=month_label(y, m)))
        pages += [Page(cu.week_dest(w.num), "week", y, m, label=f"Week {w.num}", data=w)
                  for w in plan.weeks_in((y, m))]
        pages += [Page(cu.day_dest(*d), "day", y, m, plan.week_of[d], short(d), d)
                  for d in plan.days if d[:2] == (y, m)]
    pages.append(Page("goals", "goals", y0, label="Goals"))
    pages += [Page(cu.habit_dest(y, m), "habit", y, m, label="Habits") for y, m in plan.months]
    pages += [Page(cu.budget_dest(y, m), "budget", y, m, label="Budget") for y, m in plan.months]
    pages.append(Page("notes-index", "notes-index", y0, label="Notes"))
    pages += [Page(notes.dest(k, n), "notes", y0, label="Notes", data=(k, n))
              for k, _, count in notes.KINDS for n in range(1, count + 1)]
    return pages


def outline(c, plan, pages):
    names = {p.name for p in pages}
    y0, m0 = plan.months[0]
    c.addOutlineEntry("Cover", "cover", 0)
    c.addOutlineEntry("Index", "index", 0)
    for y in plan.years:
        c.addOutlineEntry(f"Year {y}" if y != "u" else "Year", cu.year_dest(y), 0)
        for yy, m in plan.months:
            if yy == y:
                c.addOutlineEntry(month_label(y, m), cu.month_dest(y, m), 1)
    c.addOutlineEntry("Goals", "goals", 0)
    c.addOutlineEntry("Habits", cu.habit_dest(y0, m0), 0)
    c.addOutlineEntry("Budget", cu.budget_dest(y0, m0), 0)
    c.addOutlineEntry("Notes", "notes-index", 0)
    assert {"goals", "notes-index"} <= names


def build(set_key, theme_key, orientation, week_start, path):
    fonts.register()
    plan = cu.make_plan(set_key, week_start)
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pageCompression=1)
    theme = Theme(theme_key)
    c.setTitle(f"{cover.TITLES[set_key]} Digital Planner — {theme.display}")
    c.setAuthor("planner-generator")
    c.setSubject("Hyperlinked digital planner")
    c.setKeywords(f"set={set_key};week_start={week_start};orientation={orientation};theme={theme_key}")
    ctx = Ctx(c, theme, orientation, plan)
    c.setPageSize((ctx.W, ctx.H))
    pages = page_sequence(plan)
    for p in pages:
        background(ctx)
        c.bookmarkPage(p.name, fit="Fit")
        DRAW[p.kind](ctx, p)
        if p.kind != "cover":
            nav(ctx, p)
            tabs(ctx, p)
        c.showPage()
    missing = ctx.linked - {p.name for p in pages}
    assert not missing, f"links to undefined destinations: {sorted(missing)[:5]}"
    outline(c, plan, pages)
    c.save()
    add_named_dests(path, [p.name for p in pages])
    return plan, pages


def add_named_dests(path, names):
    """reportlab links pages directly; also publish a catalog /Dests dict so names are readable.
    Re-saving with object streams compresses the thousands of link annotations (~45% smaller)."""
    doc = pymupdf.open(path)
    entries = " ".join(f"/{n} [{doc.page_xref(i)} 0 R /Fit]" for i, n in enumerate(names))
    doc.xref_set_key(doc.pdf_catalog(), "Dests", f"<<{entries}>>")
    tmp = path.with_suffix(".tmp")
    doc.save(tmp, garbage=1, deflate=True, use_objstms=1)  # garbage>=3 merges identical links across pages; keep each page's own
    doc.close()
    tmp.replace(path)
