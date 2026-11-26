# VioGén investigation · Module 2 (version 2): the historical VPR4.0 scoring laboratory

**Research question.** How does Spain's VioGén system distribute discretion among the police officers who record information, the designers who build the algorithm, and the procedural rules that attach consequences to a risk level?

**What this module is.** A source-verified reconstruction of the **VPR4.0** police risk form as designed in López Ossorio's 2016 doctoral thesis (UAM). Every weight, label, critical flag, cut-off and parent–child link was checked against the thesis PDF.

> **Not VioGén 2.** This is a historical model. VioGén 2 has been in force since 30 June 2025, and its weights and cut-offs are not public. Nothing here explains a 2025–2026 classification, a Module 1 trend, or a police decision. Every case is fictitious, and scores are additive points, not probabilities or measures of danger.

## Start here

| If you want to… | Open |
|---|---|
| Read the argument with the evidence | [`VioGen_Module2_Historical_Research_Lab.ipynb`](../../scripts/02_historical_scoring/VioGen_Module2_Historical_Research_Lab.ipynb). It is standalone (the engine and catalogue are embedded), so it can be uploaded on its own to Google Colab and run with *Run all*. |
| Click through forms yourself | `pip install -r requirements.txt`, then `streamlit run scripts/02_historical_scoring/interactive_app.py` |
| Check a number against the thesis | [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/02_historical_scoring/SOURCE_VERIFICATION_MATRIX.csv) and the page images in [`02_historical_scoring/`](../../sources/02_historical_scoring/) |
| Know what is still uncertain | [`UNRESOLVED_LIMITATIONS.md`](../../docs/02_historical_scoring/UNRESOLVED_LIMITATIONS.md) (plain language) and [`METHODS_AND_LIMITATIONS.md`](../../docs/02_historical_scoring/METHODS_AND_LIMITATIONS.md) (technical) |
| See what changed since version 1 | [`CHANGELOG.md`](../../docs/02_historical_scoring/CHANGELOG.md) and [`VERIFICATION_STATUS.md`](../../docs/02_historical_scoring/VERIFICATION_STATUS.md) |

## Main findings (historical rule, fictitious forms)

1. **The table is right, but version 1's structure was not.**
   - All 63 weights matched the thesis. Three rows had been given indicator numbers they do not have; they are actually the gate questions of factors 2, 3 and 8.
   - I18 and I19 were missing their parent question. This changes scores: a record of aggression against others alone is 4.012, not 1.870.
   - The 77.019 total could not detect any of this.
2. **Firearm used: 1.533. Knife used: 5.533.**
   - The knife is one of 13 expert-weighted "critical" indicators for a homicide screening, and its weight was doubled (p. 192).
   - Firearm use appeared in 30 of 6,613 cases and was not significant for the criterion: *a new police report within months*, not lethality (p. 163, p. 191).
   - The difference reflects design and data, not danger.
3. **31 of 63 recorded rows weigh zero**, among them pregnancy, disability, dependent children and economic dependence. They were kept to collect information (p. 196).
4. **Two routes to a level** (p. 192), computed exactly over every consistent form:
   - a form can hold **25 of 39 indicators** and still be *no apreciado* (example score 9.165);
   - **9 indicators** can be enough for *extremo*.

   These are logical possibilities under the rule, not observed cases.
5. **Input coding moves levels.** The same fictitious account (stalking after separation) shows this:
   - 8.226, *no apreciado*, when the insults are not recorded and the push is coded *leve*;
   - 9.654 or 10.226, *bajo*, when the insults are recorded or the push is coded *grave*. Annex 5 tells officers to choose the more severe level when in doubt.
6. **The procedure fixes the direction of discretion.**
   - Officers may raise the automatic level, never lower it (Instrucción 7/2016, rule 1.5).
   - Officers may inactivate a *no apreciado* case unless a judicial measure is in force (rule 1.6).
7. **Designers drew the cut-offs partly for workload.** Levels should hold proportions "asumibles desde el punto de vista de la seguridad" (p. 194).
8. **The boundary reading matters.** Every cut-off can be scored exactly, and the thesis does not say whether "hasta 9.535" includes 9.535.

## Files

| File | Purpose |
|---|---|
| [`vpr4_0_annex1_indicators.csv`](../../data/02_historical_scoring/vpr4_0_annex1_indicators.csv) | Verified Annex 1 catalogue: 63 rows, with factor, category, parent, response type, critical number and evidence for each link |
| [`vpr4_historical.py`](../../scripts/02_historical_scoring/vpr4_historical.py) | Scoring engine. Handles unknown answers as bounds, applies the form logic, the cut-offs (both boundary readings) and the procedural rules, and runs the exact structural analysis |
| [`interactive_app.py`](../../scripts/02_historical_scoring/interactive_app.py) | Streamlit interface: tri-state answers for all 63 rows, live result, override and procedure panel |
| [`VioGen_Module2_Historical_Research_Lab.ipynb`](../../scripts/02_historical_scoring/VioGen_Module2_Historical_Research_Lab.ipynb) | Executed, standalone notebook in 11 sections; [`make_notebook.py`](../../scripts/02_historical_scoring/make_notebook.py) rebuilds it |
| [`hypothetical_scenarios.csv`](../../data/02_historical_scoring/hypothetical_scenarios.csv) / `.json` | 17 fictitious worked examples; [`demo_scenarios.py`](../../scripts/02_historical_scoring/demo_scenarios.py) rebuilds them |
| [`02_historical_scoring/`](../../figures/02_historical_scoring/) | Five research figures generated by [`generate_figures.py`](../../scripts/02_historical_scoring/generate_figures.py) |
| [`tests/`](../../scripts/02_historical_scoring/tests/) | 52 tests: engine, interface (AppTest), source (with PDF re-check), package consistency |
| [`tools/`](../../scripts/02_historical_scoring/tools/) | Annex 1 transcription, PDF verification and the verification matrix builder |
| [`build_catalog.py`](../../scripts/02_historical_scoring/build_catalog.py) | Builds the catalogue from the transcription |
| [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/02_historical_scoring/SOURCE_VERIFICATION_MATRIX.csv) | 96 lines: one per Annex 1 row plus 33 method, threshold, form, procedure, evidence and computed claims, each with a status |
| [`SOURCE_LEDGER.csv`](../../data/02_historical_scoring/SOURCE_LEDGER.csv) | Sources used and what each supports |
| [`02_historical_scoring/`](../../sources/02_historical_scoring/) | Page images of every thesis passage cited. The thesis itself is not redistributed. |
| [`version1_data/`](../../data/02_historical_scoring/version1_data/) | The version 1 indicator catalogue, kept because [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/02_historical_scoring/SOURCE_VERIFICATION_MATRIX.csv) audits it row by row |
| [`requirements.txt`](../../scripts/02_historical_scoring/requirements.txt), [`FILE_MANIFEST.csv`](../../docs/02_historical_scoring/FILE_MANIFEST.csv) | Tested versions; checksums of every file |

## Verification recorded for the source release

- **Tests.** `VPR4_THESIS_PDF=<thesis.pdf> python -m pytest scripts/02_historical_scoring/tests/ -q` gives 52 passed. Without the PDF, the one PDF test is skipped.
- **Notebook.** Executed in an empty folder, where it wrote its own engine and catalogue. 14 code cells, 0 errors. The ipywidgets cell was exercised headlessly.
- **App.** Tested with Streamlit AppTest. Clicking I11, I36 and I39 gives 4.940 → 8.226 → 11.056 (*bajo*). Setting I9 to "No se sabe" shows the range 11.056–14.596.
- **Reproducibility.** The catalogue and scenarios rebuild byte-identical.
- **Clean environment.** A fresh virtual environment built from [`requirements.txt`](../../scripts/02_historical_scoring/requirements.txt) (Python 3.13, pandas 3.1.1, pytest 9.2.0) gives 52 tests passed. The notebook executes there with 0 errors, and the figures rebuild.

## How it connects to the other modules

- **Module 1** (completed) reports the observed 2018–2026 distribution of risk levels.
- **Module 2** (this one) shows, on the only version whose arithmetic is public, *the kinds of choices* an actuarial police form requires, and who makes each one.
- **Module 3** examines the procedural rules of VioGén 2 (Instrucción 1/2025), without assuming the 2016 numbers still apply.

## Source

Juan José López Ossorio (2016; defended 2017), *Construcción y validación de los formularios de valoración policial del riesgo de reincidencia y violencia grave contra la pareja (VPR4.0–VPER4.0) del Ministerio del Interior de España*, doctoral thesis, Universidad Autónoma de Madrid.

- PDF: https://repositorio.uam.es/server/api/core/bitstreams/09c11ef0-a544-439a-a623-4e492db41610/content
- MD5 `5d111ff6d9a6717d14f2c265544406f1`; 336 pages.
