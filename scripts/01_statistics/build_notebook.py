#!/usr/bin/env python3
"""Build the Module 1 Colab notebook. usage: build_notebook.py [notebook_output_directory]"""
import sys
from pathlib import Path
import nbformat as nbf

DEL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s))
code = lambda s: C.append(nbf.v4.new_code_cell(s))

md("""# VioGén 2 · Module 1: how the 2025 reform reshaped the risk categories that structure police follow-up

**Course:** Data and Algorithms for Public Policy (Sciences Po, S. Chignard & P.-E. Devineau) · **Group D**

**Question for this module.** VioGén 2 changed *how cases are classified and administered*: the lowest
category ("No apreciado") was abolished from July 2025, and a new administrative status ("Supervisados")
appears in the statistics from November 2024. This notebook uses the official monthly bulletins from
January 2018 to September 2026 to show **what changed in the published classifications, where, and what
the published data cannot tell us**. Starting in 2018 lets the earlier protocol change (Instrucción 4/2019, in
force 13 March 2019) serve as a benchmark for the 2025 one. It is an investigation of a socio-technical decision process, *not*
an audit of predictive accuracy.

**What the data are.** End-of-month *stocks* of VioGén cases (a case = one victim–aggressor pair), from the
Delegación del Gobierno contra la Violencia de Género's *Boletín estadístico mensual* (BEM). Every table
was extracted from the official PDFs and checked: each row adds up, provinces add up to their region,
regions and police institutions add up to the national total. See [Methods and limitations](../../docs/01_statistics/METHODS_AND_LIMITATIONS.md).

**What the data are not.** They do not contain the 2025 scoring algorithm, individual case trajectories,
officer override records, or the protection actually delivered.

Run the cells from top to bottom. In Google Colab, the first cell asks you to upload the package ZIP.""")

code("""# 0. Find the repository, locally or in Google Colab.
from pathlib import Path
import tempfile
import zipfile

marker = Path('data/01_statistics/national_monthly_verified.csv')
cwd = Path.cwd()
repo = next((p for p in (cwd, *cwd.parents) if (p / marker).is_file()), None)
if repo is None:
    try:
        from google.colab import files
    except ImportError:
        raise FileNotFoundError('Open the notebook inside the VioGen-Risk-Assessment repository.') from None
    uploaded = files.upload()
    archive = next((name for name in uploaded if name.lower().endswith('.zip')), None)
    if archive is None:
        raise ValueError('Choose the repository ZIP.')
    unpacked = Path(tempfile.mkdtemp(prefix='viogen-'))
    with zipfile.ZipFile(archive) as source:
        source.extractall(unpacked)
    candidates = [p for p in (unpacked, *unpacked.iterdir()) if (p / marker).is_file()]
    if len(candidates) != 1:
        raise FileNotFoundError('The ZIP must contain the repository and its data/01_statistics folder.')
    repo = candidates[0]
data_dir = repo / 'data' / '01_statistics'
figure_dir = repo / 'figures' / '01_statistics'
scripts_dir = repo / 'scripts' / '01_statistics'""")

code("""import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Image
pd.set_option('display.width', 160); pd.set_option('display.max_columns', 30)
nat  = pd.read_csv(data_dir / 'national_monthly_verified.csv', parse_dates=['date'])
reg  = pd.read_csv(data_dir / 'regional_monthly_panel.csv', parse_dates=['date'])
prov = pd.read_csv(data_dir / 'provincial_monthly_panel.csv', parse_dates=['date'])
pol  = pd.read_csv(data_dir / 'police_force_monthly_panel.csv', parse_dates=['date'])
cov  = pd.read_csv(data_dir / 'month_by_month_coverage.csv')
val  = pd.read_csv(data_dir / 'validation_report.csv')
err  = pd.read_csv(data_dir / 'extraction_errors.csv')
chg  = pd.read_csv(data_dir / 'national_changelog.csv')
print(f'national months: {len(nat)} | regional rows: {len(reg)} | provincial rows: {len(prov)} | police-institution rows: {len(pol)}')""")

md("## 1. Coverage: what is actually in the dataset")
code("""tab = cov.pivot(index='month', columns='breakdown', values='status')
summary = cov.assign(ok=cov.status.str.startswith('extracted and reconciled')).groupby('breakdown').ok.agg(['sum','count'])
summary.columns = ['months extracted and reconciled', 'months in window']
display(summary)
print('Months not fully extracted:')
display(tab[~tab.apply(lambda r: r.str.startswith('extracted and reconciled').all(), axis=1)])""")

md("""## 2. Independent re-check of every table in this notebook

The extractor already refused any table that did not reconcile. The cells below re-run the arithmetic
from the CSVs alone, so the checks do not depend on the extraction code.""")
code("""LEV = ['no_appreciable','low','medium','high','extreme']
def row_ok(df):
    d = df[df.risk_levels_reported == True]
    lv = d[LEV].fillna(0).sum(axis=1)
    return (lv == d.active).all()
checks = {'regional rows: levels sum to active': row_ok(reg),
          'provincial rows: levels sum to active': row_ok(prov),
          'police rows: levels sum to active': row_ok(pol)}
# regions (publishing levels) sum to the national total, month by month
r = reg[reg.risk_levels_reported == True].groupby('date')[['low','medium','high','extreme','active']].sum()
n = nat.set_index('date')[['low','medium','high','extreme','active']]
checks['17 regions sum to national, every month'] = (r == n.loc[r.index]).all().all()
p = prov[prov.risk_levels_reported == True].groupby('date')[['low','medium','high','extreme','active']].sum()
checks['45 province-equivalents sum to national, every month'] = (p == n.loc[p.index]).all().all()
f = pol[pol.risk_levels_reported == True].groupby('date')[['low','medium','high','extreme','active']].sum()
checks['police institutions sum to national, every month'] = (f == n.loc[f.index]).all().all()
display(pd.Series(checks, name='passes'))
print('validation_report.csv:', val.result.value_counts().to_dict())
print('Every row that is not a pass (FAIL = arithmetic failure; tables that fail are excluded from the panels):')
display(val[val.result != 'pass'])""")

md("""### Corrections to the national series received from the previous stage
Every month with an official bulletin was re-extracted from the PDF. The changelog lists values that
differed from the series supplied in the reference, and press-relay months that the official PDF confirmed.""")
code("display(chg)")

md("""## 3. National series: the lowest category disappears, the higher categories barely move

`medium_plus` (medium + high + extreme) is the most comparable grouping across the July 2025 break, but it
is **not a constant construct**: the 2025 protocol also introduced new indicators and recalibrated
algorithms (not published), so the same woman need not receive the same level before and after.""")
code("""cols = ['date','protocol_period','no_appreciable','low','medium','high','extreme','active','supervised',
        'medium_plus_pct','high_plus_pct','verification_status']
display(nat[cols].assign(verification_status=nat.verification_status.str[:60]))
display(Image(filename=str(figure_dir / '01_national_medium_plus_share.png')))
display(Image(filename=str(figure_dir / '02_national_composition_counts.png')))""")

md("""### Where the series actually breaks

The visual impression is of one break in July 2025. The month-to-month changes say otherwise.""")
code("""v = nat[nat.verification_status.str.startswith('verified')].set_index('date')
v = v.reindex(pd.date_range(v.index.min(), v.index.max(), freq='ME'))   # gaps stay gaps: no diff across them
moves = v.medium_plus_pct.diff().dropna()
print('Largest one-month changes in the medium-or-above share, Jan 2018 - Sep 2026 (percentage points;')
print('only pairs of consecutive extracted months):')
display(moves.reindex(moves.abs().sort_values(ascending=False).index).head(5).round(2).to_frame('change, pp'))
lv = ['no_appreciable','low','medium','high','extreme','active']
display(v.loc[pd.to_datetime(['2019-02-28','2019-03-31','2019-04-30','2024-10-31','2024-11-30','2025-06-30','2025-07-31']),
             lv + ['supervised','medium_plus_pct']])""")
md("""**Reading.**
- **November 2024 is the largest one-month change in the window.** The medium-or-above share falls by about 1.7
  points while the active total barely moves, and "No apreciado" grows. That month the bulletin also first prints
  *Supervisados* and switches to new institution names.
- **July 2025**, when the protocol formally changes, moves the share by about +0.2 points.
- **March 2019 was different.** The previous protocol change (Instrucción 4/2019, in force 13 March 2019) barely moved
  the medium-or-above share either. Its footprint is at the bottom of the scale: "No apreciado" jumps from 43.9% of active
  cases in February 2019 to 52.5% in April 2019, while "Low" shrinks.

For November 2024, two readings are possible, and the published data cannot tell them apart:

* a change in **classification practice** (the VioGén 2 platform was tested for seven months before its
  January 2025 presentation);
* a change in **how the statistics were compiled**.

This is a precise question for an interview with Interior or with the protocol's designers. The next section
narrows it.""")

md("""### Break test: do the provinces move together?

A change in local practice spreads unevenly. A change made centrally (a scoring rule, the software, how the figures
are compiled) moves every province in the same month. For each month, the cell below counts how many of the 45
province-equivalents publishing risk levels moved in the same direction as the previous month. Only pairs of
consecutive extracted months count.""")
code("""pr = prov[prov.risk_levels_reported == True].copy()
pr['na_pct'] = 100 * pr.no_appreciable / pr.active
allm = pd.date_range(pr.date.min(), pr.date.max(), freq='ME')
mp_w = pr.pivot_table(index='date', columns='unit', values='medium_plus_pct').reindex(allm)
na_w = pr.pivot_table(index='date', columns='unit', values='na_pct').reindex(allm)
def moving(w):
    d = w.diff(); n = d.notna().sum(axis=1)
    return pd.DataFrame({'provinces compared': n,
                         '% falling': (100 * (d < 0).sum(axis=1) / n).round(0),
                         '% rising': (100 * (d > 0).sum(axis=1) / n).round(0),
                         'median change, pp': d.median(axis=1).round(2)})[n > 0]
mpm, nam = moving(mp_w), moving(na_w[na_w.index <= '2025-06-30'])
print('Medium-or-above share: months with the most provinces falling together')
display(mpm.sort_values('% falling', ascending=False).head(6))
print('"No apreciado" share: months with the most provinces rising together')
display(nam.sort_values('% rising', ascending=False).head(6))
print(f"Ordinary month: median {mpm['% falling'].median():.0f}% of provinces falling (medium-or-above), "
      f"{nam['% rising'].median():.0f}% rising (No apreciado).")
display(Image(filename=str(figure_dir / '08_provinces_moving_together.png')))""")
code("""# the same test on police institutions with at least 500 active cases (Oct -> Nov 2024)
q = pol[(pol.risk_levels_reported == True) & pol.date.isin(pd.to_datetime(['2024-10-31', '2024-11-30']))]
w = q.pivot_table(index='unit', columns='date', values=['medium_plus_pct', 'active'])
w = w[w[('active', pd.Timestamp('2024-10-31'))] >= 500]
chg_inst = (w[('medium_plus_pct', pd.Timestamp('2024-11-30'))] - w[('medium_plus_pct', pd.Timestamp('2024-10-31'))])
print(f'{(chg_inst < 0).sum()} of {len(chg_inst)} large institutions fell in November 2024 (percentage points):')
display(chg_inst.sort_values().round(1).to_frame('change Oct -> Nov 2024'))""")
md("""**Reading.**
- **November 2024 is the most synchronised fall in the medium-or-above share in the window.** In the publishing
  provinces the share fell in 44 of 45, against roughly half in an ordinary month, and "No apreciado" rose in most of
  them. The Guardia Civil, the Policía Nacional and most local police forces fell by similar amounts.
- **The shape matches the 2019 protocol change.** In March and April 2019, "No apreciado" rose in almost every province
  at once.
- **February 2019 also stands out.** 84% of provinces fell that month, two weeks before the 2019 protocol took
  effect. The bulletins give no explanation.
- **Simultaneity has other causes too.** The March 2020 COVID-19 state of alarm also moved most provinces together.
  A synchronised move shows that the cause was **system-wide**, not which system-wide change it was.

What this makes unlikely is a gradual, officer-by-officer shift in practice. What it leaves open is a scoring or
procedural change applied centrally versus a change in how the statistics were produced. That is the question to
put to Interior or the protocol's designers.""")

md("### The reform month: 30 June versus 31 July 2025")
code("""jj = nat[nat.date.isin(pd.to_datetime(['2025-06-30','2025-07-31']))].set_index('date')
comp = jj[['no_appreciable','low','medium','high','extreme','active','supervised','inactive','total']].T
comp['change'] = comp.iloc[:,1].fillna(0) - comp.iloc[:,0].fillna(0)
display(comp)
lowest_jun = jj.iloc[0][['no_appreciable','low']].sum(); low_jul = jj.iloc[1]['low']
print(f'June "No apreciado" + "Low" = {lowest_jun:,.0f}; July "Low" = {low_jul:,.0f} '
      f'(difference {low_jul - lowest_jun:+,.0f}).')
print(f"Medium-or-above share: {jj.iloc[0].medium_plus_pct:.2f}% -> {jj.iloc[1].medium_plus_pct:.2f}%")
display(Image(filename=str(figure_dir / '03_june_july_2025_transition.png')))""")

md("""**Reading.** In one month the "No apreciado" category (44,661 cases on 30 June) disappears and "Low"
roughly doubles, while the medium-or-above share moves by a fraction of a point. The published stocks are
consistent with the old lowest category being absorbed into "Low", but they **cannot show** which cases moved
where: this is a comparison of two stocks, and the counts also change through new entries, closures and
re-assessments during the month.""")

md("""## 4. A new administrative status: "Supervisados"

The bulletins print a *Supervisados* column from **November 2024**, eight months before the category
change. Supervised cases are in a temporary special-follow-up phase before inactivation and are **not** in
the active count. Under the 2025 protocol, the choice between keeping a case active, supervising it or
inactivating it is a procedural decision with its own rules, so this column is one of the few published
traces of how follow-up is administered.""")
code("""s = nat.dropna(subset=['supervised'])[['date','active','supervised','supervised_per_100_active']]
display(s)
pk = s.loc[s.supervised.idxmax()]
print(f"Peak: {pk.supervised:,.0f} supervised cases on {pk.date:%d %b %Y}; latest verified: "
      f"{s.iloc[-1].supervised:,.0f} on {s.iloc[-1].date:%d %b %Y}.")
display(Image(filename=str(figure_dir / '04_supervised_status.png')))""")

md("""## 5. Regions and police institutions

Differences between territories or institutions reflect **different populations, case mixes, police forces
and practices together**. They are not measures of officer behaviour, overrides or bias.""")
code("""r = reg[reg.risk_levels_reported == True]
wide = r.pivot_table(index='unit', columns='date', values='medium_plus_pct')
snap = wide[[pd.Timestamp('2024-06-30'), pd.Timestamp('2025-06-30'), pd.Timestamp('2025-07-31'), wide.columns.max()]].round(1)
snap.columns = ['Jun 2024','Jun 2025','Jul 2025', wide.columns.max().strftime('%b %Y')]
display(snap.sort_values(snap.columns[-1], ascending=False))
spread = wide.agg(['min','median','max']).T
print('Spread of the regional medium-or-above share (percentage points), selected months:')
display((spread.loc[[pd.Timestamp('2023-01-31'), pd.Timestamp('2025-06-30'), pd.Timestamp('2025-07-31'), spread.index.max()]]).round(1))
display(Image(filename=str(figure_dir / '05_regions_medium_plus_heatmap.png')))
display(Image(filename=str(figure_dir / '07_regions_june_july_2025.png')))""")

code("""p = pol[pol.risk_levels_reported == True].copy()
p['group'] = np.select([p.unit.eq('Guardia Civil'), p.unit.eq('Policía Nacional'), p.unit.str.startswith('PL ')],
                       ['Guardia Civil', 'Policía Nacional', 'Local police (PL, combined)'], 'other')
g = p[p.group != 'other'].groupby(['date','group'])[['medium_plus','active']].sum()
g['medium_plus_pct'] = (100 * g.medium_plus / g.active).round(2)
gp = g.medium_plus_pct.unstack()
display(gp.loc[[d for d in pd.to_datetime(['2020-02-29','2023-01-31','2024-06-30','2025-06-30','2025-07-31']) if d in gp.index]
               + [gp.index.max()]])
print('Institutions reported per month (names and numbers change; nothing is padded):')
display(pol.groupby('date').unit.nunique().value_counts().rename('months'))
display(Image(filename=str(figure_dir / '06_police_forces_medium_plus.png')))""")

md("""### The Guardia Civil gap is recent

The police-institution table starts in February 2020. The cell below follows the gap between the two state forces
and asks how much of the national rise in the medium-or-above share is a Guardia Civil phenomenon.""")
code("""gc = p[p.unit == 'Guardia Civil'].set_index('date')[['medium_plus', 'active']]
pn = p[p.unit == 'Policía Nacional'].set_index('date')[['medium_plus', 'active']]
nn = nat.set_index('date')[['medium_plus', 'active']]
t = pd.DataFrame({'GC %': 100 * gc.medium_plus / gc.active, 'PN %': 100 * pn.medium_plus / pn.active,
                  'national %': 100 * nn.medium_plus / nn.active,
                  'national without GC %': 100 * (nn.medium_plus - gc.medium_plus) / (nn.active - gc.active),
                  'GC share of active cases %': 100 * gc.active / nn.active,
                  'GC share of medium-or-above cases %': 100 * gc.medium_plus / nn.medium_plus}).dropna()
t['GC - PN gap, pts'] = t['GC %'] - t['PN %']
sel = [d for d in pd.to_datetime(['2020-02-29','2021-03-31','2021-12-31','2022-12-31','2023-06-30','2024-10-31',
                                  '2024-11-30','2025-07-31','2026-09-30']) if d in t.index]
display(t.loc[sel].round(1))""")
md("""**Reading.**
- **The gap opened recently.** In February 2020 the two state forces rated a similar share of their active cases
  medium or above, about a point apart. The gap opened between 2021 and mid-2023, to about 10 points, and has stayed
  there since.
- **The national rise is mostly the Guardia Civil.** From March 2021 to June 2023 the national medium-or-above share
  rose from 10.8% to 16.8%. Without the Guardia Civil it rose only from 9.9% to 11.7%. By September 2026 the Guardia
  Civil held about 45% of active cases but 65% of the medium-or-above ones.
- **The same tool and rules applied throughout.** Both forces worked under the 2019 protocol across these years.
  A divergence under one instrument is exactly where institutional discretion, training or case mix would show.
  The data cannot say which, and the Guardia Civil's caseload also grew faster.
- **The question for the interview.** What changed in the Guardia Civil's use of VioGén between 2021 and 2023?""")

md("""## 6. What this means for the research question, and what it does not

* **Classification, not observed protection.** The reform's most visible effect in the published data is
  taxonomic: a category is abolished and absorbed. Whether women formerly rated "No apreciado" receive
  different protection now depends on the measures attached to "Low" in the 2025 protocol and on how they are
  applied, which these tables do not record.
* **The composition break comes before the formal reform, and it is system-wide.** The medium-or-above share
  drops most sharply in November 2024, seven months before the 2025 protocol took effect (30 June 2025).
  - *Everywhere at once.* It fell in 44 of 45 provinces, in both state police forces by the same
    amount, and in most local police forces, the same month the bulletin's format changed.
  - *Not local practice.* That pattern points to a central change, not to gradual local practice. The formal
    switch in July 2025 is almost invisible in that share.
* **Protocol changes move the categories, not the medium-or-above share.** The 2019 protocol coincided with a rise in
  "No apreciado" and a fall in "Low" in almost every province at once. The 2025 protocol folded "No apreciado" into
  "Low". Neither moved the medium-or-above share by more than about half a point in its first month.
* **Discretion moves into procedural statuses.** The *Supervisados* status, published from November 2024,
  shows follow-up being administered through rules about activation and inactivation, not only through
  risk levels (see the series in section 4).
* **Formal discretion is one-directional and unpublished.** The 2025 protocol lets the officer raise the
  automatic result, never lower it (Instrucción 1/2025, §3.8 and §6.2). The bulletins do not say how often this
  happens. This is the decisive gap between what the protocol allows and what the statistics show.
* **Institutions diverged under the same rules.** The Guardia Civil rates a larger share of its active cases
  medium or above than the Policía Nacional in every month since February 2020.
  - *Timing.* The gap was about one point in early 2020 and opened to about ten points between 2021 and mid-2023,
    under the same 2019 protocol.
  - *Weight.* Most of the national rise in those years comes from the Guardia Civil.
  - *November 2024.* The break moved both state forces by the same amount and left their gap unchanged.
  - *Limits.* The data cannot separate case mix from practice. The gap is a question for interviews, not a
    finding about officers.
* **Not observable here:** the 2025 indicators and weights, individual reclassifications, upward
  adjustments by officers, and the protection actually delivered.""")

md("""## 7. Optional: reproduce one month from the official PDF

Set `RUN = True` to download one bulletin and re-extract it with the package's extractor
(`scripts/01_statistics/viogen_extract.py`). Most months use the PDF text layer. Image tables (several months in 2020–2021, and
March–September 2026) also need Tesseract (`apt-get install -y tesseract-ocr tesseract-ocr-spa`; `pip install pytesseract
opencv-python-headless`).""")
code("""RUN = False
MONTH = '2025-07'
if RUN:
    import subprocess, sys, json
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pymupdf', 'requests'], check=True)
    sys.path.insert(0, str(scripts_dir))
    import requests, pymupdf, viogen_extract as V
    y, m = int(MONTH[:4]), int(MONTH[5:])
    url = V.BEM_URL.format(m=V.MONTHS_ES[m-1], y=y)
    pdf = Path(f'BEM_{MONTH}.pdf')
    if not pdf.exists():
        pdf.write_bytes(requests.get(url, timeout=120).content)
    doc = pymupdf.open(pdf)
    found = V.find_pages(doc, search=range(40, 90))
    prot, ddate, cols, parsed, probs = V.parse_table(found['territory'][1], 'territory')
    print(MONTH, 'protocol', prot, 'data date', ddate, '| checks failing:', V.reconcile(parsed, cols, prot, 'territory'))
    mine = {k: V.full_values(u, cols) for k, u in parsed.items()}
    panel = reg[reg.date.dt.strftime('%Y-%m') == MONTH].set_index('unit')
    same = all(mine[u]['active'] == panel.loc[u, 'active'] for u in panel.index if panel.loc[u, 'risk_levels_reported'])
    print('re-extraction matches the regional panel:', same)""")

nb['cells'] = C
nb['metadata'] = {'kernelspec': {'name': 'python3', 'display_name': 'Python 3'},
                  'language_info': {'name': 'python'}, 'colab': {'provenance': []}}
nbf.write(nb, DEL / 'VioGen_2_Module1_Completed.ipynb')
print('notebook written')
