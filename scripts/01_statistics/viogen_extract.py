#!/usr/bin/env python3
"""VioGén table extractor for the DGVG 'Boletín estadístico mensual' (BEM) PDFs.

Repairs the earlier viogen_full_panel_extractor.py, which passed only a synthetic test.
Problems found on the real archive, and how this version handles them:
  1. 2023-24 text layers split words into letter fragments ("G alicia", "R egión de Murcia",
     "T O T AL"), so labels are matched after removing ALL spaces and accents.
  2. Police-force names differ before VioGén 2 ("Cuerpo Nacional de Policía", "PL Madrid", ...):
     an alias table maps them to the 2025 names, and the printed label is kept.
  3. From March 2026 the VioGén tables are embedded images with no text layer: those pages are
     rendered and read with Tesseract OCR, then parsed with the same geometry and the same checks.
  4. The earlier script forced the PDF TOTAL to equal a national CSV that partly came from press
     reports. Here the printed PDF TOTAL is the reference; the national CSV is compared afterwards.
Column positions are learned from the table itself (numbers are right-aligned), every row must
add up, and every level of aggregation must reconcile. Nothing is imputed: a failing table is
reported as a failure, never 'fixed'.
"""
from __future__ import annotations
import re, unicodedata, io
from collections import defaultdict

MONTHS_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre',
             'Octubre','Noviembre','Diciembre']
BEM_URL = 'https://violenciagenero.igualdad.gob.es/wp-content/uploads/BEM_{m}_{y}.pdf'

COLS_2019 = ['no_appreciable','low','medium','high','extreme','active','inactive','total','victims']
COLS_2025 = ['low','medium','high','extreme','active','supervised','inactive','total','victims']
# 30 June 2025 (first day of the 2025 protocol): 'No apreciado' still printed AND 'Supervisados' already exists
COLS_TRANSITION = ['no_appreciable','low','medium','high','extreme','active','supervised','inactive','total','victims']
LEVELS_2019 = COLS_2019[:5]
LEVELS_2025 = COLS_2025[:4]

def key(s: str) -> str:
    """Accent-, case- and space-insensitive key: 'G alicia' -> 'galicia'."""
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]', '', s.lower())

# ---------------------------------------------------------------- territorial units
REGION_PROVINCES = {
 'Andalucía': ['Almería','Cádiz','Córdoba','Granada','Huelva','Jaén','Málaga','Sevilla'],
 'Aragón': ['Huesca','Teruel','Zaragoza'],
 'Principado de Asturias': [], 'Illes Balears': [],
 'Canarias': ['Las Palmas','Santa Cruz de Tenerife'],
 'Cantabria': [],
 'Castilla y León': ['Ávila','Burgos','León','Palencia','Salamanca','Segovia','Soria','Valladolid','Zamora'],
 'Castilla-La Mancha': ['Albacete','Ciudad Real','Cuenca','Guadalajara','Toledo'],
 'Cataluña': ['Barcelona','Girona','Lleida','Tarragona'],
 'Comunitat Valenciana': ['Alicante/Alacant','Castellón/Castelló','Valencia/València'],
 'Extremadura': ['Badajoz','Cáceres'],
 'Galicia': ['A Coruña','Lugo','Ourense','Pontevedra'],
 'Comunidad de Madrid': [], 'Región de Murcia': [], 'Comunidad Foral de Navarra': [],
 'País Vasco': ['Araba/Álava','Gipuzkoa','Bizkaia'],
 'La Rioja': [], 'Ceuta': [], 'Melilla': [],
}
NO_LEVELS_REGIONS = {'Cataluña', 'País Vasco'}   # risk levels not reported (own police systems)
TERR = {}   # key -> (canonical, kind, region)
for reg, provs in REGION_PROVINCES.items():
    TERR[key(reg)] = (reg, 'region', reg)
    for p in provs:
        TERR[key(p)] = (p, 'province', reg)
for alias, canon in {'Cataluña (1)': 'Cataluña', 'País Vasco (1)': 'País Vasco',
                     'Castilla - La Mancha': 'Castilla-La Mancha', 'Region de Murcia': 'Región de Murcia',
                     'Asturias': 'Principado de Asturias', 'Baleares': 'Illes Balears',
                     'Comunidad Valenciana': 'Comunitat Valenciana', 'Navarra': 'Comunidad Foral de Navarra',
                     'Madrid': 'Comunidad de Madrid', 'Murcia': 'Región de Murcia',
                     # Nov 2024 bulletin prints inverted names and a typo in the source itself
                     'Pincipado de Asturias': 'Principado de Asturias', 'Balears Illes': 'Illes Balears',
                     'Rioja La': 'La Rioja', 'Rioja, La': 'La Rioja',
                     # 2018-2019 bulletins
                     'Islas Baleares': 'Illes Balears'}.items():
    TERR[key(alias)] = (canon, 'region', canon)
for alias, canon, reg in [('Álava','Araba/Álava','País Vasco'), ('Alicante','Alicante/Alacant','Comunitat Valenciana'),
                          ('Castellón','Castellón/Castelló','Comunitat Valenciana'),
                          ('Valencia','Valencia/València','Comunitat Valenciana'), ('La Coruña','A Coruña','Galicia'),
                          ('Vizcaya','Bizkaia','País Vasco'), ('Guipúzcoa','Gipuzkoa','País Vasco'),
                          ('Orense','Ourense','Galicia'), ('Palmas, Las','Las Palmas','Canarias'),
                          ('Coruña, A','A Coruña','Galicia')]:
    TERR.setdefault(key(alias), (canon, 'province', reg))
TERR['total'] = ('TOTAL', 'total', None)

# ---------------------------------------------------------------- police institutions
FORCE_ALIASES = {
 'Policía Nacional': ['Cuerpo Nacional de Policía', 'Policía Nacional'],
 'Guardia Civil': ['Guardia Civil'],
 'Ertzaintza': ['Ertzaintza (1)', 'Ertzaintza'],
 "Mossos d'Esquadra": ["Mossos d'Esquadra (1)", "Mossos d'Esquadra", 'Mossos dEsquadra'],
 'Policía Foral de Navarra': ['Policía Foral de Navarra', 'Policía Foral Navarra'],
 'U.A. de Galicia': ['U.A. de Galicia', 'UA de Galicia', 'Unidad Adscrita de Galicia'],
 'PL Andalucía': ['PL Andalucía'], 'PL Aragón': ['PL Aragón'],
 'PL Principado de Asturias': ['PL Principado de Asturias', 'PL Asturias'],
 'PL Illes Balears': ['PL Illes Balears', 'PL Baleares'], 'PL Canarias': ['PL Canarias'],
 'PL Cantabria': ['PL Cantabria'], 'PL Castilla y León': ['PL Castilla y León'],
 'PL Castilla-La Mancha': ['PL Castilla-La Mancha', 'PL Castilla - La Mancha'],
 'PL Cataluña': ['PL Cataluña'],
 'PL Comunitat Valenciana': ['PL Comunitat Valenciana', 'PL Comunidad Valenciana'],
 'PL Extremadura': ['PL Extremadura'], 'PL Galicia': ['PL Galicia'],
 'PL Comunidad de Madrid': ['PL Comunidad de Madrid', 'PL Madrid'],
 'PL Región de Murcia': ['PL Región de Murcia', 'PL Region de Murcia', 'PL Murcia'],
 'PL Comunidad Foral de Navarra': ['PL Comunidad Foral de Navarra', 'PL Navarra'],
 'PL País Vasco': ['PL País Vasco'], 'PL La Rioja': ['PL La Rioja'],
 'PL Ceuta': ['PL Ceuta'], 'PL Melilla': ['PL Melilla'],
}
NO_LEVELS_FORCES = {'Ertzaintza', "Mossos d'Esquadra", 'PL Cataluña', 'PL País Vasco'}
for canon, extra in {'PL Principado de Asturias': ['PL Pincipado de Asturias'],
                     'PL Illes Balears': ['PL Balears Illes'], 'PL La Rioja': ['PL Rioja La']}.items():
    FORCE_ALIASES[canon] += extra
FORCE = {key(a): (canon, 'force', None) for canon, al in FORCE_ALIASES.items() for a in al}
# From Dec 2024 the institution table adds small 'U.A. de <region>' rows (units attached to regional
# governments). Accept any of them, keyed to the canonical region name.
for reg in REGION_PROVINCES:
    for variant in {reg} | {a for a, c in {'Castilla - La Mancha': 'Castilla-La Mancha',
                                           'Region de Murcia': 'Región de Murcia'}.items() if c == reg}:
        FORCE.setdefault(key('U.A. de ' + variant), ('U.A. de ' + reg, 'force', None))
FORCE[key('U.A. de Galicia')] = ('U.A. de Galicia', 'force', None)
FORCE['total'] = ('TOTAL', 'total', None)

NUM_RE = re.compile(r'^\d{1,3}(?:[.,]\d{3})+$|^\d+$')
SCI_RE = re.compile(r'^\d(?:[.,]\d+)?E\+\d+$', re.I)   # e.g. '1E+05' printed by a spreadsheet

def levels_for(protocol):
    return LEVELS_2025 if protocol == '2025' else LEVELS_2019

def to_int(tok: str) -> int:
    return int(tok.replace('.', '').replace(',', ''))

# ---------------------------------------------------------------- word sources
def pdf_words(page):
    """Words from a PDF text layer, coordinates normalised to page width/height."""
    W, H = page.rect.width, page.rect.height
    return [(w[0]/W, w[1]/H, w[2]/W, w[3]/H, w[4]) for w in page.get_text('words')]

def ocr_words(page, dpi=400):
    """Render an image-only page and read it with Tesseract; same normalised coordinates."""
    import pymupdf, pytesseract
    from PIL import Image
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    img = Image.open(io.BytesIO(pix.tobytes('png')))
    d = pytesseract.image_to_data(img, lang='spa', config='--psm 6',
                                  output_type=pytesseract.Output.DICT)
    W, H = img.size
    out = []
    for i, t in enumerate(d['text']):
        t = t.strip()
        if not t or float(d['conf'][i]) < 0:
            continue
        x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
        out.append((x/W, y/H, (x+w)/W, (y+h)/H, t))
    return out, img

def page_text_key(words):
    return key(' '.join(w[4] for w in words))

# ---------------------------------------------------------------- table parsing
def group_rows(words, tol=0.0045):
    """Group words into printed lines by vertical centre."""
    ws = sorted(words, key=lambda w: ((w[1]+w[3])/2, w[0]))
    rows = []
    for w in ws:
        yc = (w[1]+w[3])/2
        if rows and abs(yc - rows[-1]['y']) <= tol:
            r = rows[-1]; r['w'].append(w); r['y'] = (r['y']*(len(r['w'])-1) + yc)/len(r['w'])
        else:
            rows.append({'y': yc, 'w': [w]})
    for r in rows:
        r['w'].sort(key=lambda w: w[0])
    return rows

def split_label_numbers(row):
    """Leading non-numeric words form the label; numeric tokens after it are the cells."""
    label, nums, seen_num = [], [], False
    for w in row['w']:
        t = w[4].strip()
        if NUM_RE.match(t) and (seen_num or label):
            seen_num = True
            nums.append((w[0], w[2], to_int(t), t))
        elif SCI_RE.match(t) and (seen_num or label):
            seen_num = True
            nums.append((w[0], w[2], 'SCI', t))     # printed artefact: value unreadable, column known
        elif not seen_num:
            label.append(t)
        else:
            nums.append((w[0], w[2], None, t))   # stray non-numeric token inside the cells
    return ' '.join(label), nums

def match_label(label, table):
    k = key(label)
    if k in table:
        return table[k]
    k2 = re.sub(r'1$', '', k)                      # trailing footnote '(1)'
    if k2 in table:
        return table[k2]
    # a spaced-out first letter can land on its own text line ('C omunidad Foral...'):
    # accept a UNIQUE known name that ends with this label and lacks at most 2 leading characters
    if len(k) >= 6:
        cands = {v for kk, v in table.items() if kk.endswith(k) and 0 < len(kk) - len(k) <= 2}
        if len(cands) == 1:
            return cands.pop()
    return None

def learn_columns(rows, ncols=9, gap=0.012):
    """Cluster right edges of numeric cells into columns (numbers are right-aligned)."""
    xs = sorted(x1 for r in rows for (_, x1, v, _) in r['nums'] if isinstance(v, int))
    if not xs:
        raise ValueError('no numeric cells')
    clusters = [[xs[0]]]
    for x in xs[1:]:
        if x - clusters[-1][-1] > gap:
            clusters.append([x])
        else:
            clusters[-1].append(x)
    clusters = [c for c in clusters if len(c) >= 2]
    centres = [sorted(c)[len(c)//2] for c in clusters]
    if len(centres) != ncols:
        raise ValueError(f'found {len(centres)} numeric columns, expected {ncols}: '
                         + ', '.join(f'{c:.3f}' for c in centres))
    return centres

def parse_table(words, kind, header_words=None):
    """Return (protocol, data_date, cols, rows_by_label, problems).
    header_words: optional extra words (e.g. full-page OCR) used only to read the header/date."""
    table = TERR if kind == 'territory' else FORCE
    tk = page_text_key(words + (header_words or []))
    has_na = 'apreciado' in tk
    # 'SUPERVISADOS' is printed on two lines and OCR can drop letters ('SUPER ISAD')
    has_sup = bool(re.search(r'supervisad|super.{0,2}isad|supervi', tk))
    protocol = 'transition' if (has_na and has_sup) else '2025' if has_sup else '2019' if has_na else None
    m0 = re.search(r'datosa(\d{2})(\d{2})(\d{4})', tk)
    if protocol is None and m0 and m0.group(3) + m0.group(2) >= '202507' and 'inactivos' in tk:
        protocol = '2025'   # OCR could not read 'SUPERVISADOS'; no 'No apreciado' column after July 2025
    if protocol is None and m0 and m0.group(3) + m0.group(2) < '202411' and 'inactivos' in tk:
        protocol = '2019'   # OCR could not read 'No apreciado'; before Nov 2024 the layout has no supervised column
    if protocol is None:
        raise ValueError('cannot tell protocol (no SUPERVISADOS / No apreciado header)')
    m = re.search(r'datosa(\d{2})(\d{2})(\d{4})', tk)
    data_date = f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else None
    cols = {'2025': COLS_2025, '2019': COLS_2019, 'transition': COLS_TRANSITION}[protocol]
    rows = []
    for r in group_rows(words):
        label, nums = split_label_numbers(r)
        hit = match_label(label, table) if label else None
        if hit and nums:
            rows.append({'label': label, 'hit': hit, 'nums': nums, 'y': r['y']})
    # the table ends at its TOTAL row; footnote lines below it can start with a region name
    ty = [r['y'] for r in rows if r['hit'][0] == 'TOTAL']
    if ty:
        rows = [r for r in rows if r['y'] <= ty[0] + 1e-6]
    extra = 0
    try:
        centres = learn_columns(rows, len(cols))
    except ValueError:
        # 2018 bulletins print two further columns after VÍCTIMAS ("PSP Gestión desde 17/08/2016",
        # "3A desde 15/02/2017"); they are outside the VioGén case table and are ignored
        if not ('psp' in tk and '3a' in tk):
            raise
        extra = 2
        centres = learn_columns(rows, len(cols) + extra)
    spacing = min(b - a for a, b in zip(centres, centres[1:]))
    out, problems = {}, []
    for r in rows:
        canon, unit_kind, region = r['hit']
        vals = {}
        bad = False
        sci_cells = []
        for x0, x1, v, t in r['nums']:
            j = min(range(len(centres)), key=lambda i: abs(x1 - centres[i]))
            if v is None or abs(x1 - centres[j]) > 0.45 * spacing:
                problems.append(f'{canon}: unplaceable token {t!r}'); bad = True; continue
            if j >= len(cols):            # ignored extra column (2018 PSP / 3A)
                continue
            if v == 'SCI':
                sci_cells.append({'column': cols[j], 'printed': t})
                continue
            if cols[j] in vals:
                problems.append(f'{canon}: two values in column {cols[j]}'); bad = True; continue
            vals[cols[j]] = v
        if canon in out:
            if out[canon]['values'] != vals:
                problems.append(f'{canon}: appears twice with different values')
            continue
        out[canon] = {'printed_label': r['label'], 'kind': unit_kind, 'region': region,
                      'values': vals, 'row_ok': not bad, 'sci_cells': sci_cells}
    return protocol, data_date, cols, out, problems

# ---------------------------------------------------------------- checks
def row_checks(rec, cols, protocol):
    v = rec['values']; levels = levels_for(protocol)
    fails = []
    has_levels = any(c in v for c in levels) or 'active' in v
    if has_levels:
        lv = sum(v.get(c, 0) for c in levels)
        if lv != v.get('active', 0):
            fails.append(f"levels {lv} != active {v.get('active', 0)}")
    parts = v.get('active', 0) + v.get('supervised', 0) + v.get('inactive', 0)
    if 'total' in v and parts != v['total']:
        fails.append(f"active+supervised+inactive {parts} != total {v['total']}")
    return fails

def full_values(rec, cols):
    """Blank cells in a reported row are printed zeros; returns a complete dict."""
    return {c: rec['values'].get(c, 0) for c in cols}

def reconcile(parsed, cols, protocol, kind):
    """Cross-level checks. Returns list of failures (empty = fully reconciled)."""
    levels = levels_for(protocol)
    case_cols = [c for c in cols if c != 'victims']
    fails = []
    if 'TOTAL' not in parsed:
        return ['TOTAL row not found']
    tot = full_values(parsed['TOTAL'], cols)
    for name, rec in parsed.items():
        for f in row_checks(rec, cols, protocol):
            fails.append(f'{name}: {f}')
        if not rec['row_ok']:
            fails.append(f'{name}: row has unplaceable cells')
    if kind == 'territory':
        regions = [r for r in REGION_PROVINCES]
        missing = [r for r in regions if r not in parsed]
        if missing:
            fails.append('missing regions: ' + ', '.join(missing))
        for reg, provs in REGION_PROVINCES.items():
            if not provs or reg not in parsed:
                continue
            miss = [p for p in provs if p not in parsed]
            if miss:
                fails.append(f'{reg}: missing provinces {miss}'); continue
            for c in case_cols:
                s = sum(full_values(parsed[p], cols)[c] for p in provs)
                if s != full_values(parsed[reg], cols)[c]:
                    fails.append(f'{reg}: provinces sum {c} {s} != region {full_values(parsed[reg], cols)[c]}')
        present = [r for r in regions if r in parsed]
        for c in case_cols:
            s = sum(full_values(parsed[r], cols)[c] for r in present)
            if s != tot[c]:
                fails.append(f'regions sum {c} {s} != TOTAL {tot[c]}')
    else:
        forces = [f for f in parsed if f != 'TOTAL']
        for c in case_cols:
            s = sum(full_values(parsed[f], cols)[c] for f in forces)
            if s != tot[c]:
                fails.append(f'forces sum {c} {s} != TOTAL {tot[c]}')
        expected = set(FORCE_ALIASES) - set(parsed)
        if expected - NO_LEVELS_FORCES:
            fails.append('institutions not found: ' + ', '.join(sorted(expected - NO_LEVELS_FORCES)))
    return fails

# ---------------------------------------------------------------- page finding
def is_main_territory(tk):
    return ('distribucionterritorial' in tk and 'todoslospaises' in tk and 'todaslasedades' in tk
            and 'almeria' in tk and 'melilla' in tk)

def is_force(tk):
    return 'cuerpospoliciales' in tk and 'guardiacivil' in tk

def find_pages(doc, use_ocr=False, search=range(40, 80)):
    """Return {'territory': (pno, words, img), 'force': (...)} for the main tables."""
    found = {}
    for pno in search:
        if pno >= len(doc):
            break
        page = doc[pno]
        words = pdf_words(page); img = None
        if len(words) < 30 and use_ocr and page.get_images():
            words, img = ocr_words(page)
        tk = page_text_key(words)
        # The main territorial table names 'Todos los países' AND 'Todas las edades' on one page;
        # age- and origin-specific tables name only one of them.
        if 'territory' not in found and is_main_territory(tk):
            found['territory'] = (pno, words, img)
        elif 'force' not in found and is_force(tk):
            found['force'] = (pno, words, img)
        if len(found) == 2:
            break
    return found


# ---------------------------------------------------------------- OCR of image-only grid tables (2026)
def _line_positions(mask_sum, thresh):
    idx = [i for i, v in enumerate(mask_sum) if v > thresh]
    lines, cur = [], []
    for i in idx:
        if cur and i - cur[-1] > 3:
            lines.append(sum(cur) // len(cur)); cur = []
        cur.append(i)
    if cur:
        lines.append(sum(cur) // len(cur))
    return lines

OCR_LOG = []   # per-cell OCR agreement record for the validation report

def page_table_image(page):
    """Return the page's embedded table image at NATIVE resolution (grey numpy array), or None.
    Some 2020-2021 bulletins split one table into two images stacked on the page; those are joined."""
    import numpy as np, cv2
    doc = page.parent
    placed = []
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            placed.append((r, img[0]))
    placed.sort(key=lambda t: t[0].y0)
    stack = []
    for r, xref in placed:
        if stack and abs(r.x0 - stack[-1][0].x0) < 2 and abs(r.x1 - stack[-1][0].x1) < 2 \
                and abs(r.y0 - stack[-1][0].y1) < 2:
            stack.append((r, xref))
        elif not stack or (r.y1 - r.y0) * (r.x1 - r.x0) > 0:
            if len(stack) >= 2:
                break
            stack = [(r, xref)]
    if len(stack) >= 2:
        parts = [cv2.imdecode(np.frombuffer(doc.extract_image(x)['image'], np.uint8), cv2.IMREAD_GRAYSCALE)
                 for _, x in stack]
        w = parts[0].shape[1]
        if all(p_.shape[1] == w for p_ in parts) and w >= 600:
            return np.vstack(parts)
    best = None
    for img in page.get_images(full=True):
        info = doc.extract_image(img[0])
        if best is None or info['width'] * info['height'] > best['width'] * best['height']:
            best = info
    if best is None or best['width'] < 600:
        return None
    arr = cv2.imdecode(np.frombuffer(best['image'], np.uint8), cv2.IMREAD_GRAYSCALE)
    return arr

def _prep(c, scale, method, clean_border=True):
    import numpy as np, cv2
    g = cv2.resize(c, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    if method == 'otsu':
        _, b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method.startswith('fixed'):          # fixed cut-off, e.g. 'fixed70': keeps thin strokes open (9 vs 8)
        _, b = cv2.threshold(g, int(method[5:]), 255, cv2.THRESH_BINARY)
    else:
        b = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    if not clean_border:
        return cv2.copyMakeBorder(b, 30, 30, 40, 40, cv2.BORDER_CONSTANT, value=255)
    # remove residual grid-line fragments: dark components touching the crop border
    inv = (b < 128).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv, 8)
    h, w = inv.shape
    for i in range(1, n):
        x, y, cw, ch, area = stats[i]
        if x == 0 or y == 0 or x + cw >= w or y + ch >= h:
            b[lab == i] = 255
    return cv2.copyMakeBorder(b, 30, 30, 40, 40, cv2.BORDER_CONSTANT, value=255)

def _read_cell(gray_cell, numeric, label_table=None):
    """OCR one cell. White-on-dark cells are inverted; the cell is enlarged and binarised in two
    ways and read with Tesseract; numeric cells are read up to five ways and the majority reading
    is kept. Returns (text, n_readings_agreeing, n_readings)."""
    import numpy as np, pytesseract
    from collections import Counter
    from PIL import Image
    c = gray_cell
    if c.size == 0:
        return ('', 0, 0)
    if np.median(c) < 128:
        c = 255 - c
    if numeric:
        cfgs = [(4, 'otsu', 7), (4, 'adapt', 7), (3, 'otsu', 7), (6, 'otsu', 7), (4, 'otsu', 8)]
        reads = []
        for i, (sc, m, psm) in enumerate(cfgs):
            img = _prep(c, sc, m)
            if (img < 128).sum() < 40:
                reads.append('')
            else:
                reads.append(pytesseract.image_to_string(Image.fromarray(img), config=
                    f'--psm {psm} -c tessedit_char_whitelist=0123456789.').strip().replace(' ', ''))
            if i == 1 and reads[0] == reads[1]:
                return (reads[0], 2, 2)          # first two agree: accept
        for psm in (10, 13):                       # lone digits read better as single characters
            img = _prep(c, 4, 'otsu')
            if (img < 128).sum() >= 40:
                reads.append(pytesseract.image_to_string(Image.fromarray(img), config=
                    f'--psm {psm} -c tessedit_char_whitelist=0123456789.').strip().replace(' ', ''))
        nonempty = [r for r in reads if r]
        if not nonempty:
            img = _prep(c, 4, 'otsu')
            return ('?', 0, len(reads)) if (img < 128).sum() >= 40 else ('', 0, len(reads))
        best, n = Counter(nonempty).most_common(1)[0]
        return (best, n, len(reads))
    first = ''
    for sc, m, clean in [(4, 'otsu', False), (4, 'otsu', True), (4, 'adapt', False), (3, 'otsu', False),
                         (6, 'otsu', False), (6, 'adapt', True)]:
        img = _prep(c, sc, m, clean)
        if (img < 128).sum() < 40:
            continue
        t = pytesseract.image_to_string(Image.fromarray(img), lang='spa', config='--psm 7').strip()
        first = first or t
        if label_table is None or (t and match_label(t, label_table)):
            return (t, 1, 1)
    return (first, 0, 1)

def ocr_grid_words(page, kind='territory'):
    """Read an image-only grid table (2026 bulletins) cell by cell.

    Works on the embedded image at native resolution (about 196 dpi). Grid lines are found
    morphologically on a local-contrast map; columns printed white-on-grey/black (TOTAL, VICTIMAS)
    have no drawn separators, so the evenly spaced numeric grid is extended to the table edge and
    snapped to background steps. Each cell is OCR'd separately (digits only for numeric cells).
    Returns (cell_words, header_words) in the normalised coordinates used by pdf_words(), so the
    same parse_table() and reconcile() checks apply. Nothing is corrected by hand or guessed.
    """
    import numpy as np, cv2, pytesseract
    from PIL import Image
    gray = page_table_image(page)
    if gray is None:
        raise ValueError('no embedded table image on page')
    H, W = gray.shape
    k = max(31, (W // 40) | 1)
    bg = cv2.medianBlur(gray, k)
    ink = (cv2.absdiff(gray, bg) > 40).astype(np.uint8)
    horiz = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((1, W // 12), np.uint8))
    vert = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((H // 25, 1), np.uint8))
    ys = _line_positions(horiz.sum(axis=1), 0.35 * horiz.sum(axis=1).max())
    xs = _line_positions(vert.sum(axis=0), 0.35 * vert.sum(axis=0).max())
    if len(xs) < 4 or len(ys) < 20:
        raise ValueError(f'grid not detected (vertical lines {len(xs)}, horizontal lines {len(ys)})')
    # right edge of the table: last column whose background differs from the white page
    colmean = bg[ys[3]:ys[-1]].mean(axis=0)
    dark_cols = np.nonzero(colmean < 235)[0]
    right = int(dark_cols.max()) if len(dark_cols) else int(np.nonzero(horiz.max(axis=0))[0].max())
    right = max(right, int(np.nonzero(horiz.max(axis=0))[0].max()))
    step = np.abs(np.diff(colmean))
    spacing = int(np.median(np.diff(xs[1:])))
    # left border of the table (label column) can be missed: use the start of the horizontal rules
    left = int(np.nonzero(horiz.max(axis=0))[0].min())
    if xs[0] - left > 0.5 * spacing:
        xs.insert(0, left)
    while xs[-1] + 0.6 * spacing < right:
        guess = xs[-1] + spacing
        lo, hi = max(guess - spacing // 8, 0), min(guess + spacing // 8, len(step) - 1)
        snap = lo + int(np.argmax(step[lo:hi])) if step[lo:hi].max() > 20 else guess
        xs.append(min(snap, right))
    if right - xs[-1] > 0.4 * spacing:
        xs.append(right)
    # A row printed on a dark background (the TOTAL row) is separated from the row above by a change
    # of shade, not a drawn line: split any interval about twice the usual row height at the strongest
    # vertical background step (or at its midpoint).
    rowmean = gray[:, xs[0]:xs[-1]].astype(float).mean(axis=1)
    smooth = np.convolve(rowmean, np.ones(3) / 3, mode='same')
    vstep = np.abs(np.diff(smooth))
    extra = [i for i in range(1, len(vstep) - 1)
             if vstep[i] > 40 and vstep[i] >= vstep[i - 1] and vstep[i] >= vstep[i + 1]
             and ys[0] < i < ys[-1] + 80 and min(abs(i - y) for y in ys) > 4]
    ys = sorted(set(ys + extra))
    # header words: plain OCR of everything above the first data row, at 2x
    head = cv2.resize(gray[:ys[min(4, len(ys) - 1)]], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    hd = pytesseract.image_to_data(Image.fromarray(head), lang='spa', config='--psm 6',
                                   output_type=pytesseract.Output.DICT)
    header_words = [(hd['left'][i]/(2*W), hd['top'][i]/(2*H), (hd['left'][i]+hd['width'][i])/(2*W),
                     (hd['top'][i]+hd['height'][i])/(2*H), t.strip())
                    for i, t in enumerate(hd['text']) if t.strip()]
    # column names sit in the first grid rows (e.g. 'SUPERVISAD' / 'OS' on two lines)
    for a, b in zip(ys[:4], ys[1:5]):
        for x0, x1 in zip(xs, xs[1:]):
            t = _read_cell(gray[a + 2:b - 1, x0 + 2:x1 - 1], numeric=False)[0]
            if t:
                header_words.append((x0/W, a/H, x1/W, b/H, t.replace('\n', ' ')))
    words = []
    pad = 2
    for a, b in zip(ys, ys[1:]):
        if b - a < 0.6 * np.median(np.diff(ys)):
            continue
        lab = _read_cell(gray[a + pad:b - pad + 1, xs[0] + pad:xs[1] - pad + 1], numeric=False,
                         label_table=TERR if kind == 'territory' else FORCE)[0]
        if not lab:
            continue
        y0, y1 = a / H, b / H
        words.append((xs[0]/W, y0, xs[1]/W, y1, lab))
        for x0, x1 in zip(xs[1:], xs[2:]):
            t, agree, nread = _read_cell(gray[a + pad:b - pad + 1, x0 + pad + 1:x1 - pad], numeric=True)
            if t:
                words.append((x0/W, y0, x1/W, y1, t))
                OCR_LOG.append({'y0': a, 'y1': b, 'x0': x0, 'x1': x1, 'text': t,
                                'agree': agree, 'reads': nread})
    grid = {'gray': gray, 'xs': xs, 'ys': ys, 'W': W, 'H': H, 'pad': pad}
    return words, header_words, grid
