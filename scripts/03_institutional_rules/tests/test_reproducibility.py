"""Reproducibility: the build is deterministic, the notebook carries the current modules and ran cleanly."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / 'VioGen_Module3_Research.ipynb'
DATA = ROOT.parents[1] / 'data' / '03_institutional_rules'
OUTPUTS = sorted(p for p in DATA.iterdir() if p.is_file())


def _hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUTPUTS}


def test_build_is_deterministic():
    before = _hashes()
    subprocess.run([sys.executable, str(ROOT / 'build_module3.py')], check=True, capture_output=True, cwd=ROOT)
    assert _hashes() == before


def _code_cells():
    return [c for c in json.loads(NB.read_text(encoding='utf-8'))['cells'] if c['cell_type'] == 'code']


def test_notebook_embeds_current_modules():
    setup = ''.join(_code_cells()[0]['source'])
    tree = ast.parse(setup)
    emb = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'EMBEDDED')
    for name, text in emb.items():
        assert text == (ROOT / 'src' / name).read_text(encoding='utf-8'), f'{name}: run python make_notebook.py'


def test_notebook_executed_without_errors():
    cells = _code_cells()
    assert all(c.get('execution_count') for c in cells)
    assert not [o for c in cells for o in c.get('outputs', []) if o.get('output_type') == 'error']


def test_figures_present():
    names = {p.name for p in (ROOT.parents[1] / 'figures' / '03_institutional_rules').glob('*.png')}
    assert {'01_change_chronology.png', '02_decision_authority_map_2025.png', '03_low_risk_restructuring.png',
            '04_annex_measure_modalities.png'} <= names
