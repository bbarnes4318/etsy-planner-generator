from reportlab.pdfbase.pdfmetrics import stringWidth

from ..fonts import REG, SEMI, SERIF

TITLES = {"2027": "2027", "2027-2028": "2027 – 2028", "undated": "Undated"}
TITLE_SIZES = {"2027": 88, "2027-2028": 58, "undated": 64}


def arch(c, x0, x1, y0, top):
    """Rectangle from x0..x1, y0..top whose top edge is a full semicircle."""
    r = (x1 - x0) / 2
    p = c.beginPath()
    p.moveTo(x0, y0)
    p.lineTo(x1, y0)
    p.lineTo(x1, top - r)
    p.arcTo(x0, top - 2 * r, x1, top, startAng=0, extent=180)
    p.close()
    return p


def spaced(c, cx, y, s, font, size, color, space):
    """Centered text with character spacing."""
    w = stringWidth(s, font, size) + space * (len(s) - 1)
    c.saveState()  # char spacing is graphics state; keep it from leaking into later text
    t = c.beginText(cx - w / 2, y)
    t.setFont(font, size)
    t.setCharSpace(space)
    t.setFillColor(color)
    t.textOut(s)
    c.drawText(t)
    c.restoreState()


def draw(ctx, page):
    c, W, H, t = ctx.c, ctx.W, ctx.H, ctx.t
    m = min(W, H)
    c.setFillColor(t.accent_soft)
    for cx, cy, r in ((W * 0.18, H * 0.84, m * 0.16), (W * 0.86, H * 0.16, m * 0.21), (W * 0.80, H * 0.88, m * 0.08)):
        c.circle(cx, cy, r, stroke=0, fill=1)

    aw = min(W * 0.57, H * 0.47)
    ah = aw * 1.36
    x0, x1, ab = W / 2 - aw / 2, W / 2 + aw / 2, H / 2 - ah / 2
    c.setFillColor(t.panel)
    c.setStrokeColor(t.accent)
    c.setLineWidth(1.5)
    c.drawPath(arch(c, x0, x1, ab, ab + ah), stroke=1, fill=1)
    c.setStrokeColor(t.line)
    c.setLineWidth(0.8)
    c.drawPath(arch(c, x0 + 10, x1 - 10, ab + 10, ab + ah - 10), stroke=1, fill=0)

    set_key = ctx.plan.set_key
    spaced(c, W / 2, ab + ah * 0.70, "PLANNER", SEMI, 11, t.muted, 4)
    title = TITLES[set_key]
    size = min(TITLE_SIZES[set_key], TITLE_SIZES[set_key] * (aw - 60) / stringWidth(title, SERIF, TITLE_SIZES[set_key]))
    ctx.text(W / 2, ab + ah * 0.50, title, SERIF, size, align="center")
    c.setStrokeColor(t.accent)
    c.setLineWidth(1.2)
    c.line(W / 2 - 40, ab + ah * 0.44, W / 2 + 40, ab + ah * 0.44)
    ctx.text(W / 2, ab + ah * 0.37, "Digital Planner", REG, 16, t.muted, "center")
    spaced(c, W / 2, ab + ah * 0.12, "FULLY HYPERLINKED", SEMI, 9, t.muted, 3)
    spaced(c, W / 2, ab - 28, t.display.upper(), SEMI, 10, t.muted, 3)
    ctx.link(W * 0.1, H * 0.15, W * 0.9, H * 0.85, "index")
