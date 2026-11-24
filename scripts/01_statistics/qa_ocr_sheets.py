#!/usr/bin/env python3
"""QA contact sheets: for every OCR row that was re-read, show the row as printed in the bulletin
next to the values finally accepted, so a person can confirm the re-read by eye.
usage: qa_ocr_sheets.py <bem_dir> <out_dir> <sheet_dir> YYYY-MM ..."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
import numpy as np, cv2, pymupdf
import viogen_extract as V

_orig = V._read_cell
def _labels_only(gray_cell, numeric, label_table=None):
    return ('', 0, 0) if numeric else _orig(gray_cell, numeric, label_table)
V._read_cell = _labels_only            # grid + labels only: numbers come from the saved JSON

bem, out, sheets = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
sheets.mkdir(parents=True, exist_ok=True)
for ym in sys.argv[4:]:
    r = json.load(open(out / 'json' / f'{ym}.json'))
    doc = pymupdf.open(bem / r['file'])
    panels = []
    for kind, t in r['tables'].items():
        log = t.get('ocr_resolution_log', [])
        if not log or t.get('status') != 'reconciled':      # only tables that enter the panels
            continue
        words, hdr, grid = V.ocr_grid_words(doc[t['pdf_page'] - 1], kind)
        g, xs, ys, H, W = grid['gray'], grid['xs'], grid['ys'], grid['H'], grid['W']
        table = V.TERR if kind == 'territory' else V.FORCE
        yb = {}
        for w in words:
            hit = V.match_label(w[4], table)
            if hit and hit[0] not in yb and w[0] < xs[1] / W:
                yb[hit[0]] = (w[1], w[3])
        for lg in log:
            if lg['unit'] not in yb:
                continue
            a = min(ys, key=lambda y: abs(y / H - yb[lg['unit']][0]))
            b = min(ys, key=lambda y: abs(y / H - yb[lg['unit']][1]))
            strip = cv2.cvtColor(g[a - 2:b + 3, xs[0]:xs[-1]], cv2.COLOR_GRAY2BGR)
            strip = cv2.resize(strip, None, fx=1.6, fy=1.6, interpolation=cv2.INTER_CUBIC)
            band = np.full((34, strip.shape[1], 3), 255, np.uint8)
            cols = t['columns']
            for i, c in enumerate(cols):
                x = int((xs[i + 1] - xs[0]) * 1.6) + 4
                v = lg['after'].get(c)
                changed = lg['before'].get(c) != v
                cv2.putText(band, '' if v is None else str(v), (x, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (0, 0, 200) if changed else (90, 90, 90), 2 if changed else 1, cv2.LINE_AA)
            head = np.full((26, strip.shape[1], 3), 255, np.uint8)
            cv2.putText(head, f"{ym} {kind}: {lg['unit']}  (red = value changed by the re-read)", (4, 19),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
            panels.append(np.vstack([head, strip, band]))
    if panels:
        w = max(p.shape[1] for p in panels)
        panels = [cv2.copyMakeBorder(p, 0, 10, 0, w - p.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for p in panels]
        cv2.imwrite(str(sheets / f'qa_ocr_rereads_{ym}.png'), np.vstack(panels))
        print(ym, len(panels), 'rows')
