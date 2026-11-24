#!/usr/bin/env python3
"""Research charts for Module 1 (VioGén 2). usage: charts.py [repository_root]
All values come from the verified CSVs; unverified points are drawn hollow and labelled."""
import sys
from pathlib import Path
import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DEL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
DATA = DEL / 'data' / '01_statistics'
OUT = DEL / 'figures' / '01_statistics'
OUT.mkdir(parents=True, exist_ok=True)
SURF, INK, INK2, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df'
S1, S2, S3 = '#2a78d6', '#eb6834', '#1baf7a'                       # categorical, fixed order
ORD = ['#86b6ef', '#5598e7', '#256abf', '#104281']                 # ordinal blue ramp (validated)
REFORM = pd.Timestamp('2025-07-15')
SUP_START = pd.Timestamp('2024-11-15')
PROT19 = pd.Timestamp('2019-03-13')                                # Instrucción 4/2019 in force
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': GRID,
                     'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
                     'axes.facecolor': SURF, 'figure.facecolor': SURF, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6,
                     'axes.titlesize': 12, 'axes.titleweight': 'bold', 'axes.titlecolor': INK})

nat = pd.read_csv(DATA / 'national_monthly_verified.csv', parse_dates=['date'])
reg = pd.read_csv(DATA / 'regional_monthly_panel.csv', parse_dates=['date'])
pol = pd.read_csv(DATA / 'police_force_monthly_panel.csv', parse_dates=['date'])
verified = nat['verification_status'].str.startswith('verified')
press = nat['verification_status'].str.startswith('NOT verified')        # Oct 2026 press relay only
natv = nat.copy()
natv.loc[~verified, ['medium_plus_pct', 'no_appreciable', 'low', 'medium', 'high', 'extreme', 'active']] = np.nan

def markers(ax, ymax, with2019=True):
    ms = [(SUP_START, '"Supervisados" first printed,\nnew bulletin format (Nov 2024)', 'right', -8),
          (REFORM, '2025 protocol:\n"No apreciado" abolished', 'left', 8)]
    if with2019:
        ms.insert(0, (PROT19, '2019 protocol\n(13 Mar 2019)', 'left', 8))
    for x, txt, ha, dx in ms:
        ax.axvline(x, color=INK2, lw=1, ls=(0, (3, 3)))
        ax.text(x + pd.Timedelta(days=dx), ymax, txt, ha=ha, va='top', fontsize=8, color=INK2,
                transform=ax.get_xaxis_transform())

def finish(fig, ax, name, note, yearly=False):
    if yearly:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    else:
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.text(0.01, 0.01, note, fontsize=7.5, color=INK2, ha='left', va='bottom', wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)

SRC = ('Source: DGVG Boletín estadístico mensual (official PDFs), Jan 2018–Sep 2026; Oct 2026 press relay (hollow, unverified); '
       'gaps = months whose tables could not be extracted. ')

# 1 ---- national share medium or above
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.plot(natv.date, natv.medium_plus_pct, color=S1, lw=1.8)
ax.plot(natv.date, natv.medium_plus_pct, 'o', color=S1, ms=3.5, mec=SURF, mew=0.8)
u = nat[press]
ax.plot(u.date, u.medium_plus_pct, 'o', mfc=SURF, mec=S1, ms=6, mew=1.5)
mp = natv.set_index('date').medium_plus_pct
for a, b, xy, ha in [('2024-10-31', '2024-11-30', (-14, -18), 'right'), ('2025-06-30', '2025-07-31', (10, -22), 'left'),
                     ('2019-02-28', '2019-03-31', (6, -26), 'left')]:
    d = mp[b] - mp[a]
    ax.annotate(f"{d:+.1f} pts in one month".replace('-', '\u2212'), (pd.Timestamp(b), mp[b]),
                textcoords='offset points', xytext=xy, ha=ha, fontsize=8.5, color=INK)
ax.set_ylim(7, 19); ax.set_ylabel('% of active cases medium, high or extreme')
ax.set_title('National medium-or-above share, 2018–2026: the sharpest one-month break is November 2024')
markers(ax, 0.98)
finish(fig, ax, '01_national_medium_plus_share.png', SRC + 'Month-end stocks: the share does not show which cases changed level, '
       'nor the protection delivered.', yearly=True)

# 2 ---- composition of active cases (counts)
fig, ax = plt.subplots(figsize=(11, 4.8))
n = nat[verified].copy()
n['he'] = n.high + n.extreme
parts = [('no_appreciable', '"No apreciado" (no appreciable risk)', ORD[0]), ('low', 'Low', ORD[1]),
         ('medium', 'Medium', ORD[2]), ('he', 'High + extreme', ORD[3])]
bottom = np.zeros(len(n))
for col, lab, c in parts:
    vals = n[col].fillna(0).values
    ax.bar(n.date, vals, bottom=bottom, width=26, color=c, label=lab, edgecolor=SURF, linewidth=0.5)
    bottom += vals
ax.set_ylabel('active cases (end of month)')
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))
ax.set_title('Active cases by risk level: "No apreciado" grows with the 2019 protocol and is folded into "Low" in July 2025',
             pad=26)
ax.legend(frameon=False, ncol=4, loc='lower left', bbox_to_anchor=(0, 1.0), fontsize=8.5)
ax.set_ylim(0, 140000)
markers(ax, 0.98)
finish(fig, ax, '02_national_composition_counts.png', SRC.replace('; Oct 2026 press relay (hollow, unverified)', '')
       + '"No apreciado" is abolished from July 2025 (not zero). '
       'Each bar is a stock of active cases (victim–aggressor pairs), not a count of individual women.', yearly=True)

# 3 ---- June vs July 2025 transition
fig, ax = plt.subplots(figsize=(10, 3.4))
jj = nat[nat.date.isin(pd.to_datetime(['2025-06-30', '2025-07-31']))].copy()
jj['he'] = jj.high + jj.extreme
ylab = ['30 Jun 2025', '31 Jul 2025']
left = np.zeros(2)
for col, lab, c in parts:
    vals = jj[col].fillna(0).values
    ax.barh(ylab, vals, left=left, color=c, label=lab, edgecolor=SURF, linewidth=2, height=0.55)
    for i, val in enumerate(vals):
        if val > 4000:
            ax.text(left[i] + val / 2, i, f'{int(val):,}', ha='center', va='center', fontsize=8.5,
                    color='white' if c in ORD[2:] else INK)
    left += vals
for i, (a, s, he) in enumerate(zip(jj.active, jj.supervised, jj.he)):
    ax.text(left[i] + 900, i, f'{int(a):,} active\n(incl. {int(he):,} high/extreme)\n+ {int(s):,} supervised',
            va='center', fontsize=8, color=INK2)
ax.invert_yaxis(); ax.set_xlim(0, 130000); ax.grid(axis='y', visible=False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f'{int(x/1000)}k'))
ax.set_title('The reform month: two month-end stocks, one category fewer')
ax.set_title(ax.get_title(), pad=24)
ax.legend(frameon=False, ncol=4, loc='lower left', bbox_to_anchor=(0, 1.0), fontsize=8.5)
fig.text(0.01, 0.01, 'Source: DGVG bulletins June and July 2025 (official PDFs, territorial TOTAL rows). Two stocks one month apart: '
         'they do not show which individual cases were reclassified.', fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(OUT / '03_june_july_2025_transition.png', dpi=200); plt.close(fig)

# 4 ---- supervised status
fig, ax = plt.subplots(figsize=(10, 4.2))
s = nat[verified & nat.supervised.notna()]
ax.bar(s.date, s.supervised, width=22, color=S1, edgecolor=SURF)
for d in ['2024-11-30', '2025-06-30', s.date.max().strftime('%Y-%m-%d')]:
    r = nat[nat.date == d].iloc[0]
    ax.annotate(f"{int(r.supervised):,}", (r.date, r.supervised), textcoords='offset points', xytext=(0, 4),
                ha='center', fontsize=8, color=INK)
ax.set_xlim(pd.Timestamp('2024-09-01'), pd.Timestamp('2026-10-31'))
ax.set_ylabel('cases in "Supervisados" status')
ax.set_title('A new administrative status: "Supervisados" cases (outside the active count)')
ax.axvline(REFORM, color=INK2, lw=1, ls=(0, (3, 3)))
ax.text(REFORM + pd.Timedelta(days=8), 0.98, '2025 protocol (July 2025)', transform=ax.get_xaxis_transform(),
        fontsize=8, color=INK2, va='top')
ax.set_ylim(0, s.supervised.max() * 1.22)
finish(fig, ax, '04_supervised_status.png', 'Source: DGVG bulletins (official PDFs). The column first appears in the November 2024 bulletin. '
       'Supervised cases are in a temporary special-follow-up phase before inactivation; they are not counted among active cases.')

# 5 ---- regions heatmap
r = reg[reg.risk_levels_reported == True].copy()
order = (r[r.date == r.date.max()].sort_values('medium_plus_pct', ascending=False).unit.tolist())
piv = r.pivot_table(index='unit', columns='date', values='medium_plus_pct').reindex(order)
allm = pd.date_range(piv.columns.min(), piv.columns.max(), freq='ME')
piv = piv.reindex(columns=allm)                                    # months not extracted stay blank
fig, ax = plt.subplots(figsize=(12, 6))
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list('blue', ['#cde2fb', '#86b6ef', '#3987e5', '#1c5cab', '#0d366b'])
cmap.set_bad(SURF)
im = ax.imshow(np.ma.masked_invalid(piv.values), aspect='auto', cmap=cmap, vmin=5, vmax=30, interpolation='nearest')
ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index, fontsize=8.5)
xt = [i for i, d in enumerate(piv.columns) if d.month == 1]
ax.set_xticks(xt); ax.set_xticklabels([piv.columns[i].strftime('%Y') for i in xt], fontsize=8)
ax.grid(False)
ri = [i for i, d in enumerate(piv.columns) if d >= pd.Timestamp('2025-07-01')][0]
ax.axvline(ri - 0.5, color='white', lw=2)
ni = [i for i, d in enumerate(piv.columns) if d >= pd.Timestamp('2024-11-01')][0]
ax.axvline(ni - 0.5, color='white', lw=1.2, ls=(0, (3, 2)))
pi_ = [i for i, d in enumerate(piv.columns) if d >= pd.Timestamp('2019-03-01')][0]
ax.axvline(pi_ - 0.5, color='white', lw=1.2, ls=(0, (1, 2)))
cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01, extend='both')
cb.set_label('% of active cases medium or above (colour clipped at 5% and 30%)', color=INK2)
ax.set_title('Medium-or-above share by region, month by month (17 regions publishing risk levels)')
fig.text(0.01, 0.01, 'Source: DGVG bulletins (official PDFs), Jan 2018–Sep 2026; blank columns = months not extracted. White lines: '
         'dotted = 2019 protocol (Mar 2019), dashed = Nov 2024, solid = 2025 protocol (Jul 2025).\nRegional differences reflect case mix, police forces present and practice together; '
         'they do not measure officer behaviour.', fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(OUT / '05_regions_medium_plus_heatmap.png', dpi=200); plt.close(fig)

# 6 ---- police forces
p = pol[pol.risk_levels_reported == True].copy()
p['group'] = np.where(p.unit == 'Guardia Civil', 'Guardia Civil',
                      np.where(p.unit == 'Policía Nacional', 'Policía Nacional',
                               np.where(p.unit.str.startswith('PL '), 'Local police (all PL combined)', 'other')))
g = p[p.group != 'other'].groupby(['date', 'group'])[['medium_plus', 'active']].sum()
gp = (100 * g.medium_plus / g.active).unstack()
gp = gp.reindex(pd.date_range(gp.index.min(), gp.index.max(), freq='ME'))   # gaps break the lines
fig, ax = plt.subplots(figsize=(10, 4.6))
for grp, c in [('Guardia Civil', S1), ('Policía Nacional', S2), ('Local police (all PL combined)', S3)]:
    d = gp[grp]
    ax.plot(d.index, d.values, color=c, lw=2, label=grp)
    ax.plot(d.index, d.values, 'o', color=c, ms=2.2)                 # keeps isolated months visible
    last = d.dropna().index[-1]
    ax.text(last + pd.Timedelta(days=12), d[last], f'{grp}  {d[last]:.1f}%', va='center', fontsize=8.5, color=INK)
for dt, xy in [(gp.index[0], (4, 8)), (pd.Timestamp('2023-06-30'), (-170, 2))]:
    gap = gp.loc[dt, 'Guardia Civil'] - gp.loc[dt, 'Policía Nacional']
    ax.annotate(f"GC − PN: {gap:.1f} pts ({dt:%b %Y})", (dt, gp.loc[dt, 'Guardia Civil']), textcoords='offset points',
                xytext=xy, fontsize=8, color=INK)
ax.set_xlim(pd.Timestamp('2020-01-01'), pd.Timestamp('2027-09-30'))
ax.set_ylabel('% of each institution\'s active cases'); ax.set_ylim(0, 26)
ax.legend(frameon=False, loc='lower left', ncol=3, fontsize=8.5)
ax.set_title('Medium-or-above share by police institution: the Guardia Civil gap opens in 2021–2023')
markers(ax, 0.66, with2019=False)
finish(fig, ax, '06_police_forces_medium_plus.png', SRC.replace('; Oct 2026 press relay (hollow, unverified)', '')
       .replace('Jan 2018', 'Feb 2020 (first police-institution table)') +
       'June 2025: previous transcription of the VioGén portal table. Institutions cover different territories and populations; '
       'differences do not establish officer behaviour, overrides or bias.', yearly=True)

# 7 ---- regions June vs July 2025
a = r[r.date == '2025-06-30'].set_index('unit').medium_plus_pct
b = r[r.date == '2025-07-31'].set_index('unit').medium_plus_pct
df = pd.DataFrame({'jun': a, 'jul': b}).dropna().sort_values('jul')
fig, ax = plt.subplots(figsize=(8, 6))
y = np.arange(len(df))
ax.hlines(y, df.jun, df.jul, color=GRID, lw=2)
ax.plot(df.jun, y, 'o', color=S1, ms=8, mec=SURF, mew=1.5, label='30 Jun 2025')
ax.plot(df.jul, y, 'o', color=S2, ms=8, mec=SURF, mew=1.5, label='31 Jul 2025')
ax.set_yticks(y); ax.set_yticklabels(df.index, fontsize=8.5); ax.grid(axis='y', visible=False)
ax.set_xlabel('% of active cases medium or above')
ax.legend(frameon=False, loc='lower right', fontsize=8.5)
ax.set_title('Across the reform month, region by region')
fig.text(0.01, 0.01, 'Source: DGVG bulletins June and July 2025 (official PDFs). One-month change; not a causal effect.',
         fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(OUT / '07_regions_june_july_2025.png', dpi=200); plt.close(fig)
# 8 ---- how many provinces move together, month by month (break test)
prov = pd.read_csv(DATA / 'provincial_monthly_panel.csv', parse_dates=['date'])
pr = prov[prov.risk_levels_reported == True].copy()
pr['na_pct'] = 100 * pr.no_appreciable / pr.active
allm = pd.date_range(pr.date.min(), pr.date.max(), freq='ME')
mp_w = pr.pivot_table(index='date', columns='unit', values='medium_plus_pct').reindex(allm)
na_w = pr.pivot_table(index='date', columns='unit', values='na_pct').reindex(allm)
def share_moving(w, sign):
    d = w.diff()                                           # only consecutive months give a value
    n = d.notna().sum(axis=1)
    k = (d < 0).sum(axis=1) if sign < 0 else (d > 0).sum(axis=1)
    return (100 * k / n).where(n > 0)
fall = share_moving(mp_w, -1)
rise = share_moving(na_w[na_w.index <= '2025-06-30'], +1)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.2), sharex=True)
hl1 = {pd.Timestamp('2024-11-30'): 'Nov 2024', pd.Timestamp('2020-03-31'): 'Mar 2020\n(COVID-19\nstate of alarm)'}
hl2 = {pd.Timestamp('2019-03-31'): '', pd.Timestamp('2019-04-30'): 'Mar / Apr 2019', pd.Timestamp('2024-11-30'): 'Nov 2024'}
for ax, ser, hl, title in [(a1, fall, hl1, 'Provinces where the medium-or-above share FELL (%)'),
                           (a2, rise, hl2, 'Provinces where the "No apreciado" share ROSE (%)')]:
    cols = [ORD[3] if d in hl else ORD[0] for d in ser.index]
    ax.bar(ser.index, ser.values, width=26, color=cols, edgecolor=SURF, linewidth=0.5)
    ax.axhline(50, color=INK2, lw=0.8, ls=(0, (2, 2)))
    for d, lab in hl.items():
        if lab and d in ser.index and pd.notna(ser[d]):
            txt = (f"{lab}: {ser[pd.Timestamp('2019-03-31')]:.0f}% / {ser[d]:.0f}%" if lab.startswith('Mar / Apr')
                   else f"{lab}: {ser[d]:.0f}%")
            ax.annotate(txt, (d, ser[d]), textcoords='offset points', xytext=(0, 3),
                        ha='left' if lab.startswith('Mar / Apr') else 'center', va='bottom', fontsize=7.5, color=INK)
    ax.set_ylim(0, 125); ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_title(title, loc='left', fontsize=10)
    for x in (PROT19, SUP_START, REFORM):
        ax.axvline(x, color=INK2, lw=0.8, ls=(0, (3, 3)))
a2.set_xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2026-11-30'))
a2.xaxis.set_major_locator(mdates.YearLocator()); a2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
fig.suptitle('How many of the 45 provinces move in the same direction in the same month', fontweight='bold', fontsize=12, x=0.01, ha='left')
fig.text(0.01, 0.01, 'Source: DGVG bulletins (official PDFs), Jan 2018–Sep 2026; 45 province-equivalents publishing risk levels. '
         'A bar needs the month before to have been extracted (gaps = months not extracted).\nDashed lines: 2019 protocol, Nov 2024, '
         '2025 protocol. In an ordinary month about half the provinces move each way (dotted line).\nA simultaneous move in almost '
         'every province points to a system-wide change; it does not identify which one.', fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.08, 1, 0.97)); fig.savefig(OUT / '08_provinces_moving_together.png', dpi=200); plt.close(fig)

print('charts written:', sorted(x.name for x in OUT.glob('*.png')))
