from .. import calendar_util as cu
from ..components import month_label
from ..fonts import REG


def draw(ctx, page):
    plan = ctx.plan
    rows = [(f"Year Overview {y}" if y != "u" else "Year Overview", cu.year_dest(y)) for y in plan.years]
    rows += [(month_label(y, m), cu.month_dest(y, m)) for y, m in plan.months]
    y0, m0 = plan.months[0]
    rows += [("Goals", "goals"), ("Habit Trackers", cu.habit_dest(y0, m0)),
             ("Budget", cu.budget_dest(y0, m0)), ("Notes", "notes-index")]
    top = ctx.title("Index") - 8
    half = (len(rows) + 1) // 2
    gap = 32
    cw = (ctx.x1 - ctx.x0 - gap) / 2
    for i, (label, dest) in enumerate(rows):
        col, r = divmod(i, half)
        x = ctx.x0 + col * (cw + gap)
        yb = top - (r + 1) * 34
        ctx.text(x + 4, yb + 11, label, REG, 13)
        ctx.text(x + cw - 4, yb + 11, "→", REG, 13, ctx.t.muted, "right")
        ctx.hline(x, x + cw, yb)
        ctx.link(x, yb, x + cw, yb + 34, dest)
