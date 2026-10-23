from ..components import month_label
from ..fonts import SEMI

HEAD, COLHEAD, PAD = 30, 18, 8


def table(ctx, x, y, w, h, label, cols, nrows):
    """cols: [(header, weight, kind)], kind in text/amount/check."""
    body = ctx.card(x, y, w, h, label)
    t = ctx.t
    total = sum(c[1] for c in cols)
    xs, cx = [], x + 14
    for head, wt, kind in cols:
        cw = (w - 28) * wt / total
        xs.append((cx, cx + cw, kind))
        if kind == "amount":
            ctx.text(cx + cw - 4, body - 10, head.upper(), SEMI, 7.5, t.muted, "right")
        elif kind == "check":
            ctx.text(cx + cw / 2, body - 10, head.upper(), SEMI, 7.5, t.muted, "center")
        else:
            ctx.text(cx + 4, body - 10, head.upper(), SEMI, 7.5, t.muted)
        cx += cw
    rtop = body - COLHEAD
    rh = (rtop - y - PAD) / nrows
    for r in range(nrows):
        ry = rtop - (r + 1) * rh
        for a, b, kind in xs:
            if kind == "check":
                ctx.checkbox((a + b) / 2 - 5, ry + 4, 10)
            else:
                ctx.hline(a + 4, b - 6, ry + 2)


def summary(ctx, x, y, w, h):
    body = ctx.card(x, y, w, h, "Summary")
    rh = (body - y - PAD) / 4
    for i, label in enumerate(("Income", "Expenses", "Savings", "Balance")):
        ry = body - (i + 1) * rh
        ctx.text(x + 14, ry + 6, label, SEMI, 10)
        ctx.hline(x + w * 0.45, x + w - 14, ry + 2)


INCOME = [("Source", 3, "text"), ("Amount", 1.4, "amount")]
BILLS = [("Bill", 3, "text"), ("Due", 1, "text"), ("Amount", 1.3, "amount"), ("Paid", 0.7, "check")]
EXPENSES = [("Date", 1, "text"), ("Item", 2.6, "text"), ("Category", 1.6, "text"), ("Amount", 1.2, "amount")]


def draw(ctx, page):
    y, m = page.year, page.month
    top = ctx.title(f"Budget — {month_label(y, m)}" if y != "u" else "Budget — Month ____")
    x0, x1, y0, gap = ctx.x0, ctx.x1, ctx.y0, 12
    W, H = x1 - x0, top - y0
    if ctx.portrait:
        avail = H - 2 * gap
        fixed = 3 * (HEAD + COLHEAD + PAD)
        rh = (avail - fixed) / (5 + 10 + 15)
        h1 = HEAD + COLHEAD + PAD + 5 * rh
        h2 = HEAD + COLHEAD + PAD + 10 * rh
        lw = W * 0.56
        table(ctx, x0, top - h1, lw, h1, "Income", INCOME, 5)
        summary(ctx, x0 + lw + gap, top - h1, W - lw - gap, h1)
        table(ctx, x0, top - h1 - gap - h2, W, h2, "Bills", BILLS, 10)
        table(ctx, x0, y0, W, top - h1 - h2 - 2 * gap - y0, "Expenses", EXPENSES, 15)
    else:
        lw = (W - gap) / 2
        avail = H - 2 * gap
        fixed = 2 * (HEAD + COLHEAD + PAD) + HEAD + PAD
        rh = (avail - fixed) / (5 + 10 + 4 * 0.9)
        h1 = HEAD + COLHEAD + PAD + 5 * rh
        hs = HEAD + PAD + 4 * 0.9 * rh
        table(ctx, x0, top - h1, lw, h1, "Income", INCOME, 5)
        summary(ctx, x0, top - h1 - gap - hs, lw, hs)
        table(ctx, x0, y0, lw, top - h1 - hs - 2 * gap - y0, "Bills", BILLS, 10)
        table(ctx, x0 + lw + gap, y0, lw, H, "Expenses", EXPENSES, 15)
