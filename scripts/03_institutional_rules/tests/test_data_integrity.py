"""Source and dataset integrity: every excerpt re-found on its declared page, every reference resolves,
the verification matrix covers every version-1 record, and the bundled PDFs are the ones described."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
DATA = ROOT.parents[1] / 'data' / '03_institutional_rules'
sys.path.insert(0, str(ROOT / 'src'))
from annex_measures import MEASURE_CHANGES, MEASURES  # noqa: E402
from module3_records import CHRONOLOGY, COMPARISON, RULES, UNCERTAINTY  # noqa: E402
from module3_sources import CLAUSES, SOURCES  # noqa: E402
from quote_check import locate, pages  # noqa: E402

CLAUSE_IDS = {c['clause_id'] for c in CLAUSES}
MODALITY = {'mandatory', 'conditional', 'permitted_discretion', 'bounded_discretion', 'automated', 'not_provided', 'unspecified'}
ATTR = {'baseline_2019', 'predates_2019', 'continuity', 'introduced_between_2019_2025', 'first_documented_2025', 'changed_twice', 'origin_unknown'}


@pytest.mark.parametrize('c', CLAUSES, ids=[c['clause_id'] for c in CLAUSES])
def test_clause_excerpt_on_declared_page(c):
    r = locate(c['source_id'], c['quote_es'], c['pdf_pages'])
    assert r['found'], (c['clause_id'], r)


@pytest.mark.parametrize('m', MEASURES, ids=[m['measure_id'] for m in MEASURES])
def test_annex_item_on_declared_page(m):
    assert locate(m['source_id'], m['text_es'], m['pdf_page'])['found']


def test_bundled_pdfs_match_ledger():
    for s in SOURCES:
        if s['local_file']:
            assert hashlib.sha256((REPO / s['local_file']).read_bytes()).hexdigest() == s['sha256'], s['source_id']


def test_printed_page_numbers_equal_pdf_pages_2025():
    pg = pages('SES-1-2025')
    for n in (2, 13, 17, 37, 52):
        assert f'- {n} -' in pg[n]


def test_2025_derogation_list():
    p4 = re.sub(r'\s+', ' ', pages('SES-1-2025')[4])
    for inst in ('Instrucción 4/2019', 'Instrucción 7/2019', 'Instrucción 8/2021', 'Instrucción 11/2022', 'Instrucción 1/2023', 'Instrucción 2/2024'):
        assert inst in p4
    assert 'Instrucción 5/2021' not in p4                       # Protocolo Cero stays in force


def test_signature_stamp_on_every_2025_page():
    raw = (REPO / 'sources/03_institutional_rules/text/SES_1-2025_text_layer.txt').read_text(encoding='utf-8')
    assert raw.count('CSV : GEN-61b6-a6bd-ca9d-fb9e-612a-3074-2815-598b') == 52


def test_rules_reference_existing_clauses_of_their_own_protocol():
    for r in RULES:
        ids = [x.strip() for x in r['clause_ids'].split(';')]
        assert ids and all(i in CLAUSE_IDS for i in ids), r['rule_id']
        prefix = 'C19' if r['protocol'] == 2019 else 'C25'
        assert all(i.startswith(prefix) for i in ids), r['rule_id']


def test_rule_vocabularies_and_v1_coverage():
    v1 = {r['rule_id'] for r in csv.DictReader(open(DATA / 'version1_data/decision_authority_rules.csv', encoding='utf-8'))}
    ids = [r['rule_id'] for r in RULES]
    assert len(ids) == len(set(ids)) and v1 <= set(ids) and len(v1) == 35
    for r in RULES:
        assert r['modality'] in MODALITY and r['attribution'] in ATTR and r['v1_status'] in {'verified', 'qualified', 'corrected', 'new'}
        assert (r['rule_id'] in v1) == (r['v1_status'] != 'new'), r['rule_id']
        if r['v1_status'] in ('qualified', 'corrected'):
            assert r['correction_note'], r['rule_id']


def test_comparison_rows():
    rule_ids = {r['rule_id'] for r in RULES}
    for t in COMPARISON:
        assert t['attribution'] in ATTR and t['evidence_grade'][0] in 'ABCD'
        assert all(x.strip() in rule_ids for x in t['rule_ids'].split(';')), t['topic_id']
        if t['evidence_grade'][0] in 'BC':
            assert t['attribution_evidence'], t['topic_id']


def test_annex_transcription_is_complete():
    assert sum(m['year'] == 2019 for m in MEASURES) == 26 and sum(m['year'] == 2025 for m in MEASURES) == 41
    assert {m['level'] for m in MEASURES if m['year'] == 2025} == {'general', 'low', 'medium', 'high', 'extreme', 'minors'}
    assert all(m['exhaustive'] for m in MEASURES)
    ids = {m['measure_id'] for m in MEASURES}
    for _, a, b, _, _ in MEASURE_CHANGES:
        assert (not a or a in ids) and (not b or b in ids)


def test_verification_matrix_covers_every_v1_record():
    rows = list(csv.DictReader(open(DATA / 'SOURCE_VERIFICATION_MATRIX.csv', encoding='utf-8')))
    by = {}
    for r in rows:
        by.setdefault(r['origin'], []).append(r)
    assert len(by['v1_rule']) == 35 and len(by['v1_comparison']) == 16 and len(by['v1_measure']) == 13
    assert len(by['initial_hypothesis']) == 7
    assert {r['status'] for r in by['v1_rule'] + by['v1_comparison'] + by['v1_measure']} <= {'verified', 'qualified', 'corrected'}
    assert all(r['location'] for r in by['v1_rule'] + by['v2_new_rule'])


def test_sources_chronology_uncertainty():
    sids = {s['source_id'] for s in SOURCES}
    assert all(c['source_id'] in sids for c in CHRONOLOGY)
    assert [c['order'] for c in CHRONOLOGY] == sorted(c['order'] for c in CHRONOLOGY)
    assert len({u[0] for u in UNCERTAINTY}) == len(UNCERTAINTY)


def test_export_matches_records():
    ex = json.loads((DATA / 'research_export.json').read_text(encoding='utf-8'))
    assert ex['schema'].endswith('/2.0') and 'NOT application logic' in ex['status']
    assert len(ex['rules']) == len(RULES) and len(ex['measures']) == len(MEASURES) and len(ex['clauses']) == len(CLAUSES)
    assert len(ex['abstract_pathways']) == 50


def test_no_v1_root_duplicates_left():
    assert not (ROOT / 'protocol_comparison.csv').exists() and not (ROOT / 'enumerated_abstract_pathways.csv').exists()
