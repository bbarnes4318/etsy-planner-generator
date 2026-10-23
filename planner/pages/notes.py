from .. import components as comp
from ..fonts import SEMI

KINDS = [("lined", "Lined Notes", 30), ("grid", "Grid Notes", 10), ("dot", "Dot Notes", 10)]


def dest(kind, n):
    return f"notes-{kind}-{n:02d}"


def draw_index(ctx, page):
    top = ctx.title("Notes")
    gap = 12
    bw = (ctx.x1 - ctx.x0 - 2 * gap) / 3
    for i, (kind, label, _) in enumerate(KINDS):
        ctx.button(ctx.x0 + i * (bw + gap), top - 52, bw, 52, label, dest(kind, 1), 13, filled=True)
    y = top - 52 - 28
    per_row = 10
    sw = (ctx.x1 - ctx.x0 - (per_row - 1) * 8) / per_row
    for kind, label, count in KINDS:
        ctx.text(ctx.x0, y - 14, label.upper(), SEMI, 9.5, ctx.t.muted)
        y -= 24
        for n in range(1, count + 1):
            r, k = divmod(n - 1, per_row)
            ctx.button(ctx.x0 + k * (sw + 8), y - (r + 1) * 40 + 6, sw, 34, str(n), dest(kind, n), 11)
        y -= ((count - 1) // per_row + 1) * 40 + 20


def draw(ctx, page):
    kind, n = page.data
    label = dict((k, l) for k, l, _ in KINDS)[kind]
    top = ctx.title(label, f"{n:02d}", 22)
    x0, x1, y0 = ctx.x0, ctx.x1, ctx.y0
    ctx.card(x0, y0, x1 - x0, top - y0)
    if kind == "lined":
        ctx.ruled(x0 + 16, x1 - 16, top - 4, y0 + 10, 24)
    elif kind == "grid":
        comp.grid(ctx, x0 + 10, y0 + 10, x1 - 10, top - 10, 18)
    else:
        comp.dots(ctx, x0 + 10, y0 + 10, x1 - 10, top - 10, 18)
