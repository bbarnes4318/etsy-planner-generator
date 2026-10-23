import csv
import os
import shutil

from reportlab.pdfgen import canvas

from . import calendar_util as cu, fonts
from .config import ORIENTATIONS, SETS, THEMES, WEEK_STARTS, Theme, pdf_path
from .fonts import REG, SEMI, SERIF

TITLES = {
    "2027": "2027 Digital Planner, Hyperlinked GoodNotes Planner, iPad Planner, Daily Weekly Monthly, "
            "{t} Planner, Notability, Android",
    "2027-2028": "2027 2028 Digital Planner, 2 Year Hyperlinked GoodNotes Planner, iPad Planner, "
                 "Daily Weekly Monthly, {t}, Notability",
    "undated": "Undated Digital Planner, Hyperlinked GoodNotes Planner, iPad Planner, Daily Weekly Monthly, "
               "{t} Planner, Start Anytime",
}
COMMON_TAGS = ["digital planner", "goodnotes planner", "ipad planner", "hyperlinked planner",
               "notability planner", "daily planner", "weekly planner", "android planner",
               "minimalist planner", "samsung notes"]
SET_TAGS = {"2027": ["2027 planner", "planner 2027"],
            "2027-2028": ["2027 2028 planner", "two year planner"],
            "undated": ["undated planner", "start anytime"]}
SET_LABEL = {"2027": "2027", "2027-2028": "2027–2028", "undated": "undated"}
DESCRIPTION = """Plan your whole year on your tablet with this fully hyperlinked {set_label} digital planner in the {theme} design. Tap any tab, date or label to jump straight to the page you need.

WHAT'S INCLUDED
• Year overview with clickable dates
• {months} monthly calendars
• {weeks} weekly spreads
• {days} daily pages with hourly schedule, top 3, to-do, water and mood trackers
• Goals page
• Monthly habit trackers
• Monthly budget pages
• 50 notes pages (lined, grid, dot)
• Portrait and landscape versions
• Monday start and Sunday start versions

WORKS WITH
GoodNotes, Notability, Noteshelf, Samsung Notes, Xodo, reMarkable and any PDF annotation app that supports hyperlinks.

HOW IT WORKS
This is an instant digital download. No physical item will be shipped. After purchase, download the files from your Etsy Purchases page and import the PDF into your app. Import instructions are included.

For personal use only."""

HOW_TO = [
    ("GoodNotes (iPad)", "Download the PDF to the Files app. Open GoodNotes, tap the + button, choose Import, "
                         "select the planner PDF."),
    ("Notability (iPad)", "Tap Import in the library, choose the planner PDF from Files."),
    ("Noteshelf", "Tap + then Import, select the PDF."),
    ("Samsung Notes (Android)", "Open Samsung Notes, tap the menu, choose Import PDF, select the planner."),
    ("Xodo (Android/Windows)", "Open Xodo, tap Browse, open the planner PDF."),
    ("reMarkable", "Upload the PDF through the reMarkable desktop app or my.remarkable.com."),
    ("Tip", "Tap any tab, date or label to jump to that page. Use your app's read/view mode if links do not "
            "respond in edit/pen mode."),
    ("Which file to choose", "Portrait or Landscape layout; Monday or Sunday week start."),
]


def title(set_key, theme):
    parts = TITLES[set_key].format(t=Theme(theme).display).split(", ")
    while len(", ".join(parts)) > 140:
        parts.pop()
    return ", ".join(parts)


def tags(set_key, theme):
    out = COMMON_TAGS + SET_TAGS[set_key] + [f"{Theme(theme).display.lower()} planner"]
    assert len(out) == 13 and all(len(t) <= 20 for t in out), out
    return out


def counts(set_key):
    weeks = sorted({len(cu.make_plan(set_key, ws).weeks) for ws in WEEK_STARTS})
    plan = cu.make_plan(set_key, "mon")
    return len(plan.months), "–".join(map(str, weeks)), len(plan.days)


def write_csv(out):
    out.mkdir(parents=True, exist_ok=True)
    path = out / "listings.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel shows – and • correctly
        w = csv.writer(f)
        w.writerow(["folder", "title", "tags", "description"])
        for s in SETS:
            months, weeks, days = counts(s)
            for t in THEMES:
                desc = DESCRIPTION.format(set_label=SET_LABEL[s], theme=Theme(t).display,
                                          months=months, weeks=weeks, days=days)
                w.writerow([f"{s}_{t}", title(s, t), ",".join(tags(s, t)), desc])
    return path


def wrap(s, font, size, width):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if stringWidth(trial, font, size) > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def how_to_import(path, theme_key):
    fonts.register()
    t = Theme(theme_key)
    W, H = 768, 1024
    c = canvas.Canvas(str(path), pagesize=(W, H), pageCompression=1)
    c.setTitle("How to Import Your Planner")
    c.setFillColor(t.bg)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(t.ink)
    c.setFont(SERIF, 34)
    c.drawString(64, H - 120, "How to Import Your Planner")
    c.setStrokeColor(t.accent)
    c.setLineWidth(1.2)
    c.line(64, H - 140, 184, H - 140)
    y = H - 196
    for head, body in HOW_TO:
        c.setFillColor(t.accent if head in ("Tip", "Which file to choose") else t.ink)
        c.setFont(SEMI, 14)
        c.drawString(64, y, head)
        y -= 22
        c.setFillColor(t.ink)
        c.setFont(REG, 12.5)
        for line in wrap(body, REG, 12.5, W - 128):
            c.drawString(64, y, line)
            y -= 18
        y -= 22
    c.showPage()
    c.save()


def bundle(out, set_key, theme):
    """out/etsy/{set}_{theme}/: the 4 planner PDFs + How_To_Import.pdf."""
    d = out / "etsy" / f"{set_key}_{theme}"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for o in ORIENTATIONS:
        for ws in WEEK_STARTS:
            src = pdf_path(out, set_key, theme, o, ws)
            try:
                os.link(src, d / src.name)
            except OSError:
                shutil.copy2(src, d / src.name)
    how_to_import(d / "How_To_Import.pdf", theme)
    return d


if __name__ == "__main__":
    for s in SETS:
        for t in THEMES:
            assert len(title(s, t)) <= 140, title(s, t)
            tags(s, t)
    print(counts("2027"), counts("2027-2028"), counts("undated"))
