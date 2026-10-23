import os

import pymupdf

from . import calendar_util as cu
from .config import TAB_W

MAX_BYTES = 20 * 1024 * 1024


def verify(path):
    """Return (summary dict, list of error strings)."""
    errors = []
    doc = pymupdf.open(path)
    names = {k: v["page"] for k, v in doc.resolve_names().items()}
    page_name = {p: k for k, p in names.items()}
    n = len(doc)
    targets = []  # per page: set of target page numbers
    for pno, page in enumerate(doc):
        tgt = set()
        for ln in page.get_links():
            if ln["kind"] == pymupdf.LINK_NAMED and ln.get("nameddest"):
                p = names.get(ln["nameddest"])
            elif ln["kind"] == pymupdf.LINK_GOTO:
                p = ln["page"]
            else:
                errors.append(f"p{pno + 1}: non-internal link kind {ln['kind']}")
                continue
            if p is None or not 0 <= p < n or p not in page_name:
                errors.append(f"p{pno + 1}: link to missing destination ({ln.get('nameddest') or p})")
            else:
                tgt.add(p)
        if pno > 0 and not page.get_links():
            errors.append(f"p{pno + 1} ({page_name.get(pno)}): no links")
        targets.append(tgt)

    meta = dict(kv.split("=") for kv in doc.metadata.get("keywords", "").split(";") if "=" in kv)
    plan = cu.make_plan(meta["set"], meta["week_start"])
    count = lambda prefix: sum(k.startswith(prefix) for k in names)  # noqa: E731
    for label, got, want in (("daily", count("d-"), len(plan.days)),
                             ("month", count("m-"), len(plan.months)),
                             ("weekly", count("w-"), len(plan.weeks))):
        if got != want:
            errors.append(f"{label} pages: {got} != expected {want}")

    if names.get("index") not in targets[0]:
        errors.append("cover does not link to index")
    for day in plan.days:
        p = names.get(cu.day_dest(*day))
        if p is None:
            continue
        for want in (cu.month_dest(*day[:2]), cu.week_dest(plan.week_of[day])):
            if names.get(want) not in targets[p]:
                errors.append(f"{cu.day_dest(*day)} does not link to {want}")
    for y, m in plan.months:
        p = names.get(cu.month_dest(y, m))
        if p is None:
            continue
        page = doc[p]
        tabs = [ln for ln in page.get_links() if ln["from"].x0 >= page.rect.width - TAB_W - 0.5]
        ok = [ln for ln in tabs if ln.get("page") in page_name]
        if len(tabs) != 16 or len(ok) != 16:
            errors.append(f"{cu.month_dest(y, m)}: {len(ok)}/{len(tabs)} side tabs resolve (want 16)")

    size = os.path.getsize(path)
    if size > MAX_BYTES:
        errors.append(f"file is {size / 1e6:.1f} MB > 20 MB")
    doc.close()
    return {"file": str(path), "pages": n, "mb": size / 1024 / 1024, "links_ok": not errors}, errors


def report(paths):
    """Verify each PDF, print a table, return True if all pass."""
    rows = []
    for p in paths:
        s, errs = verify(p)
        rows.append((s, errs))
    w = max(len(os.path.basename(s["file"])) for s, _ in rows)
    print(f"{'file':<{w}}  pages     MB  result")
    for s, errs in rows:
        print(f"{os.path.basename(s['file']):<{w}}  {s['pages']:>5}  {s['mb']:5.2f}  {'PASS' if not errs else 'FAIL'}")
        for e in errs[:10]:
            print(f"    {e}")
        if len(errs) > 10:
            print(f"    ... {len(errs) - 10} more")
    bad = sum(1 for _, e in rows if e)
    print(f"\n{len(rows) - bad}/{len(rows)} passed")
    return bad == 0
