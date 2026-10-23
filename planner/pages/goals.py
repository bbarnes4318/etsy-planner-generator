def draw(ctx, page):
    top = ctx.title("Goals")
    gap = 16
    w = (ctx.x1 - ctx.x0 - gap) / 2
    h = (top - ctx.y0 - gap) / 2
    for i, label in enumerate(("Personal", "Career", "Health", "Finance")):
        r, k = divmod(i, 2)
        x, y = ctx.x0 + k * (w + gap), top - (r + 1) * h - r * gap
        body = ctx.card(x, y, w, h, label)
        ctx.ruled(x + 14, x + w - 14, body, y + 10, (body - y - 10) / 8)
