"""Figures from the verified historical VPR4.0 table (not empirical cases). Run: python generate_figures.py"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

from vpr4_historical import (EMPIRICAL_MAX, ITEMS, THEORETICAL_MAX, THRESHOLD_ROWS, category_extremes,  # noqa: E402
                             evaluate, make_case)

OUT = Path(__file__).resolve().parents[2] / 'figures' / '02_historical_scoring'
OUT.mkdir(exist_ok=True)
SURF, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
BLUE, ORANGE = '#2a78d6', '#eb6834'
RAMP = ['#cde2fb', '#86b6ef', '#5598e7', '#256abf', '#104281']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.edgecolor': GRID, 'axes.facecolor': SURF,
                     'figure.facecolor': SURF, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.titleweight': 'bold',
                     'axes.titlesize': 11.5, 'axes.titlecolor': INK, 'axes.grid': True, 'grid.color': GRID})
NOTE = 'Source: López Ossorio (2016), UAM doctoral thesis, Annex 1 pp. 274-275; cut-offs p. 194. Historical VPR4.0, not VioGén 2.'


def save(fig, name, note=NOTE):
    import textwrap
    wrapped = textwrap.fill(note, width=int(fig.get_figwidth() * 17))
    lines = wrapped.count('\n') + 1
    fig.text(0.01, 0.01, wrapped, fontsize=7.5, color=INK2, va='bottom')
    fig.tight_layout(rect=(0, 0.03 + 0.11 * lines / fig.get_figheight(), 1, 1))
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)


# 1 ---- every positive weight, critical indicators marked
pos = sorted([it for it in ITEMS if it.weight > 0], key=lambda x: x.weight)
fig, ax = plt.subplots(figsize=(10, 8.5))
ax.barh(range(len(pos)), [float(x.weight) for x in pos], color=[ORANGE if x.critical else BLUE for x in pos],
        edgecolor=SURF, height=0.75)
ax.set_yticks(range(len(pos)))
def short(t, n=58):
    t = t.split(' (factor')[0]
    return t if len(t) <= n else t[:n - 1].rstrip() + '…'
ax.set_yticklabels([f'{x.indicator or x.factor} · {short(x.english)}' for x in pos], fontsize=8)
for i, x in enumerate(pos):
    ax.text(float(x.weight) + 0.04, i, f'{x.weight:.3f}', va='center', fontsize=7.5, color=INK)
ax.grid(axis='y', visible=False)
ax.set_xlabel('Historical additive weight (Annex 1 "Odds ratio" column; not a probability)')
ax.set_title('VPR4.0 (2016): the 32 rows that carry weight', pad=24)
ax.bar([0], [0], color=ORANGE, label='critical indicator: weight set by experts (Table 1, p. 193)')
ax.bar([0], [0], color=BLUE, label='other indicator or factor question')
ax.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8.5)
save(fig, '01_published_weights.png')

# 2 ---- cut-offs on the theoretical scale
fig, ax = plt.subplots(figsize=(10, 2.9))
bounds = [0.0] + [float(u) for _, u in THRESHOLD_ROWS[:-1]] + [float(THEORETICAL_MAX)]
for i, (label, _) in enumerate(THRESHOLD_ROWS):
    ax.barh([0], [bounds[i + 1] - bounds[i]], left=bounds[i], color=RAMP[i], edgecolor=SURF, height=0.5)
    ax.text((bounds[i] + bounds[i + 1]) / 2, 0, label, ha='center', va='center', fontsize=8.5,
            color='white' if i >= 3 else INK)
for b in bounds[1:-1]:
    ax.text(b, 0.33, f'{b:.3f}', ha='center', fontsize=8, color=INK2)
ax.axvline(float(EMPIRICAL_MAX), color=INK, lw=1, ls=(0, (3, 2)))
ax.text(float(EMPIRICAL_MAX) - 0.8, -0.45, 'highest score observed\nin the data (68.062)', ha='right', va='center', fontsize=7.5, color=INK)
ax.set_xlim(0, 77.019); ax.set_ylim(-0.9, 0.6); ax.set_yticks([]); ax.grid(False)
ax.set_xlabel('Additive score (theoretical scale 0-77.019; cut-offs set on the empirical scale, p. 194)')
ax.set_title('Where the designers drew the lines: four cut-offs, five levels')
save(fig, '02_historical_cutoffs.png')

# 3 ---- controlled contrasts
cases = [('Firearm used (F02 + firearm)', ['I5_firearm_use']), ('Knife used (F02 + knife)', ['I5_knife']),
         ('Access to firearms only (I6)', ['I6_firearm_access']), ('Stalking only (I11)', ['I11_stalking']),
         ('Stalking + separation', ['I11_stalking', 'I36_recent_separation']),
         ('+ insults recorded as psychological violence', ['I11_stalking', 'I36_recent_separation', 'I1_psychological']),
         ('+ victim fears lethal violence (I39)', ['I11_stalking', 'I36_recent_separation', 'I39_victim_fear_lethal'])]
vals = [evaluate(make_case(*c))['score'] for _, c in cases]
fig, ax = plt.subplots(figsize=(10, 4.3))
y = list(range(len(cases)))[::-1]
ax.barh(y, vals, color=[BLUE if v <= 9.535 else RAMP[3] for v in vals], edgecolor=SURF, height=0.6)
for yy, v in zip(y, vals):
    ax.text(v + 0.12, yy, f'{v:.3f}', va='center', fontsize=8.5, color=INK)
ax.set_yticks(y); ax.set_yticklabels([n for n, _ in cases]); ax.grid(axis='y', visible=False)
ax.axvline(9.535, color=INK, lw=1, ls=(0, (3, 2)))
ax.text(9.6, len(cases) - 0.6, 'cut-off 9.535: "No apreciado" ends', fontsize=8, color=INK)
ax.set_xlim(0, 13.5); ax.set_xlabel('Historical additive score (every other row answered No)')
ax.set_title('Fictitious, fully specified forms: what moves the score, and what does not')
save(fig, '03_selected_indicator_contrasts.png', NOTE + ' Not statements about real danger.')

# 4 ---- weighted versus zero-weight rows, by category of the form
cats = {1: 'Violence history', 2: 'Aggressor', 3: 'Victim vulnerability\nand relationship', 4: 'Victim perception'}
posn = [sum(1 for it in ITEMS if it.category == c and it.weight > 0) for c in cats]
zero = [sum(1 for it in ITEMS if it.category == c and it.weight == 0) for c in cats]
fig, ax = plt.subplots(figsize=(9, 4.2))
x = range(len(cats))
ax.bar([i - 0.2 for i in x], posn, width=0.38, color=BLUE, label='positive weight', edgecolor=SURF)
ax.bar([i + 0.2 for i in x], zero, width=0.38, color=RAMP[1], label='zero weight', edgecolor=SURF)
for i in x:
    ax.text(i - 0.2, posn[i] + 0.3, str(posn[i]), ha='center', fontsize=8.5)
    ax.text(i + 0.2, zero[i] + 0.3, str(zero[i]), ha='center', fontsize=8.5)
ax.set_xticks(list(x)); ax.set_xticklabels(list(cats.values())); ax.grid(axis='x', visible=False)
ax.set_ylabel('Annex 1 rows'); ax.legend(frameon=False)
ax.set_title('Victim-vulnerability rows are recorded but carry no weight in the 2016 score')
save(fig, '04_scored_vs_zero_entries.png', NOTE + ' Zero-weight rows were kept to gather information (p. 196).')

# 5 ---- two routes to a level (p. 192), exact over every consistent form
ext = category_extremes()
fig, ax = plt.subplots(figsize=(9.5, 3.8))
for i, r in enumerate(ext):
    ax.plot([r['min_indicators'], r['max_indicators']], [i, i], color=BLUE, lw=6, solid_capstyle='round')
    ax.text(r['min_indicators'] - 0.6, i, str(r['min_indicators']), ha='right', va='center', fontsize=8.5)
    ax.text(r['max_indicators'] + 0.6, i, str(r['max_indicators']), ha='left', va='center', fontsize=8.5)
ax.set_yticks(range(len(ext))); ax.set_yticklabels([r['level'] for r in ext]); ax.grid(axis='y', visible=False)
ax.set_xlim(-3, 43); ax.set_xlabel('Number of indicators (I1-I39) answered Sí')
ax.set_title('How many indicators a form can hold in each level: from fewest to most')
save(fig, '05_indicators_per_level.png', NOTE + ' Computed exactly over every form consistent with the documented structure.')
print('figures written:', sorted(p.name for p in OUT.glob('*.png')))
