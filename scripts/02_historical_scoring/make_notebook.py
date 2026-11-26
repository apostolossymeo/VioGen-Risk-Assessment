"""Build VioGen_Module2_Historical_Research_Lab.ipynb (standalone: the engine and the catalogue are embedded).

Run:  python make_notebook.py
Then: jupyter nbconvert --to notebook --execute --inplace VioGen_Module2_Historical_Research_Lab.ipynb
"""
import hashlib
from pathlib import Path

import nbformat as nbf

P = Path(__file__).resolve().parent
ENGINE = (P / 'vpr4_historical.py').read_text(encoding='utf-8')
CATALOG = (P.parents[1] / 'data' / '02_historical_scoring' / 'vpr4_0_annex1_indicators.csv').read_text(encoding='utf-8')
SHA = {n: hashlib.sha256(t.encode('utf-8')).hexdigest() for n, t in
       (('vpr4_historical.py', ENGINE), ('vpr4_0_annex1_indicators.csv', CATALOG))}

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip('\n')))   # noqa: E731
py = lambda s: cells.append(nbf.v4.new_code_cell(s.strip('\n')))       # noqa: E731

# ------------------------------------------------------------------------------------------------ 0. framing
md(r'''
# VioGén investigation · Module 2
## How a 2016 police form turned answers into a risk level, and who decided what along the way

**Research question.** Where is discretion located when the Spanish police risk form VPR4.0 (2016) converts recorded facts into an administrative risk level: with the **officer** who records the answers, with the **designers** who set weights and cut-offs, or with the **procedural rules** that attach consequences to a level?

> **Historical reconstruction only.** This is the VPR4.0 form described in a 2016 doctoral thesis. It is **not VioGén 2** (in force since 30 June 2025), not the operational police software, and it must never be used to assess a real person. Every case in this notebook is fictitious. Scores are additive units from the thesis, **not probabilities and not measures of danger**. Nothing here explains a 2025–2026 classification or a police decision.

**Primary source.** Juan José López Ossorio, *Construcción y validación de los formularios de valoración policial del riesgo de reincidencia y violencia grave contra la pareja (VPR4.0–VPER4.0)*, doctoral thesis, Universidad Autónoma de Madrid, 2016. PDF from the [UAM repository](https://repositorio.uam.es/server/api/core/bitstreams/09c11ef0-a544-439a-a623-4e492db41610/content) (336 pages, MD5 `5d111ff6d9a6717d14f2c265544406f1`). Page numbers below are the thesis's printed page numbers, which equal the PDF page numbers.

**How to read the evidence labels used below**

| Label | Meaning |
|---|---|
| **DOCUMENTED** | stated in the thesis; page given |
| **INFERRED** | follows from the documented form structure, but the thesis does not state it in so many words |
| **ASSUMPTION** | a choice made by this reconstruction because the source is silent; alternatives are shown |
| **COMPUTED** | an exact calculation over the documented rule (a property of the rule, not of real cases) |
''')

md(r'''
### 0 · Setup

The engine (`vpr4_historical.py`) and the verified catalogue (`vpr4_0_annex1_indicators.csv`) are embedded below, so the notebook runs on its own in Google Colab. Inside the repository, the notebook uses the script and catalogue in their respective directories and compares them with the embedded copies.
''')

py('''
import hashlib, sys
from pathlib import Path

EMBEDDED = {
    'vpr4_historical.py': ''' + repr(ENGINE) + ''',
    'vpr4_0_annex1_indicators.csv': ''' + repr(CATALOG) + ''',
}
EMBEDDED_SHA256 = ''' + repr(SHA) + '''

cwd = Path.cwd()
script_dir = Path('scripts/02_historical_scoring')
repo = next((p for p in (cwd, *cwd.parents) if (p / script_dir / 'vpr4_historical.py').is_file()), None)
base = repo / script_dir if repo is not None else cwd
data_dir = repo / 'data' / '02_historical_scoring' if repo is not None else cwd
for name, text in EMBEDDED.items():
    path = (data_dir if name.endswith('.csv') else base) / name
    if not path.exists():
        path.write_text(text, encoding='utf-8', newline='')
        print(f'{name}: written from the embedded copy')
    else:
        same = hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest() == EMBEDDED_SHA256[name]
        print(f'{name}: local file used; {"identical to" if same else "DIFFERENT FROM"} the embedded copy')
if str(base) not in sys.path:
    sys.path.insert(0, str(base))

import pandas as pd
import matplotlib.pyplot as plt
import vpr4_historical as V
from vpr4_historical import ITEMS, BY_CODE, CHILDREN, THRESHOLD_ROWS, LEVEL_ORDER, evaluate, make_case, compare_cases

pd.set_option('display.max_colwidth', 90)
pd.set_option('display.width', 160)
SURF, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE = '#2a78d6', '#eb6834'
RAMP = ['#cde2fb', '#86b6ef', '#5598e7', '#256abf', '#104281']
plt.rcParams.update({'font.size': 9.5, 'axes.edgecolor': GRID, 'axes.facecolor': SURF, 'figure.facecolor': SURF,
                     'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.titleweight': 'bold', 'axes.grid': True, 'grid.color': GRID})
catalog = pd.read_csv(data_dir / 'vpr4_0_annex1_indicators.csv', dtype=str, keep_default_na=False)
catalog['w'] = catalog['weight'].astype(float)
print(V.STATUS)
''')

# ------------------------------------------------------------------------------------------------ 1. source
md(r'''
### 1 · Is the table right? Verifying the transcription against the thesis

Annex 1 (pp. 274–275) prints 63 rows: 39 numbered indicators (I1–I39), some with sub-items, and three rows with **no indicator number** (the gate questions of factors 2, 3 and 8). Each row has one value in the column headed "Odds ratio", which is the additive weight.

**What was checked, row by row.** Every row was typed by hand from the page images (`tools/annex1_transcription.py`). An automatic check then confirms that each Spanish label occurs in the PDF text of its page and that the sequence of 63 values read from the right-hand column of the PDF equals the transcription. Critical flags were checked against Table 1 (p. 193), cut-offs against p. 194, and the form structure against Annexes 2 and 5. Every claim and its status is listed in `SOURCE_VERIFICATION_MATRIX.csv`.

**Why the 77.019 total is not proof.** The weights add up to the thesis's stated maximum, but that only shows the *multiset* of numbers is right. A weight attached to the wrong row, a mislabelled row, or a wrong parent leaves the total unchanged:
''')

py('''
info = V.source_integrity()
print({k: info[k] for k in ['main_indicators', 'item_rows', 'factor_question_rows', 'positive_rows', 'zero_rows',
                            'critical_items', 'theoretical_ceiling', 'critical_weight_total']})

# A transposition error that the total cannot detect: swap the knife and firearm weights
swapped = catalog['w'].copy()
i_knife = catalog.index[catalog.code == 'I5_knife'][0]; i_fire = catalog.index[catalog.code == 'I5_firearm_use'][0]
swapped[i_knife], swapped[i_fire] = swapped[i_fire], swapped[i_knife]
print(f"\\nTotal with the correct table: {catalog['w'].sum():.3f}")
print(f"Total with knife and firearm weights swapped: {swapped.sum():.3f}  <- identical, yet every weapon example would change")
''')

md(r'''
**What the verification changed** (version 1 → version 2; details in `CHANGELOG.md`). The weights themselves were all correct. The structure was not:
''')

py('''
corrections = pd.DataFrame([
    ('10, 15, 38', 'Rows had been given the numbers I5, I7 and I17', 'The source prints no indicator number: they are the gate questions of factors 2, 3 and 8. Renamed F02_weapons_used, F03_threats, F08_criminal_record (old codes still accepted).'),
    ('38 → 39', 'Row 38 ("has a criminal and/or police record") was labelled I17', 'I17 is row 39, "previous breaches of measures". Row 38 is the factor-8 question.'),
    ('40, 41', 'I18 and I19 had no parent', 'Annex 5 p. 301: asked only "en caso afirmativo" to the record question. I18 alone now scores 2.142 + 1.870 = 4.012 (was 1.870).'),
    ('18, 20', 'Spanish labels truncated', 'Restored "... por parte del agresor".'),
    ('all', 'Invented thematic "sections"', 'Replaced by the source factors F01–F12 and the four categories of the form (Annex 2).'),
], columns=['Annex 1 row(s)', 'Version 1', 'Version 2 (verified)'])
corrections
''')

# ------------------------------------------------------------------------------------------------ 2. structure
md(r'''
### 2 · How the form is structured: additive, dependent, or mutually exclusive?

* **DOCUMENTED (p. 193).** The instrument is "de tipo actuarial con pesos aditivos ponderados": weights of the items answered *Sí* are added.
* **DOCUMENTED (Annex 5).** Sub-items are asked only "en caso afirmativo" (a child requires its parent). Weapon types (p. 294), threat types (p. 295), control types (p. 297) and life-problem types (p. 301) are checkboxes: "se pueden marcar varias opciones". Firearm *access* (I6) is assessed "independientemente de si empleó armas" (p. 295), so it is not a sub-item of weapon use. I17–I19 are asked only if the record question (F08) is *Sí* (p. 301).
* **DOCUMENTED (Annex 2).** Severity is a radio button *Leve / Grave / Muy grave*. Annex 1 has one row "grave o muy grave"; choosing *Leve* adds nothing.
* **INFERRED.** The only mutually exclusive choice on the screen (the severity radio) has a single weighted option, so **no two weighted rows exclude each other**. The full 77.019 is therefore attainable by a consistent form; the highest score observed in the construction sample was 68.062 (p. 194).
''')

py('''
types = (catalog.groupby('response_type')
         .agg(rows=('code', 'size'), weighted_rows=('w', lambda s: int((s > 0).sum())), points=('w', 'sum'))
         .reindex(['indicator', 'gate_question', 'severity_option', 'subtype_checkbox', 'sub_question']))
types['how it combines'] = ['added if Sí (I17-I19 only when F08 is Sí)',
                            'added if Sí; opens its sub-items',
                            'added if the radio is Grave or Muy grave (needs its parent)',
                            'added for each box ticked (needs its parent)',
                            'added if Sí (needs its parent)']
display(types.round(3))
parents = pd.DataFrame([(p, BY_CODE[p].weight, ', '.join(f'{c} ({BY_CODE[c].weight})' for c in kids))
                        for p, kids in CHILDREN.items()], columns=['parent row', 'parent weight', 'sub-items (weight)'])
display(parents)
full = evaluate(make_case(*BY_CODE))
print('Every row Sí, consistent with the structure:', full['score_exact'], full['category'])
''')

# ------------------------------------------------------------------------------------------------ 3. thresholds
md(r'''
### 3 · From score to level: where the designers drew the lines

**DOCUMENTED (p. 194).** "no apreciado, de 0 hasta 9.535; bajo, hasta 21.886; medio, hasta 34.715; alto, hasta 45.284; y extremo, a partir del punto anterior". The cut-offs were chosen with three criteria: a low share of **false negatives** at the first cut-off "aunque aumentase la tasa de falsos positivos"; levels from *medio* upwards should capture most of the cases considered most serious; and, "en menor grado", proportions per level that are "asumibles desde el punto de vista de la seguridad", meaning workable for police resources. The last criterion is an administrative one, written into a numerical threshold.

**ASSUMPTION.** The text does not say whether "hasta" includes the cut-off, and at 45.284 it overlaps ("alto, hasta 45.284" / "extremo, a partir del punto anterior"). We read "hasta" as ≤. **COMPUTED:** every cut-off can be hit *exactly* by a consistent form, so the reading changes the level of some forms:
''')

py('''
att = pd.DataFrame(V.threshold_attainability())
ex = pd.DataFrame(V.exact_cutoff_examples())
att['example form scoring exactly the cut-off'] = ex['codes'].apply(', '.join)
att['level if "hasta" is inclusive'] = ex['inclusive_reading']
att['level if exclusive'] = ex['exclusive_reading']
att[['cutoff', 'exactly_attainable', 'level if "hasta" is inclusive', 'level if exclusive', 'example form scoring exactly the cut-off']]
''')

# ------------------------------------------------------------------------------------------------ 4. firearm vs knife
md(r'''
### 4 · Firearm versus knife: what the numbers say, and what they do not

Both start from the weapon-use question F02 (1.533). The knife box adds 4.000 because "empleo de arma blanca" is one of the 13 **critical indicators**: chosen "con ponderación experta para un screening del riesgo de homicidio", with the consensus of three clinical and forensic experts, and doubled ("el peso final ... se obtuvo multiplicando por 2 su valor inicial", pp. 191–193). Firearm use is not on that list, and the thesis does not say why. The firearm box adds 0.

Where the empirical weights come from. **DOCUMENTED.** The Annex 1 weights are odds ratios for *reincidencia policial*, a new report against the same aggressor, within **four months** (p. 191), estimated on 60% of a cohort of 6,613 cases reported in autumn 2015 (n = 3,907). In the thesis's study of the predecessor form VPR2015 (Table 1, p. 163; criterion: a new report within six months), firearm use appeared in **30 of 6,613 cases** and its association was not significant (RR 1.408, 95% CI 0.479–4.134); knife use was significant (RR 1.845, p < .001). A rare item cannot reach significance in that design. The zero is therefore **a property of the sample and of the criterion** (a new police report within months, not lethality). It says nothing about how dangerous firearms are.
''')

py('''
rows = []
for label, codes in [('Firearm used', ['I5_firearm_use']), ('Knife used', ['I5_knife']),
                     ('Firearm and knife used', ['I5_firearm_use', 'I5_knife']), ('Access to firearms, no use', ['I6_firearm_access'])]:
    e = evaluate(make_case(*codes))
    rows.append((label, ' + '.join(f"{c['indicator']} {c['weight']:.3f}" for c in e['contributions']), e['score_exact'], e['category']))
pd.DataFrame(rows, columns=['fictitious form (every other row No)', 'contributions', 'score', 'historical level'])
''')

# ------------------------------------------------------------------------------------------------ 5. zero weights
md(r'''
### 5 · Thirty-one rows that are recorded but weigh nothing

**DOCUMENTED (p. 196).** Only indicators with empirical weight contribute to the scale; "el resto se van a mantener durante un periodo estimado de unos 18 meses con la finalidad de obtener más información sobre ellos". A weight of zero is a **design decision about what counts** for the score. It does not mean that the circumstance is harmless, and the officer still records it.

Almost all of the victim-vulnerability block (category 3) is in that position: disability, pregnancy, serious illness, being foreign, lack of support, dependent children, economic dependence.
''')

py('''
z = catalog.assign(weighted=catalog.w > 0).groupby(['category', 'category_es'])['weighted'].agg(rows='size', weighted='sum')
z['zero_weight'] = z['rows'] - z['weighted']
display(z)
e = evaluate(make_case('I24_disability', 'I25_pregnancy', 'I26_serious_illness', 'I28_social_support', 'I33_economic_dependence', 'I34_dependents'))
print('Six vulnerability facts answered Sí ->', e['score_exact'], e['category'], '| zero-weight rows Sí:', len(e['zero_weight_positive']))
''')

# ------------------------------------------------------------------------------------------------ 6. many indicators, low score
md(r'''
### 6 · Can a form record many indicators and still score "no apreciado"?

The thesis says a level can be reached "mediante la suma de muchos indicadores con peso bajo y, también con la suma de menos indicadores de mayor peso" (p. 192). **COMPUTED:** we enumerated exactly (by dynamic programming over the form's groups, respecting every parent–child rule) the fewest and the most indicators a consistent form can hold in each level. "Facts" adds the three weighted gate questions (F02, F03, F08), which have no I-number.

This establishes what is **logically possible under the rule**. It does not say such forms occurred, and it says nothing about the danger in any real situation.
''')

py('''
ext = pd.DataFrame(V.category_extremes())[['level', 'min_indicators', 'max_indicators', 'min_facts', 'max_facts', 'attainable_scores']]
display(ext)
fig, ax = plt.subplots(figsize=(8.5, 3.2))
for i, r in ext.iterrows():
    ax.plot([r.min_indicators, r.max_indicators], [i, i], color=BLUE, lw=6, solid_capstyle='round')
    ax.text(r.min_indicators - 0.7, i, str(r.min_indicators), ha='right', va='center', fontsize=8.5)
    ax.text(r.max_indicators + 0.7, i, str(r.max_indicators), ha='left', va='center', fontsize=8.5)
ax.set_yticks(range(len(ext))); ax.set_yticklabels(ext.level); ax.grid(axis='y', visible=False)
ax.set_xlim(-3, 43); ax.set_xlabel('Indicators (I1-I39) answered Sí')
ax.set_title('Fewest to most indicators a consistent form can hold in each historical level')
plt.tight_layout(); plt.show()
''')

py('''
most = V.indicator_count_example('No appreciable risk', most=True)
print(f"MOST indicators while 'No apreciado': {most['indicators']} indicators ({most['facts']} facts), score {most['evaluation']['score_exact']}")
display(pd.DataFrame(most['evaluation']['contributions'])[['indicator', 'label', 'weight']])
few = V.indicator_count_example('Extreme', most=False)
print(f"FEWEST indicators for 'Extremo': {few['indicators']} indicators ({few['facts']} facts), score {few['evaluation']['score_exact']}")
print(', '.join(few['codes']))
''')

md(r'''
Read the first table carefully: physical violence, sexual violence, an object used as a weapon, threats against the children, dependent children, pregnancy. All of these sit inside "no apreciado" **because** the physical and sexual violence were recorded as *leve* (the severity rows were not ticked) and because most of the other rows weigh zero. This is where input discretion (section 8) and design discretion meet: the same account recorded with one severity box ticked differently changes the level.
''')

# ------------------------------------------------------------------------------------------------ 7. unknowns
md(r'''
### 7 · "No se sabe": what the thesis does not tell us

**DOCUMENTED.** The screen offers *Sí / No / No se sabe* for most items (Annex 2). In the statistical analysis, "no se sabe" was treated as missing (p. 161). **NOT DOCUMENTED:** how the operational software scored an unknown answer.

**ASSUMPTION (conservative).** The engine never turns an unknown into *No*. Because every weight is ≥ 0, whatever rule the software used, the score lies between the score with every unknown counted as *No* and the score with every unknown counted as *Sí* (respecting the parent–child rules). A level is reported only if both ends agree.
''')

py('''
for base_rows, unknown in [(['I11_stalking', 'I36_recent_separation'], ['I9_jealousy']),
                           (['I11_stalking', 'I36_recent_separation'], ['I39_victim_fear_lethal', 'I9_jealousy']),
                           (['I5_knife'], ['I10_control_cyber'])]:
    e = evaluate(make_case(*base_rows, unknown=unknown))
    print(f"Sí: {base_rows}; unknown: {unknown}\\n   score {e['score_min']:.3f} to {e['score_max']:.3f}; "
          f"level {e['category_at_min']} to {e['category_at_max']} -> "
          f"{'determined' if e['category_robust_to_unknowns'] else 'UNDETERMINED'}")
''')

# ------------------------------------------------------------------------------------------------ 8. discretion
md(r'''
### 8 · Where discretion sits: four layers

| Layer | Who decides | What they decide | Source | Status |
|---|---|---|---|---|
| **Input** | the officer | whether a fact is recorded, how it is classified (insults as psychological violence?), the severity (*leve* or *grave*), what counts as "No se sabe" | Annex 5: "En caso de duda entre dos niveles, se recomienda indicar el nivel más grave" (pp. 292–296); raise severity if children were present (pp. 292, 296); reciprocal violence (I37) "en ningún caso podrá preguntarse ... será labor del agente inferir" (p. 306) | DOCUMENTED |
| **Design: weights** | the designers | which facts count, by how much; 13 critical weights set by expert judgement and doubled; mental disorder fixed at 3; 31 rows kept at 0 | pp. 192–193, 196 | DOCUMENTED |
| **Design: cut-offs** | the designers | where the levels begin; false negatives traded against false positives and police workload | p. 194 | DOCUMENTED |
| **Procedure** | the officer, under the Secretary of State's instruction | raise the automatic level, never lower it; switch a "no apreciado" case to inactive; inform the victim at *medio* and above | Instrucción 7/2016, rules 1.5, 1.6, 1.8 (thesis Annex 6, pp. 327–328) | DOCUMENTED |

The demonstration below follows **one fictitious account** (stalking after a recent separation, with insults and a push) through defensible choices at each layer.
''')

py('''
story = ['I11_stalking', 'I36_recent_separation']
versions = [
    ('A. Insults not recorded; push recorded as leve', story + ['I2_physical']),
    ('B. Insults recorded as psychological violence (I1); push leve', story + ['I2_physical', 'I1_psychological']),
    ('C. Insults not recorded; push recorded as grave ("en caso de duda ... más grave")', story + ['I2_physical_severe']),
]
rows = []
for label, codes in versions:
    e = evaluate(make_case(*codes))
    rows.append(dict(coding=label, score=e['score_exact'], automatic_level=e['category'],
                     consequence=V.procedural_consequences(e['category'])[0]))
display(pd.DataFrame(rows))
ov = V.apply_officer_override('Low', 'Medium')
print('Procedure layer: the officer may raise Low ->', ov['final'], '|', ov['rule'])
print('   ', V.procedural_consequences('Medium')[1])
try:
    V.apply_officer_override('Low', 'No appreciable risk')
except ValueError as err:
    print('Lowering is not provided for:', err)
''')

md(r'''
**A design-layer counterfactual (COMPUTED, with a caveat).** Critical weights are the expert value multiplied by 2 (p. 192). If that doubling is removed and the cut-offs are held fixed, the stalking + separation + victim-fear form changes level. The caveat matters: the cut-offs were set on the distribution of the weighted scores, so the designers would also have moved the cut-offs. The point is not the alternative number but that a single design decision is enough to move a form across a line that has procedural consequences.
''')

py('''
from decimal import Decimal
def score_without_doubling(codes):
    case, _ = V.normalize(make_case(*codes))
    total = Decimal('0')
    for code, yes in case.items():
        if yes:
            it = BY_CODE[code]
            total += it.weight if (not it.critical or code == 'I20_mental_disorder') else it.weight / 2
    return total
codes = ['I11_stalking', 'I36_recent_separation', 'I39_victim_fear_lethal']
s1, s0 = Decimal(evaluate(make_case(*codes))['score_exact']), score_without_doubling(codes)
print(f'As published (critical weights doubled): {s1} -> {V.category(s1)}')
print(f'Critical weights not doubled, same cut-offs: {s0} -> {V.category(s0)}')
''')

py('''
fig, ax = plt.subplots(figsize=(9, 2.8))
ax.axvspan(0, 9.535, color='#efeeea', lw=0); ax.axvspan(9.535, 16, color=RAMP[0], lw=0)
ax.axvline(9.535, color=INK, lw=1, ls=(0, (3, 2)))
ax.text(4.77, 2.65, 'No apreciado (case may be inactivated)', ha='center', fontsize=8.5, color=INK)
ax.text(12.77, 2.65, 'Bajo (case stays active)', ha='center', fontsize=8.5, color=INK)
short = ['A · insults not recorded, push leve', 'B · insults recorded as I1, push leve', 'C · insults not recorded, push grave']
for k, (label, codes) in enumerate(versions):
    x = float(evaluate(make_case(*codes))['score_exact'])
    ax.plot([x], [2 - k], 'o', color=BLUE, ms=9, mec=SURF, mew=2)
    ax.text(x + 0.3, 2 - k, f'{x:.3f}', va='center', fontsize=8.5)
ax.set_yticks([2, 1, 0]); ax.set_yticklabels(short); ax.grid(False)
ax.set_xlim(0, 16); ax.set_ylim(-0.6, 3.0)
ax.set_xlabel('Historical additive score (zoomed to 0-16 of 77.019); dashed line = first cut-off 9.535')
ax.set_title('One fictitious account, three defensible codings, two procedural outcomes')
plt.tight_layout(); plt.show()
''')

# ------------------------------------------------------------------------------------------------ 9. bridge
md(r'''
### 9 · Bridge to VioGén 2, without overclaiming

What this module can support is a **comparison of rule structures**, not of numbers:

* The **upward-only override** documented for 2016 (rule 1.5) is still the pattern in Instrucción 1/2025, §§ 3.8 and 6.2, as read in Module 1. The *direction* of officer discretion over the automatic level has not changed.
* The **"no apreciado" level**, and with it the discretionary inactivation of rule 1.6, was removed with VioGén 2 (in force 30 June 2025). Module 1 shows those cases absorbed into *bajo*.
* The **weights, items and cut-offs** of VPR5.0-H (2019) and of VioGén 2 are not public. Nothing in sections 3–8 may be used to explain, estimate or reproduce a 2025–2026 classification, a Module 1 trend, or any police decision.

The historical model is useful because it is the only version whose arithmetic is public. It shows **the kinds of choices** an actuarial police form requires (what counts, how much, where the lines go, who may move a case across them). It does not show which choices are made today.
''')

# ------------------------------------------------------------------------------------------------ 10. widget
md(r'''
### 10 · Optional: build your own fictitious form

Requires `ipywidgets` (preinstalled in Colab). Rows ticked under *Sí* are added (their parent question is set to *Sí*); rows under *No se sabe* stay unknown; every other row is *No*. The full app with tri-state answers per row is `interactive_app.py` (Streamlit).
''')

py('''
try:
    import ipywidgets as widgets
    from IPython.display import clear_output
    options = [(f"{it.indicator or it.factor} · {it.english} [{it.weight}]", it.code) for it in ITEMS]
    yes_box = widgets.SelectMultiple(options=options, rows=12, description='Sí', layout=widgets.Layout(width='95%'))
    unk_box = widgets.SelectMultiple(options=options, rows=6, description='No se sabe', layout=widgets.Layout(width='95%'))
    out = widgets.Output()
    def update(*_):
        with out:
            clear_output(wait=True)
            try:
                e = evaluate(make_case(*yes_box.value, unknown=[c for c in unk_box.value if c not in yes_box.value]))
            except ValueError as err:
                print('Inconsistent form:', err); return
            if e['complete']:
                print(f"Score {e['score_exact']} / 77.019 -> {e['category']} ({e['category_es']}). Historical VPR4.0, not VioGén 2.")
            else:
                print(f"Score between {e['score_min']:.3f} and {e['score_max']:.3f}: level {e['category_at_min']} to {e['category_at_max']}.")
            print('Who decided? Input: which rows you ticked. Design: their weights and the cut-offs. Procedure: what follows.')
    yes_box.observe(update, names='value'); unk_box.observe(update, names='value')
    display(widgets.VBox([yes_box, unk_box, out])); update()
except ImportError:
    print('ipywidgets is not installed: pip install ipywidgets, or run: streamlit run interactive_app.py')
''')

# ------------------------------------------------------------------------------------------------ 11. conclusions
md(r'''
### 11 · What we can and cannot conclude

**Supported by the source and the computation**
1. VPR4.0 was an additive actuarial form: 63 rows, 32 with weight, total 77.019, five levels cut at 9.535 / 21.886 / 34.715 / 45.284 (pp. 192–194, 274–275).
2. Much of what is decisive was set by **designers**: 13 expert weights doubled, 31 recorded rows at zero, cut-offs chosen partly for police workload.
3. **Officers** shape the input: severity choices, classification of insults, inferred items, unknowns. One severity box can move a form across the first cut-off.
4. The **procedure** fixed the direction of officer discretion over the automatic level (upwards only) and made "no apreciado" the only level at which officers could inactivate a case at their discretion (rule 1.6).
5. Under the documented rule, a form can hold 25 of 39 indicators and score "no apreciado", and 9 indicators can be enough for "extremo".

**Not supported**
* That these numbers are VioGén 2, VPR5.0-H, or the deployed software (unknown handling, boundary rule, later re-weighting).
* Anything about predictive accuracy, about fairness, or about the danger in any real situation. The weights are odds ratios for a **new police report within four months** in a 2015–2016 cohort (p. 191).
* Any explanation of Module 1's 2018–2026 series or of a police decision.

**Discussion questions**
1. Who is accountable when the first cut-off was set to limit false negatives *and* to keep caseloads "asumibles"?
2. Rule 1.5 lets officers raise but never lower the level. Does that constrain discretion, or move it to the input layer?
3. Should a recorded fact that weighs zero be shown to the officer, the victim or the judge as part of the result?
''')

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
               'language_info': {'name': 'python'}}
out = P / 'VioGen_Module2_Historical_Research_Lab.ipynb'
nbf.write(nb, out)
print('cells:', len(cells), '| code cells:', sum(c.cell_type == 'code' for c in cells), '|', out.name)
