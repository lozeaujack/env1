#!/usr/bin/env python3
"""Make every slide in a Google Slides deck follow one house style.

Input : a masked read of the deck saved as JSON (see README.md for the mask).
Output: the `requests` list for Slides `batchUpdate`, wrapped with the revision guard.

Usage:
  python3 style_deck.py deck.json --revision <revisionId> [--style deck_style.json] [--dry-run]

What it sets, per slide (slides in `skip_slide_ids` are left alone):
  * background colour (paper for content slides, navy for dark layouts)
  * title placeholders  -> font, size, bold, colour
  * body/subtitle placeholders -> font, size, colour
  * every other text box / shape -> font and colour only (your sizes and bold stay)
  * footnote-sized text (<= 12 pt) -> muted colour
  * table cells -> font and colour, header row bold
Text is never shrunk below your own size except placeholders, which take the style sizes.
"""
import argparse, json, re, sys, pathlib

def rgb(h):
    h = h.lstrip('#')
    return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}

def color_obj(h):
    return {"opaqueColor": {"rgbColor": rgb(h)}}

def text_of(shape_or_cell):
    els = (shape_or_cell.get("text") or {}).get("textElements") or []
    return "".join(e.get("textRun", {}).get("content", "") for e in els)

def max_size(shape):
    sizes = []
    for e in (shape.get("text") or {}).get("textElements") or []:
        s = e.get("textRun", {}).get("style", {}).get("fontSize", {}).get("magnitude")
        if s: sizes.append(s)
    return max(sizes) if sizes else None

def any_bold(shape):
    return any(e.get("textRun", {}).get("style", {}).get("bold") for e in (shape.get("text") or {}).get("textElements") or [])

def style_req(oid, font, color, size=None, bold=None, cell=None):
    style = {"fontFamily": font, "foregroundColor": color_obj(color)}
    fields = ["fontFamily", "foregroundColor"]
    if size is not None:
        style["fontSize"] = {"magnitude": size, "unit": "PT"}; fields.append("fontSize")
    if bold is not None:
        style["bold"] = bold; fields.append("bold")
    r = {"objectId": oid, "textRange": {"type": "ALL"}, "style": style, "fields": ",".join(fields)}
    if cell: r["cellLocation"] = cell
    return {"updateTextStyle": r}

def C_note(is_note, fn, t):
    return fn["color"] if is_note else t["color"]

def decor(deck, st):
    """Visual layer: edge stripe, footer bar with page numbers, banded table headers, white cards.
    Decor objects have ids starting 'deco_'; they are deleted and rebuilt on every run, so re-running is safe."""
    D = st["decor"]; C = st["colors"]; W, H = D["page_w"], D["page_h"]
    layouts = {l["objectId"]: l.get("layoutProperties", {}).get("name", "") for l in deck.get("layouts", [])}
    slides = deck.get("slides", []); N = len(slides); out = []
    def box(oid, sid, x, y, w, h, fill, kind="RECTANGLE"):
        return [{"createShape": {"objectId": oid, "shapeType": kind, "elementProperties": {"pageObjectId": sid,
                   "size": {"width": {"magnitude": w, "unit": "EMU"}, "height": {"magnitude": h, "unit": "EMU"}},
                   "transform": {"scaleX": 1, "scaleY": 1, "translateX": x, "translateY": y, "unit": "EMU"}}}},
                {"updateShapeProperties": {"objectId": oid, "fields": "shapeBackgroundFill,outline",
                   "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(fill)}}}, "outline": {"propertyState": "NOT_RENDERED"}}}}]
    for idx, sl in enumerate(slides):
        sid = sl["objectId"]
        if sid in st.get("skip_slide_ids", []): continue
        for el in sl.get("pageElements", []):          # clear old decor
            if el["objectId"].startswith("deco_"): out.append({"deleteObject": {"objectId": el["objectId"]}})
        layout = layouts.get(sl.get("slideProperties", {}).get("layoutObjectId", ""), "")
        if layout in st.get("dark_layouts", []): continue
        if D.get("edge_stripe"): out += box(f"deco_{idx}_edge", sid, 0, 0, 110000, H, C["green"])
        if D.get("footer"):
            fh = 300000; out += box(f"deco_{idx}_foot", sid, 0, H - fh, W, fh, C["navy"])
            out += box(f"deco_{idx}_ftxt", sid, 330000, H - fh, W - 660000, fh, C["navy"])
            label = f"{D['team']}  ·  {idx+1} / {N}"
            out += [{"insertText": {"objectId": f"deco_{idx}_ftxt", "text": label}},
                    {"updateTextStyle": {"objectId": f"deco_{idx}_ftxt", "textRange": {"type": "ALL"}, "fields": "fontFamily,fontSize,bold,foregroundColor",
                       "style": {"fontFamily": st["font"], "fontSize": {"magnitude": 10, "unit": "PT"}, "bold": True, "foregroundColor": color_obj(C["white"])}}},
                    {"updateParagraphStyle": {"objectId": f"deco_{idx}_ftxt", "textRange": {"type": "ALL"}, "fields": "alignment", "style": {"alignment": "END"}}},
                    {"updateShapeProperties": {"objectId": f"deco_{idx}_ftxt", "fields": "contentAlignment", "shapeProperties": {"contentAlignment": "MIDDLE"}}}]
        for el in sl.get("pageElements", []):
            oid = el["objectId"]
            if oid.startswith("deco_"): continue
            if D.get("table_style") and "table" in el:
                rows = el["table"].get("tableRows", []); ncol = max((len(r.get("tableCells", [])) for r in rows), default=0)
                if not rows or not ncol: continue
                hdr = {"tableRange": {"location": {"rowIndex": 0, "columnIndex": 0}, "rowSpan": 1, "columnSpan": ncol}}
                out.append({"updateTableCellProperties": {"objectId": oid, "fields": "tableCellBackgroundFill", **hdr,
                    "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(C["navy"])}}}}}})
                out.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"}, "fields": "foregroundColor,bold",
                    "cellLocation": None, "style": {}}}) if False else None
                for c in range(ncol):
                    out.append({"updateTextStyle": {"objectId": oid, "cellLocation": {"rowIndex": 0, "columnIndex": c}, "textRange": {"type": "ALL"},
                        "fields": "foregroundColor,bold", "style": {"bold": True, "foregroundColor": color_obj(C["white"])}}})
                for r in range(1, len(rows)):
                    band = C["white"] if r % 2 else C["paper"]
                    out.append({"updateTableCellProperties": {"objectId": oid, "fields": "tableCellBackgroundFill",
                        "tableRange": {"location": {"rowIndex": r, "columnIndex": 0}, "rowSpan": 1, "columnSpan": ncol},
                        "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(band)}}}}}})
            elif D.get("cards") and "shape" in el and not el["shape"].get("placeholder"):
                sh = el["shape"]
                if sh.get("shapeType") not in ("TEXT_BOX", "RECTANGLE", "ROUND_RECTANGLE"): continue
                t = text_of(sh)
                if len(t.strip()) < D.get("card_min_chars", 25): continue
                fn = st["text"]["footnote"]
                if any(k in oid.lower() for k in fn.get("id_contains", [])) or any(re.search(p, t, re.I) for p in fn.get("patterns", [])): continue
                out.append({"updateShapeProperties": {"objectId": oid, "fields": "shapeBackgroundFill,outline",
                    "shapeProperties": {"shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(C["white"])}}},
                        "outline": {"outlineFill": {"solidFill": {"color": {"rgbColor": rgb(C["navy"])}}}, "weight": {"magnitude": 1.5, "unit": "PT"}}}}})
    return out

def build(deck, st, revision):
    C = st["colors"]; font = st["font"]; T = st["text"]
    reqs, log = [], []
    layouts = {l["objectId"]: l.get("layoutProperties", {}).get("name", "") for l in deck.get("layouts", [])}
    for idx, slide in enumerate(deck.get("slides", [])):
        sid = slide["objectId"]
        if sid in st.get("skip_slide_ids", []):
            log.append(f"slide {idx+1} ({sid}): skipped"); continue
        layout = layouts.get(slide.get("slideProperties", {}).get("layoutObjectId", ""), "")
        dark = layout in st.get("dark_layouts", [])
        bg = C[st["backgrounds"]["dark" if dark else "content"]]
        txt_col = C[st["dark_text_color"]] if dark else None
        reqs.append({"updatePageProperties": {"objectId": sid,
            "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(bg)}}}},
            "fields": "pageBackgroundFill.solidFill.color"}})
        n = 0
        for el in slide.get("pageElements", []):
            oid = el["objectId"]
            if "shape" in el:
                sh = el["shape"]; content = text_of(sh)
                if not content.strip(): continue
                ph = (sh.get("placeholder") or {}).get("type", "")
                size = max_size(sh); floor = st.get("min_size", 10)
                fn = T["footnote"]
                is_note = (any(k in oid.lower() for k in fn.get("id_contains", []))
                           or any(re.search(p, content, re.I) for p in fn.get("patterns", [])))
                if ph in ("TITLE", "CENTERED_TITLE"):
                    t = T["title"]; col = txt_col or C[t["color"]]
                    reqs.append(style_req(oid, font, col, t["size"], t["bold"])); role = "title"
                elif ph in ("BODY", "SUBTITLE"):
                    t = T["body_long"] if len(content) > T["body_long"]["_when_chars_over"] else T["body"]
                    col = txt_col or C[C_note(is_note, fn, t)]
                    use = max(size, floor) if size else t["size"]
                    reqs.append(style_req(oid, font, col, use, (True if any_bold(sh) else None) if size else t["bold"])); role = "body"
                else:
                    col = txt_col or C[fn["color"] if is_note else "navy"]
                    use = floor if (size is not None and size < floor) else None
                    reqs.append(style_req(oid, font, col, use, True if any_bold(sh) else None)); role = "footnote" if is_note else "text"
                    if use: role += f" (raised {size:g}->{floor} pt)"
                n += 1
                log.append(f"slide {idx+1}: {oid} -> {role}")
            elif "table" in el:
                tb = el["table"]
                for r, row in enumerate(tb.get("tableRows", [])):
                    for cell in row.get("tableCells", []):
                        if not text_of(cell).strip(): continue
                        loc = {"rowIndex": r, "columnIndex": (cell.get("location") or {}).get("columnIndex", 0)}
                        col = txt_col or C[T["table"]["color"]]
                        reqs.append(style_req(oid, font, col, bold=(True if (r == 0 and T["table"]["header_bold"]) else None), cell=loc))
                log.append(f"slide {idx+1}: {oid} -> table")
    reqs = decor(deck, st) + reqs if st.get("decor", {}).get("enabled") else reqs
    return {"requests": reqs, "writeControl": {"requiredRevisionId": revision}}, log

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck"); ap.add_argument("--revision", required=True)
    ap.add_argument("--style", default=str(pathlib.Path(__file__).with_name("deck_style.json")))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    raw = json.load(open(a.deck))
    deck = raw.get("content", raw)
    st = json.load(open(a.style))
    out, log = build(deck, st, a.revision)
    print("\n".join(log), file=sys.stderr)
    print(f"{len(out['requests'])} requests", file=sys.stderr)
    if not a.dry_run:
        print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__":
    main()
