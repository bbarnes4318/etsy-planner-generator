import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import calendar_util as cu
from .config import Theme, pdf_path
from .fonts import DIR, REG, SERIF

SIZE = (3000, 2250)
BEZEL, RADIUS, FRAME = 60, 90, "#1A1A1A"
INCLUDED = ["Year Overview", "Monthly Calendars", "Weekly Pages", "Daily Pages", "Goals",
            "Habit Trackers", "Monthly Budget", "50 Notes Pages", "Portrait + Landscape",
            "Monday + Sunday Start"]
APPS = ["GoodNotes", "Notability", "Noteshelf", "Samsung Notes", "Xodo", "reMarkable"]


def font(name, size):
    return ImageFont.truetype(str(DIR / f"{name}.ttf"), size)


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


def tablet(img, page, box_h, right):
    """Paste a framed page render, vertically centered, its right edge at `right`."""
    screen_h = box_h - 2 * BEZEL
    zoom = screen_h / page.rect.height
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    shot = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    fw, fh = shot.width + 2 * BEZEL, shot.height + 2 * BEZEL
    x, y = right - fw, (SIZE[1] - fh) // 2
    shadow = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x + 30, y + 30, x + fw + 30, y + fh + 30), RADIUS,
                                             fill=(0, 0, 0, int(255 * 0.35)))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(40)))
    ImageDraw.Draw(img).rounded_rectangle((x, y, x + fw, y + fh), RADIUS, fill=FRAME)
    img.paste(shot, (x + BEZEL, y + BEZEL))
    return x


def headline(img, t, text, sub, x0, x1, y_center):
    d = ImageDraw.Draw(img)
    hf, sf = font(SERIF, 150), font(REG, 64)
    lines = wrap(d, text, hf, x1 - x0)
    sub_lines = wrap(d, sub, sf, x1 - x0) if sub else []
    total = len(lines) * 175 + (40 + len(sub_lines) * 86 if sub else 0)
    y = y_center - total // 2
    for line in lines:
        d.text((x0, y), line, font=hf, fill=t.hex["ink"])
        y += 175
    if sub:
        y += 20
        d.line((x0, y, x0 + 220, y), fill=t.hex["accent"], width=6)
        y += 40
        for line in sub_lines:
            d.text((x0, y), line, font=sf, fill=t.hex["ink"])
            y += 86


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


def set_title(set_key):
    return {"2027": "2027", "2027-2028": "2027–2028", "undated": "Undated"}[set_key]


def make(out, set_key, theme_key):
    t = Theme(theme_key)
    src = pdf_path(out, set_key, theme_key, "portrait", "mon")
    doc = pymupdf.open(src)
    names = {k: v["page"] for k, v in doc.resolve_names().items()}
    plan = cu.make_plan(set_key, "mon")
    y0 = plan.years[0]
    day = (y0, 3, 15)
    week = 10 if y0 == "u" else plan.week_of[day]
    shots = {
        "01_cover": ("cover", f"{set_title(set_key)} Digital Planner", f"{t.display} • Fully Hyperlinked"),
        "02_links": (cu.month_dest(y0, 3), "Every Date Is Clickable", "Tabs, months, weeks and days all linked"),
        "03_year": (cu.year_dest(y0), "Year at a Glance", None),
        "04_week": (cu.week_dest(week), "Weekly Planning", None),
        "05_day": (cu.day_dest(*day), "Daily Pages for Every " + ("Month" if y0 == "u" else "Day"), None),
    }
    d = out / "mockups" / f"{set_key}_{theme_key}"
    d.mkdir(parents=True, exist_ok=True)
    W, H = SIZE
    for fname, (dest, head, sub) in shots.items():
        img = Image.new("RGBA", SIZE, t.hex["bg"])
        x = tablet(img, doc[names[dest]], 1980, W - 200)
        headline(img, t, head, sub, 200, x - 160, H // 2)
        img.convert("RGB").save(d / f"{fname}.png")
    img = Image.new("RGBA", SIZE, t.hex["bg"])
    headline(img, t, "What's Included", None, 240, W - 240, 330)
    text_list(img, t, INCLUDED, 2, 300, W - 240, 640)
    img.convert("RGB").save(d / "06_included.png")
    img = Image.new("RGBA", SIZE, t.hex["bg"])
    headline(img, t, "Works In Your Favorite App", None, 240, W - 240, 330)
    text_list(img, t, APPS, 2, 300, W - 240, 760)
    img.convert("RGB").save(d / "07_apps.png")
    doc.close()
    return d
