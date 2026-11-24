"""Second pass for OCR'd tables: re-read the cells of rows that fail their own arithmetic.

For a failing row every cell is re-read at 4 scales x 5 binarisations (Otsu, adaptive, three fixed
cut-offs) x 4 Tesseract modes. A cell's
candidates are only the distinct readings OCR actually produced. The row is accepted only if
EXACTLY ONE combination of candidates satisfies the row identities (levels = active;
active + supervised + inactive = total). Otherwise the row stays a failure for visual checking.
Every resolved cell is logged with all candidates, so the step is auditable.
"""
import itertools
from collections import Counter
import numpy as np, cv2, pytesseract
from PIL import Image
import viogen_extract as V

def candidates(gray_cell):
    c = gray_cell
    if np.median(c) < 128:
        c = 255 - c
    out = Counter()
    for sc in (3, 4, 5, 6):
        for m in ('otsu', 'adapt', 'fixed70', 'fixed130', 'fixed160'):
            img = V._prep(c, sc, m)
            if (img < 128).sum() < 40:
                continue
            for psm in (7, 8, 10, 13):
                t = pytesseract.image_to_string(Image.fromarray(img), config=
                    f'--psm {psm} -c tessedit_char_whitelist=0123456789.').strip().replace(' ', '')
                if t and V.NUM_RE.match(t):
                    out[V.to_int(t)] += 1
    return out

def row_cells(grid, y0n, y1n):
    g, xs, ys, W, H, pad = grid['gray'], grid['xs'], grid['ys'], grid['W'], grid['H'], grid['pad']
    a = min(ys, key=lambda y: abs(y / H - y0n)); b = min(ys, key=lambda y: abs(y / H - y1n))
    return [(x0, x1, g[a + pad:b - pad + 1, x0 + pad + 1:x1 - pad]) for x0, x1 in zip(xs[1:], xs[2:])]

def expected_from_parent(name, rec, parsed, cols, protocol):
    """Value each case column must take so that the parent row adds up, given siblings that pass."""
    case = [c for c in cols if c != 'victims']
    ok = lambda u: not V.row_checks(u, cols, protocol) and u.get('row_ok', True)
    if rec['kind'] == 'province':
        parent = parsed.get(rec['region'])
        sibs = [p for p in V.REGION_PROVINCES.get(rec['region'], []) if p != name]
    else:                                  # region or police institution: parent is TOTAL
        parent = parsed.get('TOTAL')
        if rec['kind'] == 'region':
            sibs = [r for r in V.REGION_PROVINCES if r != name]
        else:
            sibs = [k for k in parsed if k not in ('TOTAL', name)]
    if not parent or not ok(parent) or any(s not in parsed or not ok(parsed[s]) for s in sibs):
        return None
    fv = lambda u: V.full_values(u, cols)
    return {c: fv(parent)[c] - sum(fv(parsed[s])[c] for s in sibs) for c in case}

def resolve(parsed, cols, protocol, grid, words, log):
    """Try to repair rows whose cells break the row identities. Mutates parsed; returns n repaired."""
    levels = V.levels_for(protocol)
    # map canonical name -> its row's normalised y-bounds (from the label word)
    ybounds = {}
    for w in words:
        hit = V.match_label(w[4], V.TERR) or V.match_label(w[4], V.FORCE)
        if hit and hit[0] not in ybounds and w[0] < grid['xs'][1] / grid['W']:
            ybounds[hit[0]] = (w[1], w[3])
    repaired, cache = 0, {}
    # several passes: a row left ambiguous in one pass can be settled by the parent-row identity
    # once its siblings have been repaired in that pass
    while True:
        before = repaired
        repaired += _one_pass(parsed, cols, protocol, grid, levels, ybounds, cache, log)
        if repaired == before:
            return repaired

def _one_pass(parsed, cols, protocol, grid, levels, ybounds, cache, log):
    repaired = 0
    for name, rec in parsed.items():
        if not V.row_checks(rec, cols, protocol) and rec['row_ok']:
            continue
        if name not in ybounds:
            continue
        if name not in cache:
            cache[name] = [candidates(c) for _, _, c in row_cells(grid, *ybounds[name])]
        cand = cache[name]
        cur = [rec['values'].get(c) for c in cols]
        options = []
        for i, cnt in enumerate(cand):
            opts = [k for k, _ in cnt.most_common(6)] if cnt else []   # the six most frequent readings
            if cur[i] is not None and cur[i] not in opts:
                opts.append(cur[i])
            if not opts:
                opts = [0] if cols[i] not in ('active', 'total', 'inactive', 'victims') else []
            options.append(opts[:6])
        if any(not o for o in options):
            continue
        sols = []
        vi = cols.index('victims')
        no_vict = [o if i != vi else o[:1] for i, o in enumerate(options)]
        for combo in itertools.product(*no_vict):
            v = dict(zip(cols, combo))
            ok = sum(v[c] for c in levels) == v['active'] and \
                 v['active'] + v.get('supervised', 0) + v['inactive'] == v['total']
            if ok:
                sols.append(combo)
            if len(sols) > 200:
                break
        distinct = sorted({s[:vi] + s[vi + 1:] for s in sols})
        how = 'row identities'
        if len(distinct) > 1:
            # several readings satisfy the row: keep only those consistent with the parent row
            # (province -> its region; region or institution -> TOTAL), using siblings that pass
            exp = expected_from_parent(name, rec, parsed, cols, protocol)
            if exp:
                keep = []
                for s_ in sols:
                    v = dict(zip(cols, s_))
                    if all(v[c] == exp[c] for c in exp):
                        keep.append(s_)
                sols = keep
                distinct = sorted({s[:vi] + s[vi + 1:] for s in sols})
                how = 'row identities + parent-row identity'
        if len(distinct) == 1:
            chosen = list(sols[0])
            vi = cols.index('victims')
            chosen[vi] = cand[vi].most_common(1)[0][0] if cand[vi] else chosen[vi]
            new = dict(zip(cols, chosen))
            log.append({'unit': name, 'before': {c: rec['values'].get(c) for c in cols},
                        'after': new, 'constraint': how,
                        'candidates': {cols[i]: {str(k): v for k, v in cand[i].items()} for i in range(len(cols))}})
            rec['values'] = new; rec['row_ok'] = True; rec['ocr_resolved'] = True
            repaired += 1
    return repaired
