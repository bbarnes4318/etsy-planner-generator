from reportlab.lib.colors import HexColor

SIZES = {"portrait": (768, 1024), "landscape": (1024, 768)}
MARGIN = 32
TAB_W = 52
NAV_H = 44
TAB_GAP = 20   # space between content and tab strip
TOP_GAP = 16   # space between nav bar and content
LINE_W = 0.6

_THEME_HEX = {
    "neutral":    ("Neutral",      "#F7F3EE #FFFFFF #3B3A36 #8A857C #DDD6CC #C8A97E #EFE4D3"),
    "sage":       ("Sage",         "#F3F5F0 #FFFFFF #2F3A33 #7C8A80 #D4DDD5 #8FA98F #DDE8DC"),
    "blush":      ("Blush",        "#FBF4F3 #FFFFFF #4A3838 #9A8282 #EBD9D7 #D8A7A1 #F4DEDB"),
    "navy":       ("Navy",         "#F2F4F8 #FFFFFF #1F2A44 #6B7690 #D3D9E4 #2F4A7A #D6DEEC"),
    "lavender":   ("Lavender",     "#F6F4FA #FFFFFF #3A3450 #857E99 #DCD7E8 #A795C9 #E6DFF2"),
    "terracotta": ("Terracotta",   "#FAF4EF #FFFFFF #45332A #96806F #E6D6CA #C67B5C #F2DCCF"),
    "mono":       ("Minimal Mono", "#FFFFFF #FFFFFF #111111 #777777 #DDDDDD #111111 #EEEEEE"),
    "dark":       ("Dark Mode",    "#1C1C1E #2A2A2D #EDEDED #9A9A9F #3A3A3E #D9B97A #3A342A"),
}
_KEYS = ("bg", "panel", "ink", "muted", "line", "accent", "accent_soft")


class Theme:
    def __init__(self, key):
        self.key = key
        self.display, hexes = _THEME_HEX[key]
        self.hex = dict(zip(_KEYS, hexes.split()))
        for k, v in self.hex.items():
            setattr(self, k, HexColor(v))


THEMES = list(_THEME_HEX)
SETS = ["2027", "2027-2028", "undated"]
ORIENTATIONS = ["portrait", "landscape"]
WEEK_STARTS = ["mon", "sun"]


def set_file_label(set_key):
    return "Undated" if set_key == "undated" else set_key


def pdf_path(out, set_key, theme, orientation, week_start):
    name = "Planner_{}_{}_{}_{}.pdf".format(
        set_file_label(set_key), Theme(theme).display.replace(" ", ""),
        orientation.capitalize(), "MonStart" if week_start == "mon" else "SunStart")
    return out / set_key / theme / name
