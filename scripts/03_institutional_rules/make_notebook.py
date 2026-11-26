"""Build VioGen_Module3_Research.ipynb: standalone (the four src modules are embedded), runs in Colab or locally.

    python make_notebook.py
    jupyter nbconvert --to notebook --execute --inplace VioGen_Module3_Research.ipynb
"""
import hashlib
from pathlib import Path

import nbformat as nbf

P = Path(__file__).resolve().parent
MODULES = ['module3_sources.py', 'module3_records.py', 'annex_measures.py', 'decision_rules.py']
EMB = {m: (P / 'src' / m).read_text(encoding='utf-8') for m in MODULES}
SHA = {m: hashlib.sha256(t.encode('utf-8')).hexdigest() for m, t in EMB.items()}

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip('\n')))  # noqa: E731
py = lambda s: cells.append(nbf.v4.new_code_cell(s.strip('\n')))     # noqa: E731

md(r'''
# VioGén investigation · Module 3
## From a risk level to an administrative obligation: where does discretion sit in the 2019 and 2025 police protocols?

**Question.** Who decides what, between the recording officer, the system's designers, the specialised police unit, police management, courts, prosecutors and the victim, once VioGén assigns a risk level? And which of the 2019→2025 differences were actually introduced by VioGén-2?

> **Scope.** An institutional reading of two protocol texts, Instrucción 4/2019 and Instrucción 1/2025, plus the instructions issued between them. The automatic risk level is an **input**. It is never computed, and VioGén-2's scoring is neither reconstructed nor approximated. Everything below describes **formal rules**, not what police do. The 50 "pathways" are combinations of rules, not cases.

**Evidence grades.** A = primary text read. B = official government summary. C = secondary source (press, police academy). D = inference from the absence of a rule in the available sources.
''')

md('### 0 · Setup (the research modules are embedded; the full package adds the PDFs, the extracted texts and the tests)')
py('''
import hashlib, sys
from pathlib import Path
EMBEDDED = {
''' + ''.join(f'    {m!r}: {t!r},\n' for m, t in EMB.items()) + '''}
EMBEDDED_SHA256 = ''' + repr(SHA) + '''
base = Path.cwd()
source_dir = Path('scripts/03_institutional_rules/src')
repo = next((p for p in (base, *base.parents) if (p / source_dir / 'decision_rules.py').is_file()), None)
src = repo / source_dir if repo is not None else base / '_module3_src'
src.mkdir(exist_ok=True)
for name, text in EMBEDDED.items():
    p = src / name
    if p.exists():
        same = hashlib.sha256(p.read_bytes()).hexdigest() == EMBEDDED_SHA256[name]
        print(f'{name}: local copy {"identical to" if same else "DIFFERENT FROM"} the embedded one')
    else:
        p.write_text(text, encoding='utf-8', newline=''); print(f'{name}: written from the embedded copy')
sys.path.insert(0, str(src))

import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_colwidth', 120); pd.set_option('display.width', 200)
from module3_sources import SOURCES, CLAUSES, clause
from module3_records import RULES, COMPARISON, CHRONOLOGY, UNCERTAINTY
from annex_measures import MEASURES, MEASURE_CHANGES
import decision_rules as D
from decision_rules import Scenario as S
''')

md(r'''
### 1 · Sources and provenance

* **2019.** The official PDF on the Delegación del Gobierno contra la Violencia de Género site. It is a scan, so it was OCR'd and checked against the page images. Printed page = PDF page.
* **2025.** A signed copy carrying the *código seguro de verificación* (CSV) GEN-61b6…598b and the signature of the Secretary of State (15/01/2025).
  * No government-hosted copy was found.
  * Two third-party copies are byte-identical, and a third, unstamped copy has identical text.
  * The official CSV check at sede.administracion.gob.es is captcha-protected and was **not** performed.
* **Intervening instructions.** These are named in the 2025 derogation list (p. 4). Only Protocolo Cero (5/2021) was available in full on an official site. For the others there are official press summaries (grade B) or secondary sources (grade C).
''')
py('''
src_df = pd.DataFrame(SOURCES)[['source_id', 'kind', 'date_signed', 'host_type', 'pages', 'sha256']]
src_df['sha256'] = src_df['sha256'].str[:12]
src_df
''')
py('''
# Every clause excerpt is re-found on its declared PDF page by the package's test suite (tests/test_data_integrity.py).
if repo is not None and (repo / 'sources/03_institutional_rules/text').is_dir():
    from quote_check import check_all
    res = pd.DataFrame(check_all(CLAUSES))
    print(f"{res.found.sum()} of {len(res)} clause excerpts found on their declared page "
          f"({(res.method == 'fuzzy_ocr').sum()} from the 2019 OCR, minimum similarity {res.loc[res.method == 'fuzzy_ocr', 'score'].min()})")
else:
    print(f'{len(CLAUSES)} clauses indexed; run the package tests to re-find each excerpt in the source texts.')
''')

md(r'''
### 2 · What the audit of version 1 found

The audit covered every version-1 record: 35 rules, 16 comparisons and 13 measures. Both protection annexes are now transcribed in full: 26 items for 2019 and 41 for 2025.

The main corrections:
* **The 2019 first-VPER deadline.** It covers Bajo and above, not just "medium+".
* **Special relevance.** The 7-day clause is a minimum wait, not an exception to the deadline, and it already existed in 2019.
* **Assessment without a complaint.** This duty is already in the 2019 text; Protocolo Cero did not introduce it.
* **Supervised cases.** They come from Instrucción 2/2024, not from 2022.
''')
py('''
r = pd.DataFrame(RULES)
display(pd.crosstab(r.protocol, r.v1_status))
r[r.v1_status.isin(['corrected'])][['rule_id', 'decision_point', 'correction_note']]
''')

md(r'''
### 3 · What changed when: attribution of each 2019→2025 difference

A comparison of two documents cannot tell *when* a rule changed. Instrucción 1/2025 consolidates six earlier instructions (p. 4). The table gives, for each topic, where the change was introduced and how strong the evidence is.
''')
py('''
c = pd.DataFrame(COMPARISON)
display(pd.crosstab(c.attribution, c.evidence_grade))
c[['topic_id', 'topic', 'classification', 'attribution', 'evidence_grade', 'attribution_evidence']]
''')

md(r'''
**The non-location rule changed twice.** This is the clearest case of why the intervening instructions matter.

| Period | Victim not located for at least | Evidence |
|---|---|---|
| 2019 | one month | 2.7, p. 9 (A) |
| March 2024 (2/2024) | six months | La Marea quoting the instruction; DEPOL (C) |
| 2025 | three months | 7.2.1, p. 18 (A) |

A 2019-vs-2025 reading would call this a tightening. Measured against 2024, it is a shortening.
''')

md('### 4 · Who decides what (formal rules)')
py('''
display(pd.crosstab([r.protocol, r.stage], r.modality).loc[2025])
r[r.protocol == 2025][['rule_id', 'decision_point', 'decision_owner', 'modality', 'accountability_trail']]
''')

md(r'''
### 5 · The low-risk restructuring

In 2025, "no apreciado" disappears and Bajo is split by whether judicial measures are in force (p. 11). The engine runs the four relevant category labels through the same procedural questions.
''')
py('''
def row(label, s):
    f = D.first_vper(S(**{**s.__dict__, 'first_vper_done': False}))
    l = D.later_vper(S(**{**s.__dict__, 'first_vper_done': True}))
    fl = D.protection_floor(s.version, s.algorithm_category, s.judicial_measures)
    return dict(category=label, first_vper=f"max {f['max_days']} d" if f['max_days'] else f['status'],
                later_vper=f"< {l['value']} {l['unit']}", ordinary_inactivation=D.ordinary_inactivation(S(**{**s.__dict__, 'first_vper_done': True}))['status'],
                aggressor_told=('A1-2019-09' in fl['measure_ids']) or ('A2-2025-15' in fl['measure_ids']), annex_items=fl['n_items'])
pd.DataFrame([row('2019 no apreciado', S(2019, 'no_appreciable')), row('2025 Bajo, no measures', S(2025, 'low')),
              row('2019 bajo', S(2019, 'low')), row('2025 Bajo, with measures', S(2025, 'low', judicial_measures=True))])
''')
md(r'''
**Reading.** In deadlines and intervals, "Bajo without judicial measures" follows the 2019 "no apreciado" rules: no stated first-VPER deadline, and under 90 days thereafter. "Bajo with measures" follows the old "bajo". Two things are new for this group:

* **More written measures.** The protection floor for this group went from 3 items to 15, close to the 2019 bajo floor, minus the items that tell the aggressor his case is under police control and track his prison movements, which now require judicial measures.
* **Stricter conditions for closing a case.** Ordinary inactivation now needs a positive finding that a repeat is objectively unlikely, a contact with the victim and a reassessment.

None of this says which real cases moved where. The algorithm was recalibrated, according to the Moncloa press release of 15/01/2025.
''')

md('### 6 · Reassessment, new incidents and court notification')
py('''
cases = [('2019 Medio, first VPER', S(2019, 'medium', first_vper_done=False)), ('2025 Medio, first VPER', S(2025, 'medium', first_vper_done=False)),
         ('2025 Alto, special relevance', S(2025, 'high', special_relevance=True, first_vper_done=False)),
         ('2025 Extremo, special relevance', S(2025, 'extreme', special_relevance=True, first_vper_done=False)),
         ('2025 Bajo, measures unknown', S(2025, 'low', judicial_measures=None, first_vper_done=False))]
pd.DataFrame([dict(case=n, **{k: D.first_vper(s)[k] for k in ('status', 'min_days', 'max_days', 'clause_ids')}) for n, s in cases])
''')
py('''
pd.DataFrame([dict(protocol=y, change=f'{a} -> {b}', oficio=D.vper_court_notification(S(y, a), a, b)['individual_oficio'])
              for y in (2019, 2025) for a, b in (('medium', 'high'), ('medium', 'low'))])
''')

md('### 7 · Inactivation, supervision and reactivation')
py('''
rows = []
for y in (2019, 2025):
    for lvl in ('low', 'medium', 'high'):
        rows.append(dict(protocol=y, level=lvl,
                         renunciation=D.exceptional_inactivation(S(y, lvl, judicial_measures=False), 'victim_renounces')['status'],
                         not_located_2_months=D.exceptional_inactivation(S(y, lvl), 'victim_not_located', 2)['status'],
                         verb=D.exceptional_inactivation(S(y, lvl), 'death')['verb']))
pd.DataFrame(rows)
''')
py('''
sup = D.supervision(S(2025, 'low', medium_plus_last_3m=True, special_relevance_or_minors_last_12m=False, two_plus_complaints_first_6m=False))
print(sup['reason']); pd.Series(sup['procedure'])
''')

md(r'''
### 8 · The protection floor as written

Both annexes are transcribed item by item. Each item is classified by how its wording obliges: a bare instruction, a condition of fact, an officer's judgement, advice to the victim, a request to another authority, or dependence on available means.
''')
py('''
m = pd.DataFrame(MEASURES)
display(pd.crosstab(m.modality, m.year))
pd.DataFrame(MEASURE_CHANGES, columns=['topic', 'measure_2019', 'measure_2025', 'change_type', 'note'])
''')
py('''
ct = pd.crosstab(m.modality, m.year).reindex(['mandatory', 'conditional_fact', 'conditional_judgement', 'advice_to_victim',
                                              'request_other_authority', 'resource_contingent', 'discretionary_option']).fillna(0)
ax = ct.plot.barh(color=['#2a78d6', '#eb6834'], figsize=(8, 3.6), edgecolor='#fcfcfb')
ax.invert_yaxis(); ax.set_xlabel('annex items'); ax.set_ylabel(''); ax.set_title('How the annex items oblige, 2019 vs 2025')
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
plt.tight_layout(); plt.show()
''')

md('### 9 · The 50 abstract pathways (combinations of rules, not cases)')
py('''
paths = pd.DataFrame(D.enumerate_abstract_pathways())
display(paths.groupby(['year', 'first_vper_status']).size())
paths.head(8)
''')

md(r'''
### 10 · Findings, limits and questions for interviews

The full memo, with page references, is `FINDINGS_MEMO.md`. In short:

1. **Discretion over the automatic level is upward-only and old.** It dates from Instrucción 7/2016 at least, and VioGén-2 did not change it. The 2025 wording that the officer adopts the final decision "en acuerdo o desacuerdo" does not create a downward route. Any downward effect has to come through input coding.
2. **The low-risk restructuring is partly a relabelling.** At the procedural level, "Bajo without judicial measures" takes over the deadlines and intervals of the old "no apreciado", with a larger written floor and stricter conditions for closing the case.
3. **Within Bajo, a court's decision now sets the police schedule.** Whether judicial measures exist decides the first-VPER deadline (15 days or none), the interval (60 or 90 days), whether the case can be inactivated, and whether the aggressor is told his case is under police control and his prison movements are checked. In 2019 neither the bajo interval nor those two items depended on it. At Medio, the device request now depends on the system's special-relevance flag.
4. **Case closure is where the rules moved most, and 2024 matters as much as 2025.** Supervised cases came in 2/2024; the non-location threshold went 1 → 6 → 3 months; renunciation narrowed from any level (2019) to no apreciado/bajo/medio (2024) to Bajo/Medio (2025); exceptional inactivation moved from "podrá" to "se procederá"; ordinary inactivation now needs a positive finding.
5. **The accountability trail is uneven.** Exceptional-inactivation causes, capacity shortfalls and a missing supervision interview must be recorded. The protection measures actually taken only "should be recorded where possible". Courts now see the "No se sabe" answers, but receive a routine VPER only when the level rises, and no clause requires telling them about an ordinary inactivation.

**What the texts cannot tell us:** override frequency, delivery of measures, how "No se sabe" is scored, how Bajo cases split by judicial measures, and how supervised cases are handled in practice. See `INTERVIEW_PROMPTS.md`.
''')
py('''
pd.DataFrame(UNCERTAINTY, columns=['item', 'type', 'question', 'current_evidence', 'confidence', 'how_to_resolve'])[['item', 'type', 'question', 'confidence']]
''')

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}}
nbf.write(nb, P / 'VioGen_Module3_Research.ipynb')
print('cells', len(cells))
