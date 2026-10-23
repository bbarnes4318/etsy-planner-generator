from .. import calendar_util as cu
from ..components import month_label
from ..fonts import REG


def draw(ctx, page):
    y, m, t = page.year, page.month, ctx.t
    top = ctx.title(f"Habits — {month_label(y, m)}" if y != "u" else "Habits — Month ____")
    n = cu.days_in_month(y, m)
    rh = 46 if ctx.portrait else 42
    th = 30 + 20 + 10 * rh + 10
    x0, x1 = ctx.x0, ctx.x1
    body = ctx.card(x0, top - th, x1 - x0, th, "Habit")
    nx0 = x0 + 14
    dx0 = nx0 + 160
    dw = (x1 - 14 - dx0) / n
    for d in range(n):
        ctx.text(dx0 + (d + 0.5) * dw, body - 10, str(d + 1), REG, 8, t.muted, "center")
    rows_top = body - 20
    sq = min(11, dw - 4)
    for r in range(10):
        ry = rows_top - (r + 1) * rh
        ctx.hline(nx0, dx0 - 10, ry + 10)
        for d in range(n):
            ctx.checkbox(dx0 + (d + 0.5) * dw - sq / 2, ry + rh / 2 - sq / 2, sq)
        if r < 9:
            ctx.hline(nx0, x1 - 14, ry)
    nh = top - th - 16 - ctx.y0
    if nh > 80:
        body = ctx.card(x0, ctx.y0, x1 - x0, nh, "Notes")
        ctx.ruled(x0 + 14, x1 - 14, body + 4, ctx.y0 + 6)
