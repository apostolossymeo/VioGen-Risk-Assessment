"""Package consistency: the notebook carries the current engine and catalogue, ran without errors, and the
verification matrix covers every Annex 1 row."""
import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parents[1] / 'data' / '02_historical_scoring'
NB = ROOT / 'VioGen_Module2_Historical_Research_Lab.ipynb'


def _code_cells():
    return [c for c in json.loads(NB.read_text(encoding='utf-8'))['cells'] if c['cell_type'] == 'code']


def test_notebook_embeds_the_current_engine_and_catalogue():
    setup = ''.join(_code_cells()[0]['source'])
    tree = ast.parse(setup)
    embedded = next(ast.literal_eval(n.value) for n in tree.body
                    if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'EMBEDDED')
    for name, text in embedded.items():
        path = (DATA if name.endswith('.csv') else ROOT) / name
        assert text == path.read_text(encoding='utf-8'), f'{name}: run python make_notebook.py'
        assert hashlib.sha256(text.encode('utf-8')).hexdigest() in setup


def test_notebook_was_executed_without_errors():
    cells = _code_cells()
    assert all(c.get('execution_count') for c in cells), 'notebook not executed'
    assert not [o for c in cells for o in c.get('outputs', []) if o.get('output_type') == 'error']


def test_verification_matrix_covers_every_row_and_uses_known_statuses():
    rows = list(csv.DictReader(open(DATA / 'SOURCE_VERIFICATION_MATRIX.csv', encoding='utf-8')))
    annex = [r for r in rows if r['scope'] == 'annex1_row']
    assert [r['claim_id'] for r in annex] == [f'A1-{i:02d}' for i in range(1, 64)]
    assert {r['status'] for r in rows} <= {'verified', 'corrected', 'inferred', 'assumption', 'not_documented'}
    catalog = list(csv.DictReader(open(DATA / 'vpr4_0_annex1_indicators.csv', encoding='utf-8-sig')))
    for m, c in zip(annex, catalog):
        assert m['value_in_package'].startswith(f"weight {c['weight']};")
    assert sorted(int(r['claim_id'][3:]) for r in annex if r['status'] == 'corrected') == [10, 15, 18, 20, 38, 40, 41]


def test_scenario_csv_and_json_agree():
    js = json.loads((DATA / 'hypothetical_scenarios.json').read_text(encoding='utf-8'))
    cs = list(csv.DictReader(open(DATA / 'hypothetical_scenarios.csv', encoding='utf-8')))
    assert [r['name'] for r in js] == [r['name'] for r in cs]
    assert all(abs(float(c['score_min']) - j['score_min']) < 1e-9 for c, j in zip(cs, js))
