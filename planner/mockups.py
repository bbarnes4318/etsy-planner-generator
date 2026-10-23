import pymupdf
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

from . import calendar_util as cu
from .config import TAB_W, THEMES, Theme, pdf_path
from .fonts import DIR, REG, SEMI, SERIF

SIZE = (3000, 2250)
BEZEL, RADIUS, FRAME, RIM = 60, 90, "#1A1A1A", "#4A4A4E"  # rim keeps the frame visible on dark bg
HEAD, HEAD_LH, SUB, SUB_LH = 180, 205, 70, 94
INCLUDED = ["Year Overview", "Monthly Calendars", "Weekly Pages", "Daily Pages", "Goals",
            "Habit Trackers", "Monthly Budget", "50 Notes Pages", "Portrait + Landscape",
            "Monday + Sunday Start"]
APPS = ["GoodNotes", "Notability", "Noteshelf", "Samsung Notes", "Xodo", "reMarkable"]
DAILY = {"2027": "365", "2027-2028": "731", "undated": "372"}


def font(name, size):
    return ImageFont.truetype(str(DIR / f"{name}.ttf"), size)


def rgba(hex_, a=1.0):
    return ImageColor.getrgb(hex_) + (int(255 * a),)


def wrap(draw, text, f, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=f) > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def render(page, h):
    zoom = h / page.rect.height
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples), zoom


def device(page, box_h):
    """Framed page render on its own RGBA layer, plus the render zoom."""
    shot, zoom = render(page, box_h - 2 * BEZEL)
    layer = Image.new("RGBA", (shot.width + 2 * BEZEL, shot.height + 2 * BEZEL), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((0, 0, layer.width - 1, layer.height - 1), RADIUS, fill=FRAME, outline=RIM, width=4)
    layer.paste(shot, (BEZEL, BEZEL))
    return layer, zoom


def place(img, layer, x, y):
    """Composite `layer` at (x, y) with a soft drop shadow."""
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, int(255 * 0.35)), (x + 30, y + 30), layer.getchannel("A"))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(40)))
    img.alpha_composite(layer, (x, y))


def tablet(img, page, box_h, right):
    """Vertically centered tablet with its right edge at `right`. Returns (frame x, screen origin, zoom)."""
    layer, zoom = device(page, box_h)
    x, y = right - layer.width, (SIZE[1] - layer.height) // 2
    place(img, layer, x, y)
    return x, (x + BEZEL, y + BEZEL), zoom


def headline(img, t, text, sub, x0, x1, y_center, extra=0):
    """Draw headline (+ optional sub) centered on y_center, reserving `extra` px below. Returns end y."""
    d = ImageDraw.Draw(img)
    hf, sf = font(SERIF, HEAD), font(REG, SUB)
    lines = wrap(d, text, hf, x1 - x0)
    while max(d.textlength(l, font=hf) for l in lines) > x1 - x0:  # a single word wider than the column
        hf = font(SERIF, hf.size - 10)
        lines = wrap(d, text, hf, x1 - x0)
    lh = HEAD_LH * hf.size // HEAD
    sub_lines = wrap(d, sub, sf, x1 - x0) if sub else []
    total = len(lines) * lh + (60 + len(sub_lines) * SUB_LH if sub else 0) + extra
    y = y_center - total // 2
    for line in lines:
        d.text((x0, y), line, font=hf, fill=t.hex["ink"])
        y += lh
    if sub:
        y += 20
        d.line((x0, y, x0 + 220, y), fill=t.hex["accent"], width=6)
        y += 40
        for line in sub_lines:
            d.text((x0, y), line, font=sf, fill=t.hex["ink"])
            y += SUB_LH
    return y


def pill(d, x, y, text, f, fill, ink, pad, radius=None, outline=None):
    """Rounded label with its top-left at (x, y). Returns its box."""
    b = d.textbbox((0, 0), text, font=f)
    box = (x, y, x + b[2] - b[0] + 2 * pad[0], y + b[3] - b[1] + 2 * pad[1])
    r = radius if radius is not None else (box[3] - box[1]) // 2
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=4 if outline else 0)
    d.text((x + pad[0] - b[0], y + pad[1] - b[1]), text, font=f, fill=ink)
    return box


def badges(img, t, items, x, y):
    d = ImageDraw.Draw(img)
    f = font(SEMI, 54)
    for text in items:
        y = pill(d, x, y, text, f, t.hex["accent"], t.hex["bg"], (40, 22), radius=40)[3] + 26
    return y


def badge_h():
    b = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), "FULLY HYPERLINKED", font=font(SEMI, 54))
    return b[3] - b[1] + 44


def markers(img, t, page, origin, zoom, targets):
    """Tap markers on link rects. targets: [(dest page no, filter(rect), on_text, label, side)].
    on_text centers the marker on the words inside the rect (tab and week labels) instead of the rect."""
    over = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    f = font(SEMI, 40)
    words = page.get_text("words")
    for pno, keep, on_text, label, side in targets:
        r = next(l["from"] for l in page.get_links() if l.get("page") == pno and keep(l["from"]))
        if on_text:
            r = pymupdf.Rect(next(w[:4] for w in words if pymupdf.Rect(w[:4]) in r))
        cx, cy = origin[0] + (r.x0 + r.x1) / 2 * zoom, origin[1] + (r.y0 + r.y1) / 2 * zoom
        d.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), outline=rgba(t.hex["panel"]), width=4)  # visible on accent tabs
        d.ellipse((cx - 46, cy - 46, cx + 46, cy + 46), fill=rgba(t.hex["accent"], 0.35),
                  outline=rgba(t.hex["accent"]), width=10)
        b = d.textbbox((0, 0), label, font=f)
        w, h = b[2] - b[0] + 56, b[3] - b[1] + 32
        x, y = {"right": (cx + 66, cy - h / 2), "left": (cx - 66 - w, cy - h / 2),
                "above": (cx - 46, cy - 66 - h)}[side]
        pill(d, x, y, label, f, t.hex["panel"], t.hex["ink"], (28, 16), outline=t.hex["accent"])
    img.alpha_composite(over)


def thumb(img, page, x, y, h, border, width):
    """Page render with rounded corners and a border, top-left at (x, y). Returns its box."""
    shot, _ = render(page, h)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, shot.width - 1, shot.height - 1), 14, fill=255)
    img.paste(shot, (x, y), mask)
    box = (x, y, x + shot.width - 1, y + shot.height - 1)
    ImageDraw.Draw(img).rounded_rectangle(box, 14, outline=border, width=width)
    return box


def caption(img, text, f, fill, cx, y):
    ImageDraw.Draw(img).text((cx, y), text, font=f, fill=fill, anchor="ma")


def grid(n_cols, w, gap_x, y0, row_h):
    x0 = (SIZE[0] - n_cols * w - (n_cols - 1) * gap_x) // 2
    return lambda i: (x0 + i % n_cols * (w + gap_x), y0 + i // n_cols * row_h)


def set_title(set_key):
    return {"2027": "2027", "2027-2028": "2027–2028", "undated": "Undated"}[set_key]


def make(out, set_key, theme_key):
    t = Theme(theme_key)
    doc = pymupdf.open(pdf_path(out, set_key, theme_key, "portrait", "mon"))
    names = {k: v["page"] for k, v in doc.resolve_names().items()}
    plan = cu.make_plan(set_key, "mon")
    y0 = plan.years[0]
    day = (y0, 3, 15)
    week = 10 if y0 == "u" else plan.week_of[day]
    month = doc[names[cu.month_dest(y0, 3)]]
    d = out / "mockups" / f"{set_key}_{theme_key}"
    d.mkdir(parents=True, exist_ok=True)
    W, H = SIZE
    new = lambda: Image.new("RGBA", SIZE, t.hex["bg"])
    save = lambda img, name: img.convert("RGB").save(d / f"{name}.png")

    # 01 cover: rotated month page behind the cover page
    img = new()
    front_right = W - 160
    back, _ = device(month, 1900)
    back = back.rotate(-6, expand=True, resample=Image.BICUBIC)
    bx = front_right - 300 - back.width  # 380 pushes the back tablet into the badges
    place(img, back, bx, (H - back.height) // 2 - 70)
    tablet(img, doc[names["cover"]], 2150, front_right)
    items = ["FULLY HYPERLINKED", f"{DAILY[set_key]} DAILY PAGES", "PORTRAIT + LANDSCAPE"]
    y = headline(img, t, f"{set_title(set_key)} Digital Planner", None, 140, bx + 60, H // 2,
                 extra=60 + len(items) * (badge_h() + 26) - 26)
    badges(img, t, items, 140, y + 60)
    save(img, "01_cover")

    # 02 links: month page with tap markers on real link rects
    img = new()
    x, origin, zoom = tablet(img, month, 2150, W - 200)
    pw = month.rect.width
    markers(img, t, month, origin, zoom, [
        (names[cu.month_dest(y0, 3)], lambda r: r.x0 >= pw - TAB_W, True, "Month tabs", "left"),
        (names[cu.day_dest(*day)], lambda r: True, False, "Tap a date", "right"),
        (names[cu.week_dest(plan.week_of[day])], lambda r: True, True, "Jump to week", "above"),
    ])
    headline(img, t, "Every Date Is Clickable", "Tabs, months, weeks and days all linked", 200, x - 160, H // 2)
    save(img, "02_links")

    shots = {
        "03_year": (cu.year_dest(y0), "Year at a Glance"),
        "04_week": (cu.week_dest(week), "Weekly Planning"),
        "05_day": (cu.day_dest(*day), "Daily Pages for Every " + ("Month" if y0 == "u" else "Day")),
    }
    for fname, (dest, head) in shots.items():
        img = new()
        x, _, _ = tablet(img, doc[names[dest]], 2150, W - 200)
        headline(img, t, head, None, 200, x - 160, H // 2)
        save(img, fname)

    img = new()
    headline(img, t, "What's Included", None, 240, W - 240, 330)
    text_list(img, t, INCLUDED, 2, 300, W - 240, 640)
    save(img, "06_included")
    img = new()
    headline(img, t, "Works In Your Favorite App", None, 240, W - 240, 330)
    text_list(img, t, APPS, 2, 300, W - 240, 760)
    save(img, "07_apps")

    # 08 pages: 3x2 grid of page types
    img = new()
    headline(img, t, f"{len(doc) // 50 * 50}+ Pages", None, 200, W - 200, 260)
    pages = [(cu.year_dest(y0), "Year"), (cu.month_dest(y0, 3), "Month"), (cu.week_dest(week), "Week"),
             (cu.day_dest(*day), "Day"), (cu.habit_dest(y0, 3), "Habits"), (cu.budget_dest(y0, 3), "Budget")]
    cf = font(REG, 48)
    at = grid(3, 450, 220, 470, 860)
    for i, (dest, label) in enumerate(pages):
        x, y = at(i)
        b = thumb(img, doc[names[dest]], x, y, 600, t.hex["line"], 8)
        caption(img, label, cf, t.hex["ink"], (b[0] + b[2]) // 2, b[3] + 30)
    save(img, "08_pages")

    # 09 colors: covers of every theme
    img = new()
    headline(img, t, "Available in 8 Colors", None, 200, W - 200, 260)
    sf = font(SEMI, 48)
    at = grid(4, 465, 150, 450, 860)
    for i, th in enumerate(THEMES):
        x, y = at(i)
        tt = Theme(th)
        with pymupdf.open(pdf_path(out, set_key, th, "portrait", "mon")) as other:
            cover = other[{k: v["page"] for k, v in other.resolve_names().items()}["cover"]]
            mine = th == theme_key
            b = thumb(img, cover, x, y, 620, t.hex["accent"] if mine else t.hex["line"], 12 if mine else 8)
        cx = (b[0] + b[2]) // 2
        caption(img, tt.display, cf, t.hex["ink"], cx, b[3] + 30)
        if mine:
            caption(img, "This listing", sf, t.hex["accent"], cx, b[3] + 96)
    save(img, "09_colors")
    doc.close()
    return d


def text_list(img, t, items, cols, x0, x1, y0):
    d = ImageDraw.Draw(img)
    f = font(REG, 76)
    per = (len(items) + cols - 1) // cols
    cw = (x1 - x0) // cols
    for i, item in enumerate(items):
        c, r = divmod(i, per)
        x, y = x0 + c * cw, y0 + r * 150
        d.ellipse((x, y + 30, x + 28, y + 58), fill=t.hex["accent"])
        d.text((x + 64, y), item, font=f, fill=t.hex["ink"])
