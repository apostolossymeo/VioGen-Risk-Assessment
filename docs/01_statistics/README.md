# VioGén 2 · Module 1: completed data package

Group D, *Data and Algorithms for Public Policy* (Sciences Po).

**Research question.** How does VioGén 2 transform administrative discretion in police risk management?
- *What this module does.* It uses the official monthly statistics to show what the 2025 reform changed in the
  *published classifications and statuses* that structure police follow-up, and what those statistics cannot show.
- *Why it starts in 2018.* The previous protocol change (March 2019) serves as a benchmark.
- *What it is not.* It does not audit the algorithm's accuracy.

## What was extracted and verified

Window: January 2018 – October 2026 (106 months).

| Breakdown | Extracted from the official PDF and fully reconciled | Not available, and why |
|---|---|---|
| National | **96 months** (93 from the territorial table, 3 from the police-institution table) | Oct 2026: press relay only, flagged unverified. 9 months in 2020–21: both tables are images and were not extracted |
| Regional (19 communities and cities) | **93 months** | Oct 2026. 12 months in 2020–21 with image tables (11 not attempted, Dec 2020 attempted but failed its checks) |
| Provincial (52 units) | **93 months** | Same as regional |
| Police institutions | **70 months** | Table first printed in Feb 2020. Jun 2025: portal transcription that reconciles to the bulletin total. Oct 2026. 9 months in 2020–21 with image tables (2 attempted but failed their checks, 7 not attempted) |

"Fully reconciled" means:
- every row adds up;
- provinces sum to their region;
- the 19 regions and all police institutions sum to the national TOTAL;
- where both tables exist, they agree on the TOTAL;
- the printed data date is the month end.

Tables that fail any check are left out. Their failures are listed in [`validation_report.csv`](../../data/01_statistics/validation_report.csv) and
[`extraction_errors.csv`](../../data/01_statistics/extraction_errors.csv), and nothing is filled in.

How the tables were read:
- **Text layer:** most months.
- **OCR of embedded table images:** March–September 2026 (both tables) and the December 2020 police table.
  - *Re-read rows.* 27 rows needed a constrained re-read of their cells. Each is shown against the printed image in
    [`ocr_checks/`](../../sources/01_statistics/ocr_checks/), and all 27 were checked by eye.
  - *External check.* The 2026 OCR national totals match the Interior figures relayed by the press in all seven
    months.
- **2020–2021 image tables.** Several bulletins print their tables as images. The territorial ones were not extracted.
  Where a police-institution table reconciles, its TOTAL row is used as the national row. It is identical to the
  territorial TOTAL in all 67 months where both reconcile.

**Correction to the reference series.** January 2026 *high* is 933, not 953, and *active* is 103,461, not 103,481. Every
press-relay month in the reference from November 2025 to September 2026 is now either confirmed by the official PDF or,
for January 2026, corrected ([`national_changelog.csv`](../../data/01_statistics/national_changelog.csv)).

## Files and replication

| Materials | Location |
|---|---|
| Statistical panels, coverage, validation results and changelog | [Monthly data](../../data/01_statistics/) |
| Eight figures | [Statistical figures](../../figures/01_statistics/) |
| Monthly bulletin excerpts | [Source PDFs](../../sources/01_statistics/bulletins/) |
| OCR rows checked against the published tables | [Verification sheets](../../sources/01_statistics/ocr_checks/) |
| Extraction scripts, checks and chart code | [Scripts](../../scripts/01_statistics/) |

The [executed notebook](../../scripts/01_statistics/VioGen_2_Module1_Completed.ipynb) reads the four panels and repeats their arithmetic checks. Open it inside a local clone or upload the notebook and the repository ZIP to Google Colab. To regenerate the figures from the supplied CSVs, run the following command from the repository root.

```bash
python scripts/01_statistics/charts.py
```

To repeat the PDF extraction, obtain the full bulletins named in the [source manifest](../../data/01_statistics/source_manifest.csv). The manifest records the original URLs, hashes and pages. The repository contains the extracted table pages. OCR additionally requires Tesseract and its Spanish language data.

The following command illustrates extraction for July 2025. Replace the bulletin directory with the path to your downloads.

```bash
python scripts/01_statistics/run_batch.py /path/to/full_bulletins work/viogen 2025-07
```

Supply the other months as additional YYYY-MM arguments. The historical extraction used the police-institution table alone for certain image-only months in 2020–2021. The [coverage table](../../data/01_statistics/month_by_month_coverage.csv) records these decisions. After processing the full set of months, the following commands write the rebuilt files under a separate directory.

```bash
python scripts/01_statistics/compress_sources.py work/viogen/sources work/rebuild/sources/01_statistics/bulletins
python scripts/01_statistics/assemble.py work/viogen data/01_statistics/reference_inputs /path/to/full_bulletins work/rebuild
python scripts/01_statistics/charts.py work/rebuild
```

## Coding rules that matter when you use the data

- **"No apreciado"** is blank (NaN) from July 2025 because the category was abolished. It is **not zero**.
- **Supervisados** is blank before November 2024, when it was not printed. It is outside the active count:
  total = active + supervised + inactive.
- **Catalonia and the Basque Country, and their forces (Mossos, Ertzaintza),** do not publish VioGén risk levels.
  Their level and active cells are blank, with `risk_levels_reported = False`. The printed zeros from February 2026
  are not observed zeros.
- **`medium_plus_pct`** (medium + high + extreme as a share of active cases) is the most comparable series across the
  protocol changes. But each protocol changed the algorithm, so it is not a constant construct.
- **Units are stocks of cases** (victim–aggressor pairs) at month end. They are not women, and not flows.
- **Gaps stay gaps.** Month-to-month comparisons use only pairs of consecutive extracted months.

## Charts

1. [`01_national_medium_plus_share.png`](../../figures/01_statistics/01_national_medium_plus_share.png): national medium-or-above share, 2018–2026, with the three breaks marked.
2. [`02_national_composition_counts.png`](../../figures/01_statistics/02_national_composition_counts.png): active cases by level. "No apreciado" grows with the 2019 protocol and is folded into "Low" in 2025.
3. [`03_june_july_2025_transition.png`](../../figures/01_statistics/03_june_july_2025_transition.png): the two month-end stocks either side of the 2025 reform.
4. [`04_supervised_status.png`](../../figures/01_statistics/04_supervised_status.png): the *Supervisados* status since November 2024.
5. [`05_regions_medium_plus_heatmap.png`](../../figures/01_statistics/05_regions_medium_plus_heatmap.png): 17 regions × month, 2018–2026.
6. [`06_police_forces_medium_plus.png`](../../figures/01_statistics/06_police_forces_medium_plus.png): Guardia Civil, Policía Nacional and local police combined, from February 2020.
7. [`07_regions_june_july_2025.png`](../../figures/01_statistics/07_regions_june_july_2025.png): region-by-region change across the 2025 reform month.
8. [`08_provinces_moving_together.png`](../../figures/01_statistics/08_provinces_moving_together.png): the break test, showing how many of the 45 provinces move in the same direction each month.

## What the data say

- **The formal reforms mainly change the categories.** Neither shifted the medium-or-above share by more than about
  half a point in its first month.
  - *July 2025.* "No apreciado" (44,661 cases on 30 June 2025) disappears and "Low" doubles to 88,772. The
    medium-or-above share moves from 14.6% to 14.8%.
  - *March 2019.* "No apreciado" rose from 43.9% to 52.5% of active cases in two months, in almost every province at
    once (91% in March, 98% in April), while the medium-or-above share moved by +0.6 points.
- **November 2024 is the sharpest and most synchronised break in 2018–2026.**
  - *Size.* The medium-or-above share fell from 16.5% to 14.7% in one month while the active total was flat.
  - *Breadth.* It fell in 44 of 45 provinces, against about half in an ordinary month, and in both state police
    forces by the same amount (−2.0 and −1.9 points).
  - *Format change.* The bulletin first printed *Supervisados* and changed its format that month.
  - *Reading.* A move this simultaneous points to a central change: scoring, procedure or how the statistics were
    compiled. It does not point to gradual local practice. Which one cannot be told from these tables. The March
    2020 COVID-19 state of alarm also moved 82% of provinces at once.
- **Supervised cases** rose from 2,135 (November 2024) to a peak of 7,783 on 30 June 2025, the day the 2025 protocol took
  effect, then fell to 4,491 by September 2026.
- **The institutional gap is recent.**
  - *Opening.* The Guardia Civil and the Policía Nacional rated a similar share of their active cases medium or
    above in February 2020 (11.8% against 10.5%). The gap opened to about 10 points between 2021 and mid-2023,
    under the same 2019 protocol, and has stayed there.
  - *The national rise.* From March 2021 to June 2023 the national share rose from 10.8% to 16.8%. Without the
    Guardia Civil it rose only from 9.9% to 11.7%.
  - *Weight.* By September 2026 the Guardia Civil held 45% of active cases and 65% of the medium-or-above ones.
- **What this suggests for administrative discretion.**
  - *Reforms reorganise categories.* The reforms show up as reorganisations of categories and statuses more than
    as changes in how many cases sit at the higher levels.
  - *Divergence under one instrument.* The largest sustained divergence happened between institutions using the
    same instrument under the same rules. That is where discretion, training and case mix would show.
  - *Officer discretion.* The officer's power to raise the automatic result is the discretion the 2025 protocol
    formalises (upward only, Instrucción 1/2025 §3.8 and §6.2). It is not published.

None of this is causal, and none of it measures officer behaviour.

## Questions these data hand to the interviews

1. What changed centrally in November 2024 that moved every province and both state forces by the same amount in one
   month? Was it the software, the scoring, the re-assessment rules, or how the figures are compiled?
2. What changed in the Guardia Civil's use of VioGén between 2021 and 2023, when its medium-or-above share doubled
   (12.2% to 24.0%) while the Policía Nacional's rose by about three points (10.1% to 13.4%)?
3. How often do officers raise the automatic level under §3.8 and §6.2, and is this recorded anywhere?

## What the data cannot say

These are stocks, not individual trajectories. They do not show:
- which cases were reclassified;
- how often officers raised a level;
- what protection was delivered;
- whether differences between institutions reflect practice or case mix.
