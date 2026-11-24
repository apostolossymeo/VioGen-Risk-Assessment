"""Re-find every clause excerpt in the extracted source text, on the declared PDF page(s).

Text-layer sources (2025, 2021): exact match after whitespace / quote-mark normalisation.
Scanned source (2019, Tesseract OCR): best token-sequence similarity >= 0.90 on the declared page(s),
because OCR introduces character errors (the excerpts themselves were transcribed from the page images).
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEXT = {'SES-4-2019': ROOT / 'sources/03_institutional_rules/text/SES_4-2019_OCR_tesseract_spa.txt',
        'SES-1-2025': ROOT / 'sources/03_institutional_rules/text/SES_1-2025_text_layer.txt',
        'SES-5-2021': ROOT / 'sources/03_institutional_rules/text/SES_5-2021_text_layer.txt'}
FUZZY = {'SES-4-2019'}
THRESHOLD = 0.90
_PAGE = re.compile(r'=========== PDF PAGE (\d+) ===========')
_NOISE = [r'Código seguro de Verificación[^\n]*\n', r'https://sede\.administracion\.gob\.es/pagSedeFront/servicios/consultaCSV\.htm',
          r'CSV : GEN-[0-9a-f-]+', r'DIRECCIÓN DE VALIDACIÓN :', r'FIRMANTE\(1\) : RAFAEL PEREZ RUIZ \| FECHA : 15/01/2025 17:10 \| Sin acción específica']


def norm(s: str) -> str:
    s = s.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'").replace(' ', ' ')
    s = s.replace('–', '-').replace('—', '-')
    return re.sub(r'\s+', ' ', s).strip()


@lru_cache(maxsize=None)
def pages(source_id: str) -> dict[int, str]:
    raw = TEXT[source_id].read_text(encoding='utf-8')
    for pat in _NOISE:
        raw = re.sub(pat, ' ', raw)
    parts = _PAGE.split(raw)
    out = {}
    for i in range(1, len(parts), 2):
        out[int(parts[i])] = parts[i + 1]
    return out


def page_list(spec: str) -> list[int]:
    out = []
    for chunk in str(spec).replace(' ', '').split(','):
        if '-' in chunk:
            a, b = chunk.split('-')
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(chunk))
    return out


def _tokens(s: str) -> list[str]:
    return re.findall(r'\w+', norm(s).lower())


def locate(source_id: str, quote: str, page_spec: str) -> dict:
    pg = pages(source_id)
    declared = page_list(page_spec)
    text = ' '.join(pg.get(p, '') for p in declared)
    if source_id not in FUZZY:
        found = norm(quote) in norm(text)
        anywhere = [p for p, t in pg.items() if norm(quote) in norm(t)]
        return dict(found=found, score=1.0 if found else 0.0, method='exact', pages_found=anywhere)
    q = _tokens(quote)
    t = _tokens(text)
    best = 0.0
    firsts = set(q[:3])
    for i, tok in enumerate(t):
        if tok in firsts:
            for w in (len(q) - 1, len(q), len(q) + 1, len(q) + 2):
                r = SequenceMatcher(None, q, t[i:i + w], autojunk=False).ratio()
                best = max(best, r)
    return dict(found=best >= THRESHOLD, score=round(best, 3), method='fuzzy_ocr', pages_found=declared if best >= THRESHOLD else [])


def check_all(clauses) -> list[dict]:
    rows = []
    for c in clauses:
        r = locate(c['source_id'], c['quote_es'], c['pdf_pages'])
        rows.append(dict(clause_id=c['clause_id'], **r))
    return rows
