# Methods and limitations

Module 1 of Group D's investigation of VioGén 2 for *Data and Algorithms for Public Policy* (Sciences Po).
The aim is to describe how the published risk classifications change across the 2025 reform, as evidence
about where the system places administrative discretion. The series starts in January 2018, so that the
previous protocol change (March 2019) can serve as a benchmark. This is **not** an audit of predictive accuracy
or of legal compliance.

## 1. Sources

**Main source.** The *Boletín estadístico mensual* (BEM) published by the Delegación del Gobierno contra la Violencia
de Género. URLs follow the pattern
`https://violenciagenero.igualdad.gob.es/wp-content/uploads/BEM_<Mes>_<Año>.pdf`.

**Bulletins used.**
- Downloaded: all **105 bulletins from January 2018 to September 2026**, on 10–11 November 2026.
- Missing: the October 2026 bulletin did not exist yet (HTTP 404).
- Logged in [`source_manifest.csv`](../../data/01_statistics/source_manifest.csv): each file's SHA-256 and page numbers.
- Kept in [`bulletins/`](../../sources/01_statistics/bulletins/): the two VioGén table pages of every bulletin, as evidence.

**Tables used from each bulletin.**
1. *Casos de violencia de género. Distribución territorial*, for all countries of birth and all ages. This gives one row per
   province, autonomous community and city, plus the national TOTAL.
2. *Casos de violencia de género. Distribución por cuerpos policiales*, which gives one row per police
   institution plus the TOTAL. This table is first printed in the **February 2020** bulletin.

Each row reports cases by risk level, then active, supervised, inactive and total cases, then victims.
A *case* links one victim to one aggressor; it is not a unique woman. All values are end-of-month stocks.

**Other sources used.**
- **June 2025 police institutions.** This table is not printed in the June 2025 bulletin. The earlier manual transcription
  of the VioGén portal PDF is kept. The portal is not reachable from this environment, so the PDF was not
  re-read here. The transcription reconciles exactly with the June 2025 bulletin's national TOTAL on all five
  risk levels and on active cases.
- **October 2026 national totals.** These come only from a press relay of Interior figures (Europa Press,
  3 November 2026), as supplied in the reference. They are **not verified** against an official PDF. The
  VioGén portal's listing disallows automated access, and this was respected.

**Rule texts used to date the breaks.** These are used for dating only, not as data.
- **Instrucción 7/2016 and Instrucción 4/2019 of the SES.** The bulletins themselves cite both.
  - *7/2016.* The 2018 bulletins cite Instrucción 7/2016 of 8 July 2016.
  - *4/2019.* Later bulletins cite Instrucción 4/2019, "con entrada en vigor en fecha 13 de marzo de 2019", as
    the protocol under which cases were assessed until the 2025 protocol.
- **Instrucción 1/2025 of the Secretaría de Estado de Seguridad (Protocolo 2025).**
  - *Dates.* Signed 15 January 2025, effective from 30 June 2025 (clause *Quinta*).
  - *Levels.* It removes "No apreciado" ("desaparece el Nivel de riesgo No Apreciado").
  - *Supervised cases.* It creates them in §7.4, with entry criteria (e.g. a medium-or-above rating in the last
    three months) and a minimum three-month period.
  - *Officer discretion.* It lets the officer change the automatic result **upwards only** (§3.8 for the initial
    assessment, §6.2 for re-assessments).
  - *Copy read.* A copy hosted by a third party (academia-geopol.es), not an official gazette.
- **Moncloa / Interior press note, 15 January 2025.** It announces VioGén 2 and says the platform had been tested for
  seven months in Policía Nacional and Guardia Civil stations. This is an official source.
- **Instrucción 2/2024 (SES, March 2024).** It created "inactivación supervisada" and restricted inactivation. This is known here
  **only from press reports** (La Marea, 11 March 2024; Ara, 8 March 2024). The instruction text was not obtained.

## 2. Extraction

There are two routes into the same parser ([`viogen_extract.py`](../../scripts/01_statistics/viogen_extract.py)).

**Text layer, January 2018 – February 2026, except the image months below.** Words and their coordinates are read with
PyMuPDF and grouped into printed lines. Numbers are right-aligned, so column positions are learned by
clustering the right edges of numeric cells.

The earlier extractor passed only a synthetic test. It failed on real files for four reasons, now fixed:
- **Letter fragments.** In 2023–24 the text layer splits names into fragments ("G alicia", "T O T AL"). Labels
  are now matched after removing spaces and accents.
- **Renamed institutions.** Police institutions are printed under new names from November 2024 ("Cuerpo
  Nacional de Policía" became "Policía Nacional", "PL Madrid" became "PL Comunidad de Madrid"). An alias table
  harmonises the names and keeps the printed label.
- **Inverted names and a source typo.** The November 2024 bulletin prints names in reverse order ("Palmas, Las",
  "Rioja La") and contains a typo in the source itself ("Pincipado de Asturias").
- **New institution rows.** From December 2024, small "U.A. de *region*" rows appear. They are accepted as
  institutions in their own right.

The 2018–2019 bulletins needed two further adjustments:
- **Older name.** They print "Islas Baleares".
- **Extra columns in 2018.** The 2018 tables print two columns after VÍCTIMAS ("PSP Gestión desde 17/08/2016" and
  "3A desde 15/02/2017"). These are outside the VioGén case table and are ignored.

**Image tables in 2020–2021 (12 bulletins).** The bulletins for June, July, September, October and December 2020 and
for March–June and August–October 2021 print one or both VioGén tables as images. Some tables are split into two
stacked images, which are joined before reading.
- *Territorial tables: not extracted.* One attempt (December 2020) took about 23 minutes and did not reconcile:
  two region labels were unreadable and several provinces did not sum. These months therefore have **no regional or
  provincial rows**.
- *Police-institution tables: three attempted, one used.*
  - *December 2020:* read with the OCR method described next. It reconciled and is used.
  - *June and July 2020:* attempted, but failed their checks. In the bold TOTAL row, 5 and 9 were confused; in June
    the printed date was also misread.
  - *The other seven:* September and October 2020, and April, May, August, September and October 2021 were not
    attempted.
  - *Text-layer cases:* the police tables of March and June 2021 have a text layer and reconcile.
- *National row from the police table.* Where the police-institution table reconciles, its TOTAL row is used as
  the national row. It is the same national total: in all 67 months where both tables reconcile, the two TOTAL
  rows are identical in every column, victims included.

**Embedded images, March–September 2026 (7 bulletins), and the 2020–2021 police tables.** From March 2026 the
VioGén tables are images with no text layer. Each image is read at its native resolution (about 180–196 dpi):
1. The grid is detected morphologically. The shaded TOTAL and VÍCTIMAS columns have no drawn borders, so
   their boundaries are placed at background-shade steps.
2. Every cell is read separately with Tesseract, using digits only for numeric cells and several image
   preparations, keeping the majority reading.
3. Labels are accepted only when they match a known unit name.
4. If a row then fails its own arithmetic, each of its cells is re-read in up to 80 ways (four scales × five
   binarisations × four Tesseract modes). The three fixed-cut-off binarisations were added after single "9"s
   were consistently read as "8".
5. The row is corrected only if **exactly one** combination of the values OCR actually produced satisfies the
   row's identities. Where several do, the combination must also make the parent row add up (province to region,
   region or institution to TOTAL), using siblings that pass. This is repeated until no further row resolves, so
   a row can be settled once its siblings have been repaired.
6. A level or supervised cell where OCR finds no digits may enter that combination as 0, since the tables print
   zero cells as blanks or "0". This is accepted only when the row and its parent then both add up.

No value is typed in by hand. Every corrected cell is listed in [`extraction_errors.csv`](../../data/01_statistics/extraction_errors.csv), with its first
reading and the constraint that settled it.

**One printed artefact.** In January and May 2025 the institution table prints the active-cases TOTAL as
"1E+05" (spreadsheet scientific notation). That single cell is taken from the territorial table's TOTAL in
the same bulletin and on the same date, and the substitution is logged.

## 3. Validation (every month, every table)

[`validation_report.csv`](../../data/01_statistics/validation_report.csv) records, for each month:
1. **Every row adds up.** Risk levels sum to active cases, and active + supervised + inactive = total.
2. **Provinces add up to their region.** This holds in every case column for each multi-province community.
3. **Regions add up to the national TOTAL.** The 19 rows, including Catalonia and the Basque Country, which
   contribute inactive cases only, sum to the TOTAL in every case column.
4. **Police institutions add up to the TOTAL** in every case column.
5. **The two tables agree.** The territorial TOTAL equals the police-institution TOTAL.
6. **The printed date is the month end** ("Datos a dd/mm/aaaa"). A table whose date is not read as the month end
   is not used.
7. **The national row matches the reference series**, with every difference recorded in [`national_changelog.csv`](../../data/01_statistics/national_changelog.csv).

A table enters the panels only if all its checks pass. The victims column is not part of any identity, so
for OCR'd tables it is the majority OCR reading and is less certain than the case columns.

**Result, January 2018 – October 2026.** 713 checks pass.
- *Not available (45).* The police table is not printed before February 2020 or in June 2025, image tables were not
  extracted, and the October 2026 bulletin does not exist yet.
- *Corrected (1).* The reference's January 2026 values are replaced by the official ones.
- *FAIL (8).* These belong to the three OCR'd tables that did not reconcile: the June and July 2020 police tables
  and the December 2020 territorial table. All three are excluded.
- *Coverage.*
  - National: 96 of 106 months.
  - Regional and provincial: 93 months.
  - Police institutions: 70 directly extracted months and one additional month (June 2025) from the retained portal transcription.
  - Month by month: [`month_by_month_coverage.csv`](../../data/01_statistics/month_by_month_coverage.csv).

**OCR'd tables: 27 rows were re-read** (21 in March–September 2026, 6 in the December 2020 police table). The
changes are typical digit confusions (5↔9, 8↔9, 1↔7) and blank cells resolved to the value printed.
- *Checked by eye.* Every one of them is shown in [`ocr_checks/`](../../sources/01_statistics/ocr_checks/) as printed in the bulletin, next to the accepted values,
  and all 27 were checked by eye.
- *Repeatable.* Six months reconciled under two OCR runs with different candidate settings, and their tables
  were identical, including victims. June 2026 reconciled only after the fixed-cut-off readings were added.
- *External check.* The 2026 OCR national TOTAL rows match the Interior figures relayed in the press that the
  reference series had used, in all seven months.
- *Internal check for December 2020.* There the territorial table did not reconcile, but its printed TOTAL row (read
  by eye from the image) equals the police-institution TOTAL used.

## 4. Coding decisions

**"No apreciado" (no appreciable risk).** This is a real category up to June 2025. From July 2025 it is **not
applicable**, recorded as blank (NaN), never 0.

**"Supervisados".** This column is first printed in the November 2024 bulletin, while the five old levels were still in use.
Before then it is blank (not printed).
- *Layout.* From November 2024 to June 2025 it sits under an "INACTIVOS" header group. From July 2025 it is a column of its own.
- *Definition.* The bulletin glossary defines it from July 2025 onwards (e.g. BEM July 2025, p. 45): "a temporary phase of
  special follow-up before definitive inactivation", for cases of high complexity or qualified risk.
- *Counting.* Supervised cases are not part of the active count; total = active + supervised + inactive.

**Protocol periods.**
- *2016 protocol (Instrucción 7/2016):* to February 2019.
- *2019 protocol (Instrucción 4/2019, in force 13 March 2019):* March 2019 to October 2024. The 31 March 2019
  stock is the first taken after the change.
- *Transition:* November 2024 – June 2025, with the old levels plus the supervised column.
- *2025 protocol:* from July 2025.

The 30 June 2025 table, the first day of the 2025 protocol, still uses the five old levels.

**Catalonia and the Basque Country.** Their police forces (Mossos d'Esquadra, Ertzaintza) do not publish
VioGén risk levels.
- *Level and active cells* are blank (NaN), with `risk_levels_reported = False`. From February 2026 the
  bulletins print 0 in those cells (before that they are blank); these are also recorded as *not reported*,
  not as observed zeros.
- *Inactive counts.* According to the bulletin's footnote, the inactive counts printed for these two
  communities are victims recorded in VioGén elsewhere in Spain who now live there.

**Disaggregations are kept separate**, to avoid double counting.
- *Regional panel:* 17 communities and cities that publish levels, plus the 2 that do not.
- *Provincial panel:* 45 province-equivalents (36 provinces of multi-province communities, 7 single-province
  communities, Ceuta and Melilla), plus 7 non-publishing provinces.
- *Police panel:* institutions as printed each month, from February 2020. The number varies (21–36) and
  nothing is padded.

**`medium_plus`** is medium + high + extreme, as a share of active cases. It is the most comparable grouping
across the protocol changes, but it is not a constant construct (see §5).

**Break test (notebook §3, chart 08).** For each month, the share of the 45 province-equivalents that
publish risk levels in which the medium-or-above share fell (or the "No apreciado" share rose) compared
with the previous month. Only pairs of consecutive extracted months count. In an ordinary month about half
of the provinces move each way.

## 5. Limitations that bound every claim

- **Stocks, not flows.** Two month-end stocks cannot show which cases were reclassified. Counts also move with
  new cases, closures, inactivations and re-assessments.
- **The algorithm changed too.** The 2025 protocol introduced new indicators and recalibrated algorithms that are
  not published. A similar medium-or-above share before and after does not mean the same women hold the same
  levels.
- **Classification is not protection.** The tables report risk levels, not the protection measures applied or
  delivered. Protocol obligations attached to a level are not observed service delivery.
- **Territories and institutions are not comparable on behaviour.** They serve different populations,
  territories and case mixes. Differences in shares do not measure officer discretion, overrides or bias.
- **Coverage.** Catalonia and the Basque Country are outside the risk-level figures, so the "national" figures
  cover the VioGén risk-level perimeter only.
- **What is not observable.** Officers' upward adjustments (§3.8 and §6.2 of the 2025 protocol) are where
  discretion formally sits, and they are not published. Neither are the 2025 weights and cut-offs, nor the
  outcomes for women. The dataset does not reconstruct any of these.
- **The November 2024 break.** The largest and most synchronised one-month change in the medium-or-above share
  between 2018 and 2026 occurs in November 2024.
  - *Format change too.* The bulletin's format changed that month: new institution names, inverted place names
    and the *Supervisados* column.
  - *What the test shows.* The break test (notebook §3, chart 08) shows the change was system-wide.
  - *What it cannot show.* It cannot show which system-wide change it was. A scoring or procedural change applied
    centrally and a change in how the statistics were compiled look the same in these tables. An exogenous shock
    can also move every province at once, as the March 2020 COVID-19 state of alarm did.
- **2020–2021 gaps.** Twelve months have no regional or provincial rows (territorial image tables not
  extracted), and some months have no national row (police table not reconciled; see the coverage file).
  Comparisons across these gaps use only pairs of consecutive extracted months.
- **OCR'd tables (March–September 2026; December 2020 police table).** Case columns are verified by arithmetic.
  Victims counts are OCR readings without an arithmetic check.
- **Institutions across 2020–2026.** The Guardia Civil–Policía Nacional gap opened between 2021 and mid-2023, under the
  same protocol, and the Guardia Civil's active caseload doubled over 2020–2026. The published table cannot split a force by
  province, so the gap cannot be separated from territory or case mix.
- **October 2026** rests on a press relay and is unverified.
