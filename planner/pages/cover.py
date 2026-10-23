from ..fonts import REG, SERIF

TITLES = {"2027": "2027", "2027-2028": "2027 – 2028", "undated": "Undated"}


def draw(ctx, page):
    W, H, t = ctx.W, ctx.H, ctx.t
    cy = H * 0.55
    ctx.text(W / 2, cy, TITLES[ctx.plan.set_key], SERIF, 54, align="center")
    ctx.c.setStrokeColor(t.accent)
    ctx.c.setLineWidth(1.2)
    ctx.c.line(W / 2 - 60, cy - 26, W / 2 + 60, cy - 26)
    ctx.text(W / 2, cy - 60, "Digital Planner", REG, 16, t.muted, "center")
    ctx.link(W * 0.1, H * 0.15, W * 0.9, H * 0.85, "index")
