"""Figures for Module 3 (documentary; no case data). Run: python make_figures.py"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from annex_measures import MEASURES  # noqa: E402
from decision_rules import Scenario, first_vper, later_vper, ordinary_inactivation, protection_floor  # noqa: E402

OUT = ROOT.parents[1] / 'figures' / '03_institutional_rules'
OUT.mkdir(exist_ok=True)
SURF, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
CAT = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6']
RAMP = ['#cde2fb', '#86b6ef', '#5598e7', '#256abf', '#104281']
matplotlib.rcdefaults()   # ignore any local matplotlibrc so figures render the same everywhere
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': GRID, 'axes.facecolor': SURF,
                     'figure.facecolor': SURF, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.titleweight': 'bold', 'axes.titlesize': 11,
                     'axes.titlecolor': INK})
NOTE = ('Sources: Instrucción 4/2019 (official PDF) and Instrucción 1/2025 (signed copy, CSV GEN-61b6…); intervening '
        'instructions as graded in data/03_institutional_rules/intervening_instructions.csv. Formal rules only, not police practice.')


def save(fig, name, note=NOTE):
    wrapped = textwrap.fill(note, width=int(fig.get_figwidth() * 17))
    fig.text(0.01, 0.01, wrapped, fontsize=7, color=INK2, va='bottom')
    fig.tight_layout(rect=(0, 0.03 + 0.11 * (wrapped.count('\n') + 1) / fig.get_figheight(), 1, 1))
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ 1 chronology
COLS = ['7/2016', '4/2019', '5/2021', '8/2021', '11/2022', '1/2023', '2/2024', '1/2025']
GRADE_STYLE = {'A': dict(marker='o', ms=9, mfc=RAMP[4], mec=RAMP[4]), 'B': dict(marker='o', ms=9, mfc=RAMP[2], mec=RAMP[2]),
               'C': dict(marker='o', ms=9, mfc=SURF, mec=RAMP[3], mew=1.6)}
EVENTS = [  # (row label, [(column, grade, label)])
    ('Officer may raise the level (upward only)', [('7/2016', 'A', ''), ('4/2019', 'A', ''), ('1/2025', 'A', '')]),
    ('Assessment without a complaint', [('4/2019', 'A', 'ex officio'), ('5/2021', 'A', 'Protocolo Cero'), ('1/2025', 'A', '')]),
    ('Personal Safety Plan', [('7/2016', 'A', 'created'), ('4/2019', 'A', ''), ('1/2025', 'A', 'agreed with victim')]),
    ('Persistent aggressors', [('8/2021', 'C', 'measures'), ('1/2023', 'B', 'tell victim'), ('1/2025', 'A', 'consolidated')]),
    ('Resistant cases', [('4/2019', 'A', 'inform court'), ('11/2022', 'B', 'updated'), ('1/2025', 'A', 'oficio + inactivation')]),
    ('Supervised cases', [('2/2024', 'B', 'created'), ('1/2025', 'A', 'shorter periods')]),
    ('Inactivation: victim not located', [('4/2019', 'A', '1 month'), ('2/2024', 'C', '6 months'), ('1/2025', 'A', '3 months')]),
    ('Inactivation on renunciation', [('4/2019', 'A', 'any level'), ('2/2024', 'C', 'up to medio'), ('1/2025', 'A', 'bajo/medio')]),
    ('Bajo inactivation: contact in person', [('4/2019', 'A', 'contact'), ('2/2024', 'B', 'in person'), ('1/2025', 'A', '"preferentemente"')]),
    ('"No apreciado" level', [('7/2016', 'A', ''), ('4/2019', 'A', ''), ('2/2024', 'C', 'still used'), ('1/2025', 'A', 'removed')]),
    ('New incident: assessment form', [('4/2019', 'A', 'VPER-C'), ('2/2024', 'C', 'VPER-C'), ('1/2025', 'A', 'VPR')]),
    ('First VPER, medio+: maximum', [('4/2019', 'A', '7 days'), ('1/2025', 'A', '15 days')]),
    ('VPER sent to court when level…', [('4/2019', 'A', 'varies'), ('1/2025', 'A', 'rises')]),
    ('Consolidated VPR: time limit', [('4/2019', 'A', 'none'), ('1/2025', 'A', '72 hours')]),
]
fig, ax = plt.subplots(figsize=(11.5, 6.6))
for i, (label, evs) in enumerate(EVENTS):
    y = len(EVENTS) - 1 - i
    xs = [COLS.index(c) for c, _, _ in evs]
    ax.plot([min(xs), max(xs)], [y, y], color=GRID, lw=2, zorder=1)
    for c, g, t in evs:
        x = COLS.index(c)
        ax.plot([x], [y], zorder=3, **GRADE_STYLE[g])
        if t:
            ax.text(x, y + 0.3, t, ha='center', va='bottom', fontsize=7.2, color=INK)
ax.set_yticks(range(len(EVENTS)))
ax.set_yticklabels([e[0] for e in EVENTS][::-1])
ax.set_xticks(range(len(COLS)))
ax.set_xticklabels([f'Instr.\n{c}' for c in COLS])
ax.set_xlim(-0.6, len(COLS) - 0.4)
ax.set_ylim(-0.7, len(EVENTS) - 0.1)
ax.grid(axis='x', color=GRID, lw=0.8)
ax.tick_params(axis='y', length=0)
for g, lab in (('A', 'primary text read'), ('B', 'official government summary'), ('C', 'secondary source (press / police academy)')):
    ax.plot([], [], ls='none', label=lab, **GRADE_STYLE[g])
ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=8.5)
ax.set_title('Not every 2019→2025 difference was introduced in 2025', pad=28)
save(fig, '01_change_chronology.png')

# ------------------------------------------------------------------------------------------------ 2 authority map
ACTORS = ['System /\ndesigners', 'Recording\nofficer', 'Specialised\npolice unit', 'Police\nmanagement', 'Court', 'Prosecutor', 'Victim']
MOD = {'automated': ('automated', CAT[6]), 'mandatory': ('must', CAT[0]), 'conditional': ('must, if…', RAMP[1]),
       'permitted': ('may', CAT[1]), 'bounded': ('may, within criteria', '#f6b89c'), 'decides': ('decides', CAT[2]),
       'informed': ('is informed', '#dddcd7'), 'contacted': ('is contacted', '#dddcd7')}
DARK_TEXT = {RAMP[1], '#f6b89c', '#dddcd7'}
MAP = [  # stage, {actor_index: (modality, short text)}
    ('Record indicators (VPR)', {1: ('mandatory', 'fills form; few "No se sabe"'), 6: ('informed', 'a source; never fills')}),
    ('Automatic level', {0: ('automated', '4 levels; fixed cut-offs'), 1: ('permitted', 'raise only')}),
    ('Report to court', {0: ('automated', 'report + diligencias'), 4: ('informed', 'Si/No/NS'), 5: ('informed', '')}),
    ('Judicial measures', {4: ('decides', 'order / measures'), 2: ('mandatory', 'enforce; notify both')}),
    ('Protection floor (Annex II)', {2: ('mandatory', 'level measures'), 1: ('permitted', 'add others'), 3: ('conditional', 'resources if exceeded')}),
    ('Electronic device', {2: ('conditional', 'asks: Alto+, Medio-ER'), 5: ('decides', 'whether to ask court'), 4: ('decides', 'imposes')}),
    ('First / later VPER', {2: ('conditional', 'deadlines by level & measures')}),
    ('Court notice of VPER', {2: ('conditional', 'only if level rises'), 4: ('informed', '')}),
    ('Ordinary inactivation', {2: ('bounded', 'Bajo; positive finding'), 6: ('contacted', 'at least once')}),
    ('Supervised cases', {0: ('automated', 'criteria flags'), 2: ('bounded', 'extensions; exit at Bajo')}),
    ('Exceptional inactivation', {2: ('conditional', '"se procederá"'), 4: ('informed', 'oficio'), 5: ('informed', 'oficio')}),
    ('Record measures taken', {2: ('permitted', '"recomendable"')}),
]
fig, ax = plt.subplots(figsize=(12, 7.4))
for i, (stage, cells) in enumerate(MAP):
    y = len(MAP) - 1 - i
    for a in range(len(ACTORS)):
        ax.add_patch(Rectangle((a, y), 0.96, 0.92, fc=SURF, ec=GRID, lw=0.6))
    for a, (m, txt) in cells.items():
        lab, col = MOD[m]
        ax.add_patch(Rectangle((a, y), 0.96, 0.92, fc=col, ec=SURF, lw=1.5, alpha=0.9))
        tc = INK if col in DARK_TEXT else 'white'
        ax.text(a + 0.48, y + 0.66, lab, ha='center', va='center', fontsize=7.6, fontweight='bold', color=tc)
        ax.text(a + 0.48, y + 0.3, textwrap.fill(txt, 24), ha='center', va='center', fontsize=6.4, color=tc)
ax.set_xlim(0, len(ACTORS)); ax.set_ylim(0, len(MAP))
ax.set_xticks([a + 0.48 for a in range(len(ACTORS))]); ax.set_xticklabels(ACTORS)
ax.xaxis.tick_top()
ax.set_yticks([len(MAP) - 1 - i + 0.46 for i in range(len(MAP))]); ax.set_yticklabels([m[0] for m in MAP])
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.set_title('Who decides what under Instrucción 1/2025 (formal rules)', pad=34)
save(fig, '02_decision_authority_map_2025.png',
     NOTE + ' ER = special relevance. See data/03_institutional_rules/decision_authority_rules.csv for the clause behind each cell.')

# ------------------------------------------------------------------------------------------------ 3 low-risk restructuring
COLS3 = [('2019\nno apreciado', Scenario(2019, 'no_appreciable', judicial_measures=False)),
         ('2025\nBajo, no measures', Scenario(2025, 'low', judicial_measures=False)),
         ('2019\nbajo', Scenario(2019, 'low', judicial_measures=False)),
         ('2025\nBajo, with measures', Scenario(2025, 'low', judicial_measures=True))]


def fv(s):
    r = first_vper(Scenario(**{**s.__dict__, 'first_vper_done': False}))
    return f"≤ {r['max_days']} days" if r['max_days'] else 'no deadline stated'


def lv(s):
    r = later_vper(Scenario(**{**s.__dict__, 'first_vper_done': True}))
    return f"< {r['value']} days"


def oi(s):
    if s.judicial_measures:
        return 'not available\n(measures in force)'
    return {2019: {'no_appreciable': '"con carácter general"', 'low': '"excepcionalmente"'}}.get(s.version, {}).get(s.algorithm_category, 'available, positive\nfinding required')


def ag(s):
    ids = protection_floor(s.version, s.algorithm_category, s.judicial_measures)['measure_ids']
    return 'yes' if ('A1-2019-09' in ids or 'A2-2025-15' in ids) else 'no'


ROWS3 = [('First VPER', fv), ('Later VPER', lv), ('Ordinary inactivation', oi), ('Aggressor told case\nis under police control', ag),
         ('Written measures\n(Annex items)', lambda s: str(protection_floor(s.version, s.algorithm_category, s.judicial_measures)['n_items']))]
fig, ax = plt.subplots(figsize=(10.5, 4.6))
tint = ['#eef4fc', '#eef4fc', '#fdf0ea', '#fdf0ea']
for j, (head, s) in enumerate(COLS3):
    ax.add_patch(Rectangle((j, len(ROWS3)), 0.97, 0.9, fc=CAT[0] if j < 2 else CAT[1], ec=SURF))
    ax.text(j + 0.485, len(ROWS3) + 0.45, head, ha='center', va='center', color='white', fontweight='bold', fontsize=8.6)
    for i, (lab, fn) in enumerate(ROWS3):
        y = len(ROWS3) - 1 - i
        ax.add_patch(Rectangle((j, y), 0.97, 0.9, fc=tint[j], ec=SURF))
        ax.text(j + 0.485, y + 0.45, fn(s), ha='center', va='center', fontsize=8.3, color=INK)
ax.set_xlim(-0.02, 4); ax.set_ylim(0, len(ROWS3) + 1)
ax.set_xticks([]); ax.set_yticks([len(ROWS3) - 1 - i + 0.45 for i in range(len(ROWS3))]); ax.set_yticklabels([r[0] for r in ROWS3])
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
ax.set_title('Procedurally, "Bajo without judicial measures" inherits most of the 2019 "no apreciado" treatment', pad=10)
save(fig, '03_low_risk_restructuring.png',
     NOTE + ' Blue pair and orange pair share deadlines and intervals; 2025 adds stricter inactivation premises and a larger written floor. Category labels only: individual cases cannot be mapped across the recalibrated algorithm.')

# ------------------------------------------------------------------------------------------------ 4 annex modalities
MODS = [('mandatory', 'Bare instruction'), ('conditional_fact', 'Applies if a stated fact holds'),
        ('conditional_judgement', 'Applies if the officer judges it relevant'), ('advice_to_victim', 'Advice the victim may follow'),
        ('request_other_authority', 'Request to another authority'), ('resource_contingent', 'Depends on available means'),
        ('discretionary_option', 'Police may do it')]
cnt = {y: [sum(1 for m in MEASURES if m['year'] == y and m['modality'] == k) for k, _ in MODS] for y in (2019, 2025)}
fig, ax = plt.subplots(figsize=(9.5, 4.6))
ys = list(range(len(MODS)))[::-1]
h = 0.36
ax.barh([y + h / 2 for y in ys], cnt[2019], height=h, color=CAT[0], label='2019 Anexo 1 (26 items)', edgecolor=SURF)
ax.barh([y - h / 2 for y in ys], cnt[2025], height=h, color=CAT[1], label='2025 Anexo II (41 items)', edgecolor=SURF)
for y, a, b in zip(ys, cnt[2019], cnt[2025]):
    ax.text(a + 0.2, y + h / 2, str(a), va='center', fontsize=8, color=INK)
    ax.text(b + 0.2, y - h / 2, str(b), va='center', fontsize=8, color=INK)
ax.set_yticks(ys); ax.set_yticklabels([lab for _, lab in MODS])
ax.set_xlabel('Annex items (complete transcription, all levels)')
ax.grid(axis='x', color=GRID); ax.grid(axis='y', visible=False)
ax.legend(frameon=False, loc='lower right')
ax.set_title('How the annex items oblige: 2025 adds a children block, digital-safety advice\nand items conditional on judicial measures')
save(fig, '04_annex_measure_modalities.png', NOTE + ' Classification by the wording of each item (scripts/03_institutional_rules/src/annex_measures.py).')
print('figures:', sorted(p.name for p in OUT.glob('*.png')))
