from .. import calendar_util as cu
from ..fonts import REG, SEMI
from .week import checklist

GAP = 10


def hours():
    return [f"{(h - 1) % 12 + 1} {'AM' if h < 12 else 'PM'}" for h in range(6, 23)]


def schedule(ctx, x, y, w, h):
    body = ctx.card(x, y, w, h, "Schedule")
    step = (body - y - 8) / 17
    for i, label in enumerate(hours()):
        ly = body - (i + 1) * step
        ctx.text(x + 14, ly + 4, label, REG, 9, ctx.t.muted)
        ctx.hline(x + 54, x + w - 14, ly)


def top3(ctx, x, y, w):
    h = 30 + 3 * 24 + 8
    body = ctx.card(x, y - h, w, h, "Top 3")
    for i in range(3):
        ly = body - (i + 1) * 24
        ctx.text(x + 14, ly + 5, f"{i + 1}.", SEMI, 10, ctx.t.muted)
        ctx.hline(x + 30, x + w - 14, ly)
    return y - h - GAP


def todo(ctx, x, y, w, bottom=None):
    h = 30 + 10 * 22 + 10 if bottom is None else y - bottom
    body = ctx.card(x, y - h, w, h, "To-Do")
    checklist(ctx, x + 14, x + w - 14, body + 4, 10, min(30, (h - 40) / 10))
    return y - h - GAP


def circles(ctx, x, y, w, label, n, r):
    h = 30 + 2 * r + 14
    body = ctx.card(x, y - h, w, h, label)
    step = min(2 * r + 10, (w - 28) / n)
    for i in range(n):
        ctx.circle(x + 14 + r + i * step, body - r - 2, r)
    return y - h - GAP


def notes(ctx, x, y, w, bottom):
    body = ctx.card(x, bottom, w, y - bottom, "Notes")
    ctx.ruled(x + 14, x + w - 14, body + 4, bottom + 6)


def draw(ctx, page):
    day, plan, t = page.data, ctx.plan, ctx.t
    y_, m, d = day
    if plan.dated:
        top = ctx.title(cu.WEEKDAY_NAMES[cu.weekday_of(day)], f"{cu.MONTHS[m - 1]} {d}, {y_}", 26, 14)
    else:
        top = ctx.title("Day ____", "____________", 26, 14)
    x0, x1, y0 = ctx.x0, ctx.x1, ctx.y0
    W = x1 - x0
    if ctx.portrait:
        lw = W * 0.55 - GAP / 2
        schedule(ctx, x0, y0, lw, top - y0)
        rx, rw = x0 + lw + GAP, W - lw - GAP
        y = top3(ctx, rx, top, rw)
        y = todo(ctx, rx, y, rw)
        y = circles(ctx, rx, y, rw, "Water", 8, 7)
        y = circles(ctx, rx, y, rw, "Mood", 5, 9)
        notes(ctx, rx, y, rw, y0)
    else:
        cw = (W - 2 * GAP) / 3
        schedule(ctx, x0, y0, cw, top - y0)
        x = x0 + cw + GAP
        y = top3(ctx, x, top, cw)
        todo(ctx, x, y, cw, y0)
        x += cw + GAP
        y = circles(ctx, x, top, cw, "Water", 8, 7)
        y = circles(ctx, x, y, cw, "Mood", 5, 9)
        notes(ctx, x, y, cw, y0)
    i = plan.days.index(day)
    if i > 0:
        ctx.text(x0, 14, "← prev", SEMI, 10, t.muted)
        ctx.link(x0 - 6, 4, x0 + 60, 30, cu.day_dest(*plan.days[i - 1]))
    if i < len(plan.days) - 1:
        ctx.text(x1, 14, "next →", SEMI, 10, t.muted, "right")
        ctx.link(x1 - 60, 4, x1 + 6, 30, cu.day_dest(*plan.days[i + 1]))
