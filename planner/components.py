from dataclasses import dataclass

from reportlab.pdfbase.pdfmetrics import stringWidth

from . import calendar_util as cu
from .config import LINE_W, MARGIN, NAV_H, SIZES, TAB_GAP, TAB_W, TOP_GAP
from .fonts import REG, SEMI, SERIF

TAB_LABELS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
              "YR", "GOAL", "HAB", "NOTE"]


@dataclass
class Page:
    name: str            # named destination
    kind: str
    year: object         # int or 'u'
    month: int = None    # current month (tab highlight, Month nav, HAB tab)
    week: int = None     # Week nav (day pages)
    label: str = ""      # right side of nav bar
    data: object = None  # kind-specific payload


class Ctx:
    def __init__(self, c, theme, orientation, plan):
        self.c, self.t, self.plan = c, theme, plan
        self.W, self.H = SIZES[orientation]
        self.portrait = orientation == "portrait"
        self.x0, self.x1 = MARGIN, self.W - TAB_W - TAB_GAP
        self.y0, self.y1 = MARGIN, self.H - NAV_H - TOP_GAP
        self.linked = set()

    def link(self, x0, y0, x1, y1, dest):
        self.c.linkAbsolute("", dest, (x0, y0, x1, y1), thickness=0)
        self.linked.add(dest)

    def text(self, x, y, s, font=REG, size=11, color=None, align="left"):
        c = self.c
        c.setFont(font, size)
        c.setFillColor(color or self.t.ink)
        {"left": c.drawString, "center": c.drawCentredString, "right": c.drawRightString}[align](x, y, s)

    def hline(self, x0, x1, y, color=None):
        self.c.setStrokeColor(color or self.t.line)
        self.c.setLineWidth(LINE_W)
        self.c.line(x0, y, x1, y)

    def ruled(self, x0, x1, ytop, ybot, step=22):
        """Horizontal rules every `step` below ytop, down to ybot. Returns the y of each rule."""
        ys, y = [], ytop - step
        while y >= ybot - 0.01:
            ys.append(y)
            y -= step
        self.c.setStrokeColor(self.t.line)
        self.c.setLineWidth(LINE_W)
        for y in ys:
            self.c.line(x0, y, x1, y)
        return ys

    def card(self, x, y, w, h, label=None):
        """Panel card; returns the y below its label (top of the body)."""
        c = self.c
        c.setFillColor(self.t.panel)
        c.setStrokeColor(self.t.line)
        c.setLineWidth(LINE_W)
        c.roundRect(x, y, w, h, 8, stroke=1, fill=1)
        if not label:
            return y + h - 10
        self.text(x + 14, y + h - 22, label.upper(), SEMI, 9.5, self.t.muted)
        return y + h - 30

    def checkbox(self, x, y, size=10):
        self.c.setStrokeColor(self.t.line)
        self.c.setLineWidth(LINE_W * 1.5)
        self.c.roundRect(x, y, size, size, 1.5, stroke=1, fill=0)

    def circle(self, x, y, r):
        self.c.setStrokeColor(self.t.line)
        self.c.setLineWidth(LINE_W * 1.5)
        self.c.circle(x, y, r, stroke=1, fill=0)

    def title(self, s, sub=None, size=30, sub_size=13):
        """Page title at the top of the content box; returns the y where content starts."""
        base = self.y1 - size * 0.85
        self.text(self.x0, base, s, SERIF, size)
        if sub:
            self.text(self.x0 + stringWidth(s, SERIF, size) + 14, base, sub, REG, sub_size, self.t.muted)
        return base - 22

    def button(self, x, y, w, h, s, dest, size=11, filled=False):
        c = self.c
        c.setFillColor(self.t.accent if filled else self.t.accent_soft)
        c.roundRect(x, y, w, h, min(8, h / 2), stroke=0, fill=1)
        self.text(x + w / 2, y + h / 2 - size * 0.35, s, SEMI, size, self.t.bg if filled else self.t.ink, "center")
        self.link(x, y, x + w, y + h, dest)


def month_label(y, m):
    return f"Month {m}" if y == "u" else f"{cu.MONTHS[m - 1]} {y}"


def background(ctx):
    ctx.c.setFillColor(ctx.t.bg)
    ctx.c.rect(0, 0, ctx.W, ctx.H, stroke=0, fill=1)


def nav(ctx, page):
    y = page.year
    m = page.month or 1
    items = [("Index", "index"), ("Year", cu.year_dest(y)), ("Month", cu.month_dest(y, m))]
    if page.week:
        items.append(("Week", cu.week_dest(page.week)))
    if page.kind in ("notes", "notes-index"):
        items.append(("Notes Index", "notes-index"))
    top, bot = ctx.H, ctx.H - NAV_H
    x = MARGIN
    for label, dest in items:
        w = stringWidth(label, SEMI, 11)
        ctx.text(x, bot + NAV_H / 2 - 4, label, SEMI, 11, ctx.t.muted)
        ctx.link(x - 9, bot, x + w + 9, top, dest)
        x += w + 18
    if page.label:
        ctx.text(ctx.x1, bot + NAV_H / 2 - 4, page.label, SEMI, 11, ctx.t.ink, "right")
    ctx.hline(MARGIN, ctx.x1, bot)


def tabs(ctx, page):
    c, t = ctx.c, ctx.t
    y = page.year
    dests = [cu.month_dest(y, m) for m in range(1, 13)] + [
        cu.year_dest(y), "goals", cu.habit_dest(y, page.month or 1), "notes-index"]
    x0 = ctx.W - TAB_W
    labels = [f"M{m}" for m in range(1, 13)] + TAB_LABELS[12:] if y == "u" else TAB_LABELS
    h = (ctx.H - 2 * MARGIN) / len(labels)
    for i, (label, dest) in enumerate(zip(labels, dests)):
        ty = ctx.H - MARGIN - (i + 1) * h
        current = i < 12 and page.month == i + 1
        c.setFillColor(t.accent if current else t.accent_soft)
        c.roundRect(x0 + 4, ty + 1, TAB_W + 10, h - 2, 7, stroke=0, fill=1)
        c.saveState()
        c.translate(x0 + 4 + (TAB_W - 4) / 2, ty + h / 2)
        c.rotate(90)
        ctx.text(0, -3.2, label, SEMI, 9, t.bg if current else t.ink, "center")
        c.restoreState()
        ctx.link(x0, ty, ctx.W, ty + h, dest)


def grid(ctx, x0, y0, x1, y1, step=18):
    c = ctx.c
    c.setStrokeColor(ctx.t.line)
    c.setLineWidth(LINE_W)
    nx, ny = int((x1 - x0) // step), int((y1 - y0) // step)
    gx0, gy1 = x0 + ((x1 - x0) - nx * step) / 2, y1 - ((y1 - y0) - ny * step) / 2
    xs = [gx0 + i * step for i in range(nx + 1)]
    ys = [gy1 - j * step for j in range(ny + 1)]
    c.grid(xs, ys)


def dots(ctx, x0, y0, x1, y1, step=18):
    c = ctx.c
    c.setFillColor(ctx.t.line)
    nx, ny = int((x1 - x0) // step), int((y1 - y0) // step)
    gx0, gy1 = x0 + ((x1 - x0) - nx * step) / 2, y1 - ((y1 - y0) - ny * step) / 2
    for i in range(nx + 1):
        for j in range(ny + 1):
            c.circle(gx0 + i * step, gy1 - j * step, 0.8, stroke=0, fill=1)
