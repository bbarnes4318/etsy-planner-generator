from .. import calendar_util as cu
from ..components import month_label
from ..fonts import SEMI


def draw(ctx, page):
    y, m, plan, t, c = page.year, page.month, ctx.plan, ctx.t, ctx.c
    top = ctx.title(month_label(y, m) if y != "u" else "Month ____", size=30)
    if y == "u":
        cells = [[("u", m, r * 7 + k + 1) if r * 7 + k < 31 else None for k in range(7)] for r in range(5)]
        weeks = list(cu.undated_weeks(m))
        row_weeks = [weeks[r] if r < len(weeks) else None for r in range(5)]
    else:
        cells = cu.month_grid(y, m, plan.week_start)
        row_weeks = [next((plan.week_of[d] for d in row if d in plan.week_of), None) for row in cells]
    nrows = len(cells)
    gx0, gx1 = ctx.x0 + 30, ctx.x1
    cw = (gx1 - gx0) / 7
    for i, wd in enumerate(cu.weekday_order(plan.week_start)):
        ctx.text(gx0 + (i + 0.5) * cw, top - 12, cu.WEEKDAYS[wd], SEMI, 9, t.muted, "center")
    gtop = top - 22
    ch = 96 if ctx.portrait else (gtop - ctx.y0) / nrows
    gbot = gtop - nrows * ch
    c.setFillColor(t.panel)
    c.setStrokeColor(t.line)
    c.setLineWidth(0.6)
    c.rect(gx0, gbot, gx1 - gx0, gtop - gbot, stroke=0, fill=1)
    c.grid([gx0 + i * cw for i in range(8)], [gtop - r * ch for r in range(nrows + 1)])
    for r, row in enumerate(cells):
        ry = gtop - (r + 1) * ch
        for k, day in enumerate(row):
            if day is None:
                continue
            x = gx0 + k * cw
            ctx.text(x + 8, ry + ch - 18, str(day[2]), SEMI, 11, t.ink if day[1] == m else t.muted)
            if plan.in_range(day):
                ctx.link(x, ry, x + cw, ry + ch, cu.day_dest(*day))
        if row_weeks[r]:
            c.setFillColor(t.accent_soft)
            c.roundRect(ctx.x0, ry + ch - 24, 26, 18, 5, stroke=0, fill=1)
            ctx.text(ctx.x0 + 13, ry + ch - 18.5, f"W{row_weeks[r]}", SEMI, 8, t.ink, "center")
            ctx.link(ctx.x0, ry, ctx.x0 + 28, ry + ch, cu.week_dest(row_weeks[r]))
    if ctx.portrait and gbot - 16 - ctx.y0 >= 140:
        bw = (ctx.x1 - ctx.x0 - 16) / 2
        bh = gbot - 16 - ctx.y0
        for i, label in enumerate(("Focus", "Notes")):
            x = ctx.x0 + i * (bw + 16)
            body = ctx.card(x, ctx.y0, bw, bh, label)
            ctx.ruled(x + 14, x + bw - 14, body, ctx.y0 + 10)
