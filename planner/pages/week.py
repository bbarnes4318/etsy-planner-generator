from datetime import date

from .. import calendar_util as cu
from ..fonts import REG, SEMI

HEAD = 30


def span(week):
    a, b = week.days[0], week.days[-1]
    fa = f"{cu.MONTHS[a[1] - 1][:3]} {a[2]}"
    fb = f"{cu.MONTHS[b[1] - 1][:3]} {b[2]}, {b[0]}"
    return f"{fa}, {a[0]} – {fb}" if a[0] != b[0] else f"{fa} – {fb}"


def checklist(ctx, x0, x1, top, n, step=22):
    for i in range(n):
        y = top - (i + 1) * step
        ctx.checkbox(x0, y + 3, 10)
        ctx.hline(x0 + 16, x1, y)


def day_block(ctx, x, y, w, h, header, dest):
    ctx.card(x, y, w, h)
    ctx.text(x + 12, y + h - 20, header, SEMI, 10)
    if dest:
        ctx.link(x, y + h - HEAD, x + w, y + h, dest)
    ctx.ruled(x + 12, x + w - 12, y + h - HEAD + 4, y + 6)


def draw(ctx, page):
    week, plan, t = page.data, ctx.plan, ctx.t
    top = ctx.title(f"Week {week.num}", span(week) if plan.dated else None)
    if plan.dated and plan.week_start == "mon":
        iso = date(*week.days[0]).isocalendar()[1]
        ctx.text(ctx.x1, ctx.y1 - 22, f"ISO week {iso}", REG, 9, t.muted, "right")
    names = [cu.WEEKDAYS[i] for i in cu.weekday_order(plan.week_start)]
    blocks = []
    for name, day in zip(names, week.days):
        dest = cu.day_dest(*day) if day and plan.in_range(day) else None
        blocks.append((f"{name} {day[2]}" if plan.dated else f"{name}  ________", dest))
    gap = 8
    if ctx.portrait:
        lw = (ctx.x1 - ctx.x0) * 0.68
        bh = (top - ctx.y0 - 6 * gap) / 7
        for i, (head, dest) in enumerate(blocks):
            day_block(ctx, ctx.x0, top - (i + 1) * bh - i * gap, lw, bh, head, dest)
        rx, rw = ctx.x0 + lw + 12, ctx.x1 - ctx.x0 - lw - 12
        ph = HEAD + 6 * 22 + 10
        th = HEAD + 10 * 22 + 10
        body = ctx.card(rx, top - ph, rw, ph, "Priorities")
        checklist(ctx, rx + 14, rx + rw - 14, body + 4, 6)
        ty = top - ph - gap - th
        body = ctx.card(rx, ty, rw, th, "To-Do")
        checklist(ctx, rx + 14, rx + rw - 14, body + 4, 10)
        nh = ty - gap - ctx.y0
        body = ctx.card(rx, ctx.y0, rw, nh, "Notes")
        ctx.ruled(rx + 14, rx + rw - 14, body + 4, ctx.y0 + 6)
    else:
        bw = (ctx.x1 - ctx.x0 - 3 * gap) / 4
        bh = (top - ctx.y0 - gap) / 2
        for i, (head, dest) in enumerate(blocks):
            r, k = divmod(i, 4)
            day_block(ctx, ctx.x0 + k * (bw + gap), top - (r + 1) * bh - r * gap, bw, bh, head, dest)
        x = ctx.x0 + 3 * (bw + gap)
        body = ctx.card(x, ctx.y0, bw, bh, "Notes")
        ctx.ruled(x + 12, x + bw - 12, body + 4, ctx.y0 + 6)
