"""Source tests: the catalogue must equal the Annex 1 transcription, and the transcription must equal the thesis PDF.

The PDF check runs when the thesis is available locally (it is not redistributed in this package):
    export VPR4_THESIS_PDF=/path/to/lopez_ossorio_juan_jose.pdf     (MD5 5d111ff6d9a6717d14f2c265544406f1)
Download: https://repositorio.uam.es/server/api/core/bitstreams/09c11ef0-a544-439a-a623-4e492db41610/content
"""
import csv
import hashlib
import os
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pytest  # noqa: E402

from tools.annex1_transcription import ROWS, verify_against_pdf  # noqa: E402

CATALOG = list(csv.DictReader(open(ROOT.parents[1] / 'data' / '02_historical_scoring' / 'vpr4_0_annex1_indicators.csv', encoding='utf-8-sig')))

# Table 1, p. 193 ("Indicadores críticos incluidos en la Valoración Policial del Riesgo (VPR 4.0)"), typed independently
TABLE1 = {
    1: ('Violencia física grave o muy grave', 'I2_physical_severe'),
    2: ('Violencia sexual grave o muy grave', 'I3_sexual_severe'),
    3: ('Empleo de arma blanca', 'I5_knife'),
    4: ('Amenazas de muerte por parte del agresor', 'I7_death_threat'),
    5: ('Escalada de las agresiones o amenazas en los últimos 6 meses', 'I8_escalation'),
    6: ('En los últimos 6 meses el agresor muestra celos exagerados', 'I9_jealousy'),
    7: ('En los últimos 6 meses el agresor muestra conductas de acoso', 'I11_stalking'),
    8: ('En el último año el agresor agrede físicamente a terceros o animales', 'I14_attack_others_animals'),
    9: ('El agresor presenta un trastorno mental', 'I20_mental_disorder'),
    10: ('El agresor ideas o intentos de suicidio', 'I21_suicide_ideation'),
    11: ('El agresor mantiene algún tipo de adicción o conductas de abuso de alcohol, drogas o fármacos', 'I22_substance_abuse'),
    12: ('La víctima ha expresado su intención de romper la relación hace menos de 6 meses', 'I36_recent_separation'),
    13: ('La víctima piensa que el agresor es capaz de agredirla con mucha violencia o incluso matarla', 'I39_victim_fear_lethal'),
}


def test_transcription_counts():
    assert len(ROWS) == 63
    w = [Decimal(r[4]) for r in ROWS]
    assert sum(w) == Decimal('77.019')
    assert sum(1 for x in w if x) == 32
    assert len({r[2] for r in ROWS if r[2]}) == 39
    assert [r[0] for r in ROWS if not r[2]] == [10, 15, 38]


def test_catalog_equals_transcription():
    assert len(CATALOG) == len(ROWS)
    for c, (row, page, group, label, value) in zip(CATALOG, ROWS):
        assert int(c['row']) == row and int(c['page']) == page
        assert c['indicator'] == group
        assert c['spanish_source_label'] == label
        assert c['weight_as_printed'] == value and Decimal(c['weight']) == Decimal(value)


def test_critical_flags_match_table1():
    flagged = {int(c['critical_table1_number']): c['code'] for c in CATALOG if c['critical_indicator'] == 'yes'}
    assert flagged == {n: code for n, (_, code) in TABLE1.items()}


def test_mental_disorder_fixed_score():
    # p. 192: "salvo trastorno mental que se le asignó una puntuación directa de 3"
    assert next(c for c in CATALOG if c['code'] == 'I20_mental_disorder')['weight'] == '3.000'


@pytest.mark.skipif(not os.environ.get('VPR4_THESIS_PDF'), reason='set VPR4_THESIS_PDF to the UAM thesis PDF')
def test_transcription_against_thesis_pdf():
    pytest.importorskip('pymupdf')
    pdf = os.environ['VPR4_THESIS_PDF']
    assert hashlib.md5(Path(pdf).read_bytes()).hexdigest() == '5d111ff6d9a6717d14f2c265544406f1'
    report = verify_against_pdf(pdf)
    assert all(r['label_found_in_pdf_text'] for r in report), [r for r in report if not r['label_found_in_pdf_text']]
