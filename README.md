# planner-generator

Generates fully hyperlinked, vector-only digital planner PDFs (GoodNotes, Notability, Noteshelf,
Samsung Notes, Xodo, reMarkable), plus Etsy listing images, file bundles and listing copy.

## Setup

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt      # Windows
# .venv/bin/pip install -r requirements.txt        # macOS / Linux
```

Python 3.11+. The static fonts in `fonts/` (Inter, Playfair Display — SIL OFL, licenses alongside)
are committed; they were made with `fonttools varLib.instancer` from the Google Fonts variable files.

## Commands

All output goes to `out/` (gitignored).

| Command | What it does |
|---|---|
| `python -m planner build --set 2027 --theme sage --orientation portrait --week-start mon` | Build one PDF to `out/{set}/{theme}/Planner_{Set}_{Theme}_{Portrait\|Landscape}_{MonStart\|SunStart}.pdf`. `--orientation` defaults to portrait, `--week-start` to mon. |
| `python -m planner build-all [--jobs N]` | Build all 96 PDFs (3 sets × 8 themes × 2 orientations × 2 week starts) in parallel, write the 24 Etsy bundles to `out/etsy/{set}_{theme}/` (4 PDFs + `How_To_Import.pdf`), then verify every PDF and print a summary table. Exits non-zero if any fail. |
| `python -m planner mockups --set 2027 --theme sage` | Write the 9 listing images (3000×2250 PNG) to `out/mockups/{set}_{theme}/`. Omit `--set` / `--theme` to do all of them (24 × 9). Builds any missing portrait Monday-start PDFs first; `09_colors` needs every theme's PDF for the set. |
| `python -m planner listings` | Write `out/listings.csv` (24 rows: folder, title, tags, description). |
| `python -m planner verify out/2027/sage/Planner_2027_Sage_Portrait_MonStart.pdf [...]` | Check one or more PDFs (see below). |

Sets: `2027`, `2027-2028`, `undated`. Themes: `neutral sage blush navy lavender terracotta mono dark`.

## What verify checks

- every internal link resolves to a page that has a named destination
- every page except the cover has at least one link; the cover links to the index
- daily / month / weekly page counts match the date set
- every daily page links to its month and its week
- all 16 side tabs on every month page resolve
- file size ≤ 20 MB (prints page count and size)

The set and week start are read from the PDF's keywords metadata, written at build time.

## Notes

- reportlab links straight to pages; after saving, the builder adds a catalog `/Dests` dictionary
  so the named destinations (`cover`, `m-2027-03`, `d-2027-03-15`, …) exist in the file, and
  re-saves with object streams, which roughly halves file size.
- Undated planners: months use weeks `((m-1)*52//12)+1 .. m*52//12`; week slot `i*7+j+1` in its month
  links to that day (days 29–31 of 4-week months have no week slot; their Week link goes to the
  month's last week).
- 2027–2028 has 105 Monday-start weeks and 106 Sunday-start weeks; the listing says "105–106".
