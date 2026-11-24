#!/usr/bin/env python3
"""Run the VioGén extraction over every downloaded monthly bulletin and save one JSON per month.

usage: run_batch.py <bem_dir> <out_dir> [--kinds=force] <YYYY-MM> [<YYYY-MM> ...]
--kinds=force reads only the police-institution table where the tables are images (used for Jun 2020 -
Oct 2021, where the territorial image tables were not extracted).
"""
import sys, json, time, traceback, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pymupdf
import viogen_extract as V
import viogen_ocr_resolve as R

def ocr_find_pages(doc):
    """Image-only bulletins: identify the two main tables by OCR of each page's header band."""
    import numpy as np, cv2, pytesseract
    from PIL import Image
    found = {}
    for pno in range(30, min(len(doc), 100)):
        page = doc[pno]
        if len(page.get_text().strip()) > 200 or not page.get_images():
            continue
        g = V.page_table_image(page)
        if g is None:
            continue
        top = cv2.resize(g[: int(g.shape[0] * 0.13)], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        tk = V.key(pytesseract.image_to_string(Image.fromarray(top), lang='spa', config='--psm 6'))
        if 'territory' not in found and 'distribucionterritorial' in tk and 'todoslospaises' in tk \
                and 'todaslasedades' in tk:
            found['territory'] = pno
        elif 'force' not in found and 'cuerpospoliciales' in tk:
            found['force'] = pno
        if len(found) == 2:
            break
    return found

def process(bem_dir, out_dir, ym, kinds=('territory', 'force')):
    y, m = int(ym[:4]), int(ym[5:])
    fname = f'BEM_{V.MONTHS_ES[m-1]}_{y}.pdf'
    path = Path(bem_dir) / fname
    res = {'month': ym, 'file': fname, 'url': V.BEM_URL.format(m=V.MONTHS_ES[m-1], y=y), 'tables': {}}
    if not path.exists():
        res['error'] = 'bulletin PDF not available'
        return res
    doc = pymupdf.open(path)
    res['n_pages'] = len(doc)
    found = V.find_pages(doc, use_ocr=False, search=range(20, len(doc)))
    methods = {k: 'pdf text layer' for k in found}
    if len(found) < 2:
        # image-only tables (e.g. Jun 2020 - Oct 2021 in part, Mar 2026 onwards): find them by OCR
        for k, p in ocr_find_pages(doc).items():
            if k not in found:
                found[k] = (p, None, None)
                methods[k] = 'OCR (embedded table image)'
    for kind in ('territory', 'force'):
        method = methods.get(kind, 'pdf text layer')
        t = {'method': method}
        if kind not in kinds and method.startswith('OCR'):
            t['status'] = 'image table not extracted (OCR not attempted)'
            t['pdf_page'] = found[kind][0] + 1
            res['tables'][kind] = t
            continue
        if kind not in found:
            t['status'] = ('image table not extracted (OCR not attempted)' if kind not in kinds
                           else 'table not present in bulletin')
            res['tables'][kind] = t
            continue
        pno = found[kind][0]
        t['pdf_page'] = pno + 1
        try:
            if method.startswith('OCR'):
                words, hdr, grid = V.ocr_grid_words(doc[pno], kind)
                protocol, ddate, cols, parsed, probs = V.parse_table(words, kind, hdr)
                t['fails_first_pass'] = V.reconcile(parsed, cols, protocol, kind)
                log = []
                t['ocr_rows_reread'] = R.resolve(parsed, cols, protocol, grid, words, log)
                t['ocr_resolution_log'] = log
                t['ocr_cells'] = len([w for w in words if V.NUM_RE.match(w[4])])
                t['ocr_unreadable_cells'] = len([w for w in words if w[4] == '?'])
            else:
                protocol, ddate, cols, parsed, probs = V.parse_table(found[kind][1], kind)
            # a cell printed as '1E+05' (spreadsheet artefact) is unreadable; for the force table's
            # TOTAL row only, take that cell from the reconciled territorial TOTAL of the SAME bulletin
            # and the SAME date, and record that substitution.
            t['printed_artefacts'] = []
            terr = res['tables'].get('territory', {})
            for name, rec in parsed.items():
                for sc in rec.get('sci_cells', []):
                    entry = {'unit': name, 'column': sc['column'], 'printed': sc['printed']}
                    if kind == 'force' and name == 'TOTAL' and terr.get('status') == 'reconciled' \
                            and terr.get('data_date') == ddate:
                        rec['values'][sc['column']] = terr['units']['TOTAL']['values'][sc['column']]
                        entry['filled_from'] = 'territorial TOTAL row, same bulletin and date'
                    t['printed_artefacts'].append(entry)
            fails = V.reconcile(parsed, cols, protocol, kind)
            t.update({'protocol': protocol, 'data_date': ddate, 'columns': cols, 'problems': probs,
                      'fails': fails, 'status': 'reconciled' if not fails and not probs else 'failed checks',
                      'units': {k: {'printed_label': v['printed_label'], 'kind': v['kind'],
                                    'region': v['region'], 'values': V.full_values(v, cols),
                                    'cells_present': sorted(v['values']),
                                    'ocr_resolved': v.get('ocr_resolved', False)}
                                for k, v in parsed.items()}})
        except Exception as e:
            t['status'] = 'extraction error'
            t['error'] = f'{type(e).__name__}: {e}'
            t['trace'] = traceback.format_exc()[-1500:]
        res['tables'][kind] = t
    # keep the table pages as source evidence (small PDF excerpt)
    pages = sorted(t['pdf_page'] - 1 for t in res['tables'].values() if 'pdf_page' in t)
    if pages:
        ex = pymupdf.open()
        for p in pages:
            ex.insert_pdf(doc, from_page=p, to_page=p)
        Path(out_dir, 'sources').mkdir(parents=True, exist_ok=True)
        ex.save(Path(out_dir, 'sources', f'{ym}_{fname[:-4]}_VioGen_pages_{"-".join(str(p+1) for p in pages)}.pdf'))
    return res

if __name__ == '__main__':
    bem_dir, out_dir = sys.argv[1], sys.argv[2]
    Path(out_dir, 'json').mkdir(parents=True, exist_ok=True)
    kinds = ('territory', 'force')
    args = [a for a in sys.argv[3:] if not a.startswith('--')]
    for a in sys.argv[3:]:
        if a.startswith('--kinds='):
            kinds = tuple(a.split('=', 1)[1].split(','))
    for ym in args:
        t0 = time.time()
        r = process(bem_dir, out_dir, ym, kinds)
        r['seconds'] = round(time.time() - t0, 1)
        Path(out_dir, 'json', f'{ym}.json').write_text(json.dumps(r, ensure_ascii=False, indent=1))
        st = {k: v.get('status') for k, v in r.get('tables', {}).items()}
        print(ym, r.get('error', ''), st, r['seconds'], 's', flush=True)
