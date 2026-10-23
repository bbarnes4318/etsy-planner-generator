import argparse
import itertools
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .config import ORIENTATIONS, SETS, THEMES, WEEK_STARTS, pdf_path

OUT = Path(__file__).resolve().parent.parent / "out"


def _build(args):
    from .builder import build
    path = pdf_path(OUT, *args)
    build(*args, path)
    return path


def _mockups(args):
    from .mockups import make
    return make(OUT, *args)


def cmd_build(a):
    print(_build((a.set, a.theme, a.orientation, a.week_start)))


def cmd_build_all(a):
    from .listing import bundle
    from .verify import report
    combos = list(itertools.product(SETS, THEMES, ORIENTATIONS, WEEK_STARTS))
    t = time.time()
    with ProcessPoolExecutor(a.jobs) as ex:
        paths = []
        for i, p in enumerate(ex.map(_build, combos), 1):
            paths.append(p)
            print(f"[{i}/{len(combos)}] {p.relative_to(OUT)}", flush=True)
    print(f"built {len(paths)} PDFs in {time.time() - t:.0f}s\n")
    for s, th in itertools.product(SETS, THEMES):
        bundle(OUT, s, th)
    print(f"wrote {len(SETS) * len(THEMES)} Etsy bundles to {OUT / 'etsy'}\n")
    if not report(paths):
        sys.exit(1)


def cmd_mockups(a):
    sets = [a.set] if a.set else SETS
    themes = [a.theme] if a.theme else THEMES
    combos = list(itertools.product(sets, themes))
    for s, th in combos:
        if not pdf_path(OUT, s, th, "portrait", "mon").exists():
            _build((s, th, "portrait", "mon"))
    with ProcessPoolExecutor(a.jobs) as ex:
        for d in ex.map(_mockups, combos):
            print(d)


def cmd_listings(a):
    from .listing import write_csv
    print(write_csv(OUT))


def cmd_verify(a):
    from .verify import report
    if not report(a.pdfs):
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(prog="python -m planner")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build one planner PDF")
    b.add_argument("--set", choices=SETS, required=True)
    b.add_argument("--theme", choices=THEMES, required=True)
    b.add_argument("--orientation", choices=ORIENTATIONS, default="portrait")
    b.add_argument("--week-start", choices=WEEK_STARTS, default="mon")
    b.set_defaults(fn=cmd_build)
    ba = sub.add_parser("build-all", help="build all 96 PDFs, Etsy bundles, then verify")
    ba.add_argument("--jobs", type=int, default=os.cpu_count())
    ba.set_defaults(fn=cmd_build_all)
    m = sub.add_parser("mockups", help="listing images (all sets/themes if omitted)")
    m.add_argument("--set", choices=SETS)
    m.add_argument("--theme", choices=THEMES)
    m.add_argument("--jobs", type=int, default=os.cpu_count())
    m.set_defaults(fn=cmd_mockups)
    sub.add_parser("listings", help="write out/listings.csv").set_defaults(fn=cmd_listings)
    v = sub.add_parser("verify", help="check links, page counts and size")
    v.add_argument("pdfs", nargs="+")
    v.set_defaults(fn=cmd_verify)
    a = p.parse_args()
    a.fn(a)
