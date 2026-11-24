#!/usr/bin/env python3
"""Assemble the per-month extraction JSON into the Module 1 deliverable CSVs.

usage: assemble.py <out_dir_with_json> <reference_dir> <bem_dir> <repository_root>
Nothing is imputed. Months/units that are not published stay absent; risk levels that a
reporting unit does not publish (Catalonia, Basque Country) are NaN, never 0.
"""
import sys, json, csv, glob, hashlib, os, math
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viogen_extract as V

OUT, HAND, BEM, DEL = map(Path, sys.argv[1:5])
DATA = DEL / 'data' / '01_statistics'; DATA.mkdir(parents=True, exist_ok=True)
NAN = ''
ALL_MONTHS = [f'{y}-{m:02d}' for y in range(2018, 2027) for m in range(1, 13)
              if (y, m) <= (2026, 10)]
FORCE_TABLE_START = '2020-02'      # the police-institution table is first printed in the February 2020 bulletin
LEVELS = ['no_appreciable', 'low', 'medium', 'high', 'extreme']
VALS = LEVELS + ['active', 'supervised', 'inactive', 'total', 'victims']

def period(ym):
    if ym <= '2019-02':
        return '2016 protocol (Instrucción 7/2016)'
    if ym <= '2024-10':
        return '2019 protocol (Instrucción 4/2019, in force 13 Mar 2019)'
    if ym <= '2025-06':
        return 'transition (2019 levels; Supervisados column printed)'
    return '2025 protocol (VioGén 2 levels)'

def month_end(ym):
    import calendar
    y, m = int(ym[:4]), int(ym[5:])
    return f'{ym}-{calendar.monthrange(y, m)[1]:02d}'

def pct(a, b):
    return round(100 * a / b, 4) if (a not in (None, NAN) and b) else NAN

def write(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

months = {}
for f in sorted(glob.glob(str(OUT / 'json' / '*.json'))):
    r = json.load(open(f))
    months[r['month']] = r

def month_end(ym):
    import calendar
    y, m = int(ym[:4]), int(ym[5:])
    return f'{ym}-{calendar.monthrange(y, m)[1]:02d}'

# a table is used only if it reconciles AND its printed data date is the month end (an OCR'd table whose
# date cannot be read correctly is not used: nothing else would confirm it is that month's table)
for ym, r in months.items():
    for t in r['tables'].values():
        if t.get('status') == 'reconciled' and t.get('data_date') != month_end(ym):
            t['status'] = 'failed checks (printed data date not read as the month end)'

hand_nat = {r['date'][:7]: r for r in csv.DictReader(open(HAND / '01_CURRENT_RESEARCH' / 'national_2023_2026_monthly_46.csv'))}
june_force = list(csv.DictReader(open(HAND / '01_CURRENT_RESEARCH' / 'June_2025_police_forces.csv')))

def val_or_nan(unit, col, protocol, reports_levels):
    v = unit['values']
    if col == 'no_appreciable' and protocol == '2025':
        return NAN                                 # abolished category: not applicable, not zero
    if col == 'supervised' and protocol == '2019':
        return NAN                                 # status not printed before Nov 2024
    if col in LEVELS + ['active', 'supervised'] and not reports_levels:
        return NAN                                 # unit does not publish risk levels
    return v.get(col, 0)

def method_of(t):
    return 'OCR of embedded table image' if t.get('method', '').startswith('OCR') else 'PDF text layer'

# ------------------------------------------------------------------ national
national, changelog, validation, errors = [], [], [], []
for ym in ALL_MONTHS:
    r = months.get(ym)
    t = (r or {}).get('tables', {}).get('territory', {})
    f_ = (r or {}).get('tables', {}).get('force', {})
    h = hand_nat.get(ym)
    row = {'date': month_end(ym), 'year': ym[:4], 'month': int(ym[5:]), 'protocol_period': period(ym)}
    if t.get('status') == 'reconciled':
        T = t['units']['TOTAL']
        prot = t['protocol']
        for c in VALS:
            row[c] = val_or_nan(T, c, prot, True)
        row.update(source_type='official DGVG monthly bulletin (BEM)', source_url=r['url'],
                   pdf_page=t['pdf_page'], extraction_method=method_of(t),
                   verification_status='verified against official PDF: all rows, regions and provinces reconcile',
                   data_date_printed=t['data_date'])
        # compare with the reference national series (Jan 2023 onwards only)
        diffs = []
        for c, hc in [] if not h else [('no_appreciable', 'no_appreciable'), ('low', 'low'), ('medium', 'medium'),
                      ('high', 'high'), ('extreme', 'extreme'), ('active', 'total_active')]:
            hv = h.get(hc, '') if h else ''
            hv = int(float(hv)) if hv not in ('', None) else NAN
            if row[c] != hv:
                diffs.append((c, hv, row[c]))
        for c, old, new in diffs:
            changelog.append({'date': row['date'], 'field': c, 'previous_value': old, 'corrected_value': new,
                              'previous_source': h.get('source_url', '') if h else '',
                              'previous_source_kind': h.get('source_kind', '') if h else '',
                              'corrected_source': r['url'] + f" (PDF page {t['pdf_page']})",
                              'reason': 'value differs from the official bulletin, which reconciles internally'})
        if h and not diffs and 'press' in h.get('source_kind', ''):
            changelog.append({'date': row['date'], 'field': 'all level counts and active total',
                              'previous_value': 'press relay', 'corrected_value': 'unchanged',
                              'previous_source': h.get('source_url', ''), 'previous_source_kind': h.get('source_kind', ''),
                              'corrected_source': r['url'] + f" (PDF page {t['pdf_page']})",
                              'reason': 'press-relay figures confirmed exactly by the official bulletin; source upgraded'})
        row['reference_match'] = ('not in reference (before 2023)' if not h else
                                'yes' if not diffs else 'no: ' + '; '.join(f'{c} {o}->{n}' for c, o, n in diffs))
    elif f_.get('status') == 'reconciled':
        # territorial table not extracted (image), but the police-institution table reconciles: its TOTAL row
        # is the same national total (identical to the territorial TOTAL in every month where both exist)
        T = f_['units']['TOTAL']
        for c in VALS:
            row[c] = val_or_nan(T, c, f_['protocol'], True)
        row.update(source_type='official DGVG monthly bulletin (BEM)', source_url=r['url'],
                   pdf_page=f_['pdf_page'], extraction_method=method_of(f_) + ' (police-institution table)',
                   verification_status='verified against official PDF: police-institution table reconciles '
                   '(territorial table is an image and was not extracted)',
                   data_date_printed=f_['data_date'],
                   reference_match='not in reference (before 2023)' if not h else 'not checked')
    elif h:   # no reconciled official table: keep the reference row, clearly labelled
        for c in VALS:
            row[c] = NAN
        for c, hc in [('low', 'low'), ('medium', 'medium'), ('high', 'high'), ('extreme', 'extreme'),
                      ('active', 'total_active')]:
            row[c] = int(float(h[hc]))
        row['no_appreciable'] = int(float(h['no_appreciable'])) if h['no_appreciable'] not in ('', None) else NAN
        row.update(source_type=h['source_kind'], source_url=h['source_url'], pdf_page=NAN,
                   extraction_method='not extracted (no official table available here)',
                   verification_status='NOT verified against an official PDF: '
                   + ('no DGVG bulletin published yet (HTTP 404 on 11 Nov 2026); VioGén portal disallows automated access'
                      if ym == '2026-10' else (r or {}).get('error', 'extraction failed')),
                   data_date_printed=NAN, reference_match='kept as supplied')
    else:     # no reconciled official table and nothing in the reference: the month stays empty
        for c in VALS:
            row[c] = NAN
        row.update(source_type='official DGVG monthly bulletin (BEM)', source_url=(r or {}).get('url', ''),
                   pdf_page=t.get('pdf_page', NAN), extraction_method='not extracted',
                   verification_status='NOT extracted: ' + str(t.get('status', (r or {}).get('error', 'no bulletin'))),
                   data_date_printed=NAN, reference_match='not in reference (before 2023)')
    lv = [row[c] for c in ['medium', 'high', 'extreme']]
    if all(x not in (NAN, None) for x in lv):
        row['medium_plus'] = sum(lv); row['medium_plus_pct'] = pct(sum(lv), row['active'])
        row['high_plus'] = row['high'] + row['extreme']; row['high_plus_pct'] = pct(row['high_plus'], row['active'])
        low_grp = row['low'] + (row['no_appreciable'] if row['no_appreciable'] not in (NAN, None) else 0)
        row['lowest_group'] = low_grp; row['lowest_group_pct'] = pct(low_grp, row['active'])
    if row.get('supervised') not in (NAN, None) and row.get('active') not in (NAN, None):
        row['supervised_per_100_active'] = round(100 * row['supervised'] / row['active'], 3)
    national.append(row)

NAT_FIELDS = ['date', 'year', 'month', 'protocol_period', 'no_appreciable', 'low', 'medium', 'high', 'extreme',
              'active', 'supervised', 'inactive', 'total', 'victims', 'medium_plus', 'medium_plus_pct', 'high_plus',
              'high_plus_pct', 'lowest_group', 'lowest_group_pct', 'supervised_per_100_active', 'source_type',
              'source_url', 'pdf_page', 'data_date_printed', 'extraction_method', 'verification_status', 'reference_match']
write(DATA / 'national_monthly_verified.csv', national, NAT_FIELDS)

# ------------------------------------------------------------------ subnational panels
PANEL_FIELDS = ['date', 'protocol_period', 'unit', 'printed_label', 'unit_type', 'parent_region', 'risk_levels_reported',
                'no_appreciable', 'low', 'medium', 'high', 'extreme', 'active', 'supervised', 'inactive', 'total',
                'victims', 'medium_plus', 'medium_plus_pct', 'source_url', 'pdf_page', 'extraction_method',
                'ocr_row_reread', 'qa_status', 'notes']
SINGLE = {reg for reg, p in V.REGION_PROVINCES.items() if not p}
regional, provincial, police = [], [], []

def panel_row(ym, name, u, t, r, unit_type, parent, reports):
    prot = t['protocol']
    row = {'date': month_end(ym), 'protocol_period': period(ym), 'unit': name, 'printed_label': u['printed_label'],
           'unit_type': unit_type, 'parent_region': parent, 'risk_levels_reported': reports,
           'source_url': r['url'], 'pdf_page': t['pdf_page'], 'extraction_method': method_of(t),
           'ocr_row_reread': 'yes' if u.get('ocr_resolved') else '', 'qa_status': 'reconciled'}
    for c in VALS:
        row[c] = val_or_nan(u, c, prot, reports)
    if reports:
        mp = sum(row[c] for c in ['medium', 'high', 'extreme'])
        row['medium_plus'] = mp; row['medium_plus_pct'] = pct(mp, row['active'])
    else:
        row['notes'] = ('risk levels not published for this unit (own police system); '
                        + ('from Feb 2026 the bulletin prints 0 in these cells; recorded here as not reported'
                           if ym >= '2026-02' else 'cells blank in source'))
    return row

for ym in ALL_MONTHS:
    r = months.get(ym)
    if not r:
        continue
    t = r['tables'].get('territory', {})
    if t.get('status') == 'reconciled':
        for name, u in t['units'].items():
            if name == 'TOTAL':
                continue
            if u['kind'] == 'region':
                reports = name not in V.NO_LEVELS_REGIONS
                ut = 'autonomous city' if name in ('Ceuta', 'Melilla') else 'autonomous community'
                regional.append(panel_row(ym, name, u, t, r, ut, name, reports))
                if name in SINGLE:      # single-province regions/cities are also province-equivalents
                    provincial.append(panel_row(ym, name, u, t, r,
                                                'autonomous city' if name in ('Ceuta', 'Melilla') else 'single-province region',
                                                name, reports))
            else:
                reports = u['region'] not in V.NO_LEVELS_REGIONS
                provincial.append(panel_row(ym, name, u, t, r, 'province', u['region'], reports))
    f = r['tables'].get('force', {})
    if f.get('status') == 'reconciled':
        for name, u in f['units'].items():
            if name == 'TOTAL':
                continue
            reports = name not in V.NO_LEVELS_FORCES
            grp = ('state police' if name in ('Policía Nacional', 'Guardia Civil') else
                   'regional police' if name in ('Ertzaintza', "Mossos d'Esquadra", 'Policía Foral de Navarra') else
                   'attached unit (U.A.)' if name.startswith('U.A.') else 'local police (PL), by region')
            police.append(panel_row(ym, name, u, f, r, grp, NAN, reports))

# June 2025 force table: not in the bulletin; previous transcription of the VioGén portal PDF
for fr in june_force:
    row = {'date': '2025-06-30', 'protocol_period': period('2025-06'), 'unit': fr['entity'].replace('PL Castilla - La Mancha', 'PL Castilla-La Mancha').replace('PL Region de Murcia', 'PL Región de Murcia'),
           'printed_label': fr['entity'], 'unit_type': NAN, 'parent_region': NAN, 'risk_levels_reported': True,
           'source_url': fr['source_url'], 'pdf_page': NAN,
           'extraction_method': 'previous manual transcription of VioGén portal PDF (portal not reachable here)',
           'qa_status': 'transcription reconciles exactly to the June 2025 bulletin national TOTAL; not re-read from PDF',
           'notes': 'supervised/inactive/total/victims not transcribed'}
    for c in LEVELS:
        row[c] = int(fr[c])
    row['active'] = int(fr['total_active'])
    for c in ['supervised', 'inactive', 'total', 'victims']:
        row[c] = NAN
    mp = row['medium'] + row['high'] + row['extreme']
    row['medium_plus'] = mp; row['medium_plus_pct'] = pct(mp, row['active'])
    n = row['unit']
    row['unit_type'] = ('state police' if n in ('Policía Nacional', 'Guardia Civil') else
                        'regional police' if n in ('Policía Foral de Navarra',) else
                        'attached unit (U.A.)' if n.startswith('U.A.') else 'local police (PL), by region')
    police.append(row)

police.sort(key=lambda x: (x['date'], x['unit']))
write(DATA / 'regional_monthly_panel.csv', regional, PANEL_FIELDS)
write(DATA / 'provincial_monthly_panel.csv', provincial, PANEL_FIELDS)
write(DATA / 'police_force_monthly_panel.csv', police, PANEL_FIELDS)

# ------------------------------------------------------------------ validation report
def add(ym, table, check, ok, detail=''):
    res = ok if isinstance(ok, str) else ('pass' if ok else 'FAIL')
    validation.append({'month': ym, 'table': table, 'check': check, 'result': res, 'detail': detail})

for ym in ALL_MONTHS:
    r = months.get(ym)
    if not r:
        add(ym, 'all', 'official bulletin available', 'not available',
            'no DGVG bulletin published for this month (HTTP 404, 11 Nov 2026)' if ym == '2026-10'
            else 'bulletin not processed')
        continue
    terr = r['tables'].get('territory', {}); force = r['tables'].get('force', {})
    for kind, t in (('territory', terr), ('police forces', force)):
        if t.get('status') == 'table not present in bulletin' and kind == 'police forces' and ym < FORCE_TABLE_START:
            add(ym, kind, 'table present in bulletin', 'not available',
                'police-institution table first printed in the February 2020 bulletin'); continue
        if t.get('status') == 'table not present in bulletin':
            add(ym, kind, 'table present in bulletin', 'not available',
                'not printed in this bulletin' + ('; previous VioGén portal transcription used, reconciles to the bulletin TOTAL'
                                                  if ym == '2025-06' else '')); continue
        if str(t.get('status', '')).startswith('image table not extracted'):
            add(ym, kind, 'table extracted', 'not available',
                'table printed as an image; not extracted' + ('; national row taken from the police-institution TOTAL'
                                                              if force.get('status') == 'reconciled' else '')); continue
        if 'units' not in t:
            add(ym, kind, 'extraction', False, t.get('error', '')); continue
        cols, prot = t['columns'], t['protocol']
        recs = {k: {'values': {c: v for c, v in u['values'].items()}, 'row_ok': True} for k, u in t['units'].items()}
        rowf = [f'{k}: {x}' for k, u in recs.items() for x in V.row_checks(u, cols, prot)]
        add(ym, kind, 'every row: risk levels sum to active; active+supervised+inactive = total', not rowf, '; '.join(rowf[:5]))
        add(ym, kind, 'printed data date equals month end', t['data_date'] == month_end(ym), t['data_date'] or 'not printed')
        fails = V.reconcile(recs, cols, prot, 'territory' if kind == 'territory' else 'force')
        if kind == 'territory':
            pf = [x for x in fails if 'provinces' in x]; rf = [x for x in fails if 'regions' in x]
            add(ym, kind, 'provinces sum to their region (all case columns)', not pf, '; '.join(pf[:5]))
            add(ym, kind, '19 regions sum to national TOTAL (all case columns)', not rf, '; '.join(rf[:5]))
        else:
            ff = [x for x in fails if 'forces' in x or 'institutions' in x]
            add(ym, kind, 'institutions sum to TOTAL (all case columns)', not ff, '; '.join(ff[:5]))
        if t.get('method', '').startswith('OCR'):
            add(ym, kind, 'OCR first-pass failures (before cell re-reading)', True,
                f"{len(t.get('fails_first_pass', []))} first-pass failures; rows re-read: {t.get('ocr_rows_reread', 0)}; "
                f"unreadable cells: {t.get('ocr_unreadable_cells', 0)} of {t.get('ocr_cells', 0)}")
    if terr.get('status') == 'reconciled' and force.get('status') == 'reconciled':
        a, b = terr['units']['TOTAL']['values'], force['units']['TOTAL']['values']
        diff = [c for c in terr['columns'] if c != 'victims' and a.get(c, 0) != b.get(c, 0)]
        add(ym, 'cross-table', 'territorial TOTAL equals police-force TOTAL', not diff, ', '.join(diff))
    h = hand_nat.get(ym)
    nrow = next(x for x in national if x['date'].startswith(ym))
    hm = str(nrow.get('reference_match', ''))
    if not h:
        continue                         # the reference series starts in January 2023
    add(ym, 'national', 'matches reference national series',
        True if hm.startswith('yes') else ('corrected: official PDF value used' if hm.startswith('no') else 'not checked'), hm)
for ym in ALL_MONTHS[-1:]:
    pass
write(DATA / 'validation_report.csv', validation, ['month', 'table', 'check', 'result', 'detail'])

# ------------------------------------------------------------------ extraction errors / issues
variants = {}
for ym, r in months.items():
    for kind, t in r['tables'].items():
        if t.get('status') == 'table not present in bulletin' and kind == 'force' and ym < FORCE_TABLE_START:
            continue                     # summarised once below
        if t.get('status') not in ('reconciled',):
            errors.append({'month': ym, 'table': kind, 'issue_type': 'table not extracted',
                           'detail': t.get('status', '') + ' ' + t.get('error', ''),
                           'resolution': 'June 2025 force table taken from previous portal transcription'
                           if (ym == '2025-06' and kind == 'force') else
                           'no regional or provincial rows; national row taken from the reconciled police-institution TOTAL'
                           if (kind == 'territory' and r['tables'].get('force', {}).get('status') == 'reconciled')
                           else 'none; left missing'})
        for a in t.get('printed_artefacts', []):
            errors.append({'month': ym, 'table': kind, 'issue_type': 'printed artefact in source',
                           'detail': f"{a['unit']} {a['column']} printed as '{a['printed']}' (spreadsheet scientific notation)",
                           'resolution': a.get('filled_from', 'left unreadable')})
        for lg in (t.get('ocr_resolution_log', []) if t.get('status') == 'reconciled' else []):
            ch = {k: (lg['before'][k], lg['after'][k]) for k in lg['after'] if lg['before'].get(k) != lg['after'][k]}
            errors.append({'month': ym, 'table': kind, 'issue_type': 'OCR cell re-read',
                           'detail': f"{lg['unit']}: " + '; '.join(f"{k} first read {'blank' if a is None else a} -> {b}"
                                                                    for k, (a, b) in ch.items()),
                           'resolution': 'only combination of OCR readings satisfying the '
                           + ('row identities and the parent-row identity' if 'parent' in lg['constraint'] else 'row identities')})
        for name, u in t.get('units', {}).items():
            pk, ck = V.key(u['printed_label']), V.key(name)
            if pk != ck and V.re.sub(r'1$', '', pk) != ck:
                variants.setdefault((kind, u['printed_label'], name), []).append(ym)
for (kind, printed, canon), ms in sorted(variants.items()):
    errors.append({'month': f'{min(ms)} to {max(ms)} ({len(ms)} months)', 'table': kind, 'issue_type': 'name variant harmonised',
                   'detail': f"printed '{printed}'", 'resolution': f"mapped to '{canon}'"})
errors.append({'month': f'2018-01 to 2020-01', 'table': 'force', 'issue_type': 'table not published',
               'detail': 'the police-institution table is first printed in the February 2020 bulletin',
               'resolution': 'no police-institution rows before February 2020'})
errors.append({'month': '2026-10', 'table': 'all', 'issue_type': 'source not available',
               'detail': 'BEM_Octubre_2026.pdf returns HTTP 404 (11 Nov 2026); VioGén portal listing disallows automated access (robots.txt)',
               'resolution': 'national row kept from press relay, flagged unverified; no subnational rows'})
errors.append({'month': '2025-06', 'table': 'police forces', 'issue_type': 'source not reachable',
               'detail': 'force table not printed in the June 2025 bulletin; VioGén portal PDF not reachable from this environment',
               'resolution': 'previous manual transcription kept; reconciles exactly to the bulletin national TOTAL'})
write(DATA / 'extraction_errors.csv', errors, ['month', 'table', 'issue_type', 'detail', 'resolution'])
write(DATA / 'national_changelog.csv', changelog, ['date', 'field', 'previous_value', 'corrected_value',
      'previous_source', 'previous_source_kind', 'corrected_source', 'reason'])

# ------------------------------------------------------------------ coverage
coverage = []
for ym in ALL_MONTHS:
    r = months.get(ym)
    for b in ('national', 'regional', 'provincial', 'police forces'):
        if not r and ym == '2026-10':
            st = 'press relay only (no official bulletin yet)' if b == 'national' else 'not available: no official bulletin yet'
        elif not r:
            st = 'not available: bulletin not processed'
        else:
            t = r['tables'].get('force' if b == 'police forces' else 'territory', {})
            nrow = next(x for x in national if x['date'].startswith(ym))
            if b == 'national' and str(nrow.get('verification_status', '')).startswith('verified') \
                    and t.get('status') != 'reconciled':
                st = 'extracted and reconciled (' + str(nrow['extraction_method']) + ')'
            elif t.get('status') == 'reconciled':
                st = 'extracted and reconciled (' + method_of(t) + ')'
            elif ym == '2025-06' and b == 'police forces':
                st = 'previous transcription of portal PDF; reconciles to bulletin total (not re-read)'
            elif b == 'police forces' and ym < FORCE_TABLE_START:
                st = 'not available: police-institution table first printed Feb 2020'
            else:
                st = 'not extracted: ' + str(t.get('status'))
        n = {'national': 1, 'regional': len([x for x in regional if x['date'].startswith(ym)]),
             'provincial': len([x for x in provincial if x['date'].startswith(ym)]),
             'police forces': len([x for x in police if x['date'].startswith(ym)])}[b]
        coverage.append({'month': ym, 'breakdown': b, 'status': st, 'rows': n if 'not available' not in st else 0})
write(DATA / 'month_by_month_coverage.csv', coverage, ['month', 'breakdown', 'status', 'rows'])

# ------------------------------------------------------------------ source manifest
manifest = []
for ym in ALL_MONTHS:
    r = months.get(ym)
    if not r:
        manifest.append({'month': ym, 'source': 'none', 'url': V.BEM_URL.format(m=V.MONTHS_ES[int(ym[5:]) - 1], y=ym[:4]),
                         'status': 'HTTP 404 on 11 Nov 2026 (not yet published)'})
        continue
    p = BEM / r['file']
    pages = {k: t.get('pdf_page', '') for k, t in r['tables'].items()}
    ex = sorted(glob.glob(str(DEL / 'sources' / '01_statistics' / 'bulletins' / f'{ym}_*.pdf')))
    manifest.append({'month': ym, 'source': 'DGVG Boletín estadístico mensual', 'file': r['file'], 'url': r['url'],
                     'pdf_pages_total': r.get('n_pages', ''), 'territorial_table_page': pages.get('territory', ''),
                     'police_force_table_page': pages.get('force', ''),
                     'data_date_printed': r['tables'].get('territory', {}).get('data_date', ''),
                     'text_layer_or_ocr': method_of(r['tables'].get('territory', {})),
                     'sha256_full_bulletin': sha256(p) if p.exists() else '', 'bytes_full_bulletin': p.stat().st_size if p.exists() else '',
                     'excerpt_in_package': os.path.basename(ex[0]) if ex else '', 'downloaded': '2026-11-10/11',
                     'status': 'downloaded and parsed'})
write(DATA / 'source_manifest.csv', manifest, ['month', 'source', 'file', 'url', 'pdf_pages_total', 'territorial_table_page',
      'police_force_table_page', 'data_date_printed', 'text_layer_or_ocr', 'sha256_full_bulletin', 'bytes_full_bulletin',
      'excerpt_in_package', 'downloaded', 'status'])

print('national', len(national), '| regional', len(regional), '| provincial', len(provincial), '| police', len(police))
print('validation rows', len(validation), 'FAIL', sum(v['result'] == 'FAIL' for v in validation))
print('changelog', len(changelog), '| issues', len(errors))
