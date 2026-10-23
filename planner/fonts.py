from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

DIR = Path(__file__).resolve().parent.parent / "fonts"
REG, SEMI, SERIF = "Inter-Regular", "Inter-SemiBold", "Playfair-SemiBold"


def register():
    for name in (REG, SEMI, SERIF):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(DIR / f"{name}.ttf")))
