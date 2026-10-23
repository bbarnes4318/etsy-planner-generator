from .. import calendar_util as cu
from ..components import month_label
from ..fonts import REG, SEMI


def draw(ctx, page):
    y, plan, t = page.year, ctx.plan, ctx.t
    top = ctx.title(str(y) if y != "u" else "Year Overview", "Year Overview" if y != "u" else None)
    cols, rows = (3, 4) if ctx.portrait else (4, 3)
    gap = 12
    cw = (ctx.x1 - ctx.x0 - gap * (cols - 1)) / cols
    ch = (top - ctx.y0 - gap * (rows - 1)) / rows
    order = cu.weekday_order(plan.week_start)
    for m in range(1, 13):
        r, col = divmod(m - 1, cols)
        x = ctx.x0 + col * (cw + gap)
        yb = top - (r + 1) * ch - r * gap
        ctx.card(x, yb, cw, ch)
        name_top = yb + ch
        ctx.text(x + 12, name_top - 24, month_label(y, m) if y == "u" else cu.MONTHS[m - 1], SEMI, 12)
        ctx.link(x, name_top - 34, x + cw, name_top, cu.month_dest(y, m))
        dw = (cw - 20) / 7
        gx = x + 10
        if y == "u":
            cells = [[("u", m, r * 7 + c + 1) if r * 7 + c < 31 else None for c in range(7)] for r in range(5)]
            gtop = name_top - 40
        else:
            for i, wd in enumerate(order):
                ctx.text(gx + (i + 0.5) * dw, name_top - 46, cu.WEEKDAYS[wd][0], REG, 8, t.muted, "center")
            cells = cu.month_grid(y, m, plan.week_start)
            gtop = name_top - 54
        dh = (gtop - yb - 8) / len(cells)
        for ri, row in enumerate(cells):
            for ci, day in enumerate(row):
                if day is None or day[1] != m:
                    continue
                cx, cy = gx + ci * dw, gtop - (ri + 1) * dh
                ctx.text(cx + dw / 2, cy + dh / 2 - 3, str(day[2]), REG, 9, align="center")
                if plan.in_range(day):
                    ctx.link(cx, cy, cx + dw, cy + dh, cu.day_dest(*day))
