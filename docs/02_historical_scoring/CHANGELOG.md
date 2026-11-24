# Changelog: Module 2, historical VPR4.0 laboratory

File names below follow the original release. The [component guide](README.md) links to their locations in this repository.

## Version 2 (11 November 2026): source-verified

Version 1 was built from a third-party transcription because the thesis PDF could not be downloaded. Version 2 is checked against the thesis itself: López Ossorio (2016), UAM repository, MD5 `5d111ff6d9a6717d14f2c265544406f1`, which matches the checksum published by the repository. The version 1 indicator catalogue is kept in `version1_data/` for the audit.

### Source corrections (catalogue `vpr4_0_annex1_indicators.csv`)

All 63 weights, all 13 critical flags and all page numbers in version 1 were correct. The errors were structural, and the 77.019 total could not detect them.

| Annex 1 row | Version 1 | Version 2 | Effect on scores |
|---|---|---|---|
| 10 | `I5_weapons_general`, indicator I5 | `F02_weapons_used`, no I-number (the factor-2 question) | none (renamed) |
| 15 | `I7_threats_general`, indicator I7 | `F03_threats`, no I-number (the factor-3 question) | none (renamed) |
| 38 | `I17_criminal_history`, indicator I17 | `F08_criminal_record`, no I-number (the factor-8 question). I17 is row 39, "previous breaches" | none (renamed) |
| 40, 41 | I18 and I19 had no parent | parent `F08_criminal_record` (Annex 5 p. 301: asked "en caso afirmativo") | I18 alone: **4.012** (was 1.870); I19 alone: **3.713** (was 1.571) |
| 18 | label "Amenazas económicas" | "Amenazas económicas por parte del agresor" | none |
| 20 | label "... de la víctima" | "... de la víctima por parte del agresor" | none |
| all | invented thematic "section" column | source factors F01–F12, the factor question in Spanish, and the four categories of the form | none |

New columns: `row`, `page`, `factor`, `factor_question_es`, `category`, `category_es`, `weight_as_printed`, `response_type` (gate_question / indicator / severity_option / subtype_checkbox / sub_question), `critical_table1_number`, `structure_evidence` (the Annex 2 or 5 passage behind each parent link).

Old codes are still accepted (`OLD_CODE_ALIASES` in the engine).

### Engine (`vpr4_historical.py`)

- **Unknown answers.** Version 1 refused to score any form with a missing answer. Version 2 accepts *Sí / No / No se sabe* (True / False / None) and returns `score_min` / `score_max` over every completion. A level is given only when nothing is unknown; `category_robust_to_unknowns` says whether both ends agree.
- **Form logic.** `normalize()` applies the documented "en caso afirmativo" rule in both directions. A sub-item answered Sí sets its parent to Sí. A parent answered No closes its sub-items. A Sí sub-item under a No parent is rejected.
- **Boundaries.** `category(score, upper_inclusive=True)` takes the alternative reading of "hasta" as an option. `threshold_attainability()` and `exact_cutoff_examples()` show that every cut-off can be scored exactly. The version 1 docstring said otherwise.
- **Procedure (Instrucción 7/2016, thesis Annex 6).**
  - `apply_officer_override()`: rule 1.5, the level can be raised only.
  - `procedural_consequences()`: rules 1.6, 1.8 and 2.1.
- **Exact structural analysis.** `attainable_scores()` returns 64,879 scores. `category_extremes()` gives the fewest and most indicators per level. `indicator_count_example(level, most)` gives a concrete form for each of those extremes. `source_integrity()` gains factor-question rows, critical numbers and the critical weight total (43.252).
- `compare_cases()` now refuses incomplete forms rather than comparing partial sums.

### Research findings changed by the verification

- "22 facts and still no apreciado, 9.069" (earlier project notes) is superseded. The exact maximum is **25 of 39 indicators** (27 counting the weighted factor questions). The example form scores 9.165.
- New: **9 indicators** (12 facts, 18 rows) are enough for *extremo*, the "few heavy indicators" route of p. 192.
- New: *bajo* can be reached with one I-numbered indicator, because the weighted factor questions F02 and F08 have no I-number.
- The weights' criterion is now stated precisely. They are odds ratios for a new police report against the same aggressor within **four** months (p. 191), not lethality.
- Knife versus firearm. Version 2 now explains the 4.000 by the expert homicide-screening list (p. 192), and the 0 by the 30-case frequency in the VPR2015 study (Table 1, p. 163).

### Interface, notebook, tests

- `interactive_app.py` was rewritten:
  - Tri-state radios for all 63 rows, grouped by the form's categories and factors.
  - Sub-items are disabled until their parent is not No.
  - The score range is shown under unknowns.
  - Override selector offering only levels at or above the automatic one.
  - Judicial-measure checkbox, procedural consequences, firearm/knife panel, and a table of structural extremes.
  - The app was run headless (`streamlit.testing.v1.AppTest`) and in Chromium at desktop and phone widths, with no console errors.
- The notebook was rebuilt into 11 sections, covering source verification, structure, thresholds, firearm/knife, zero weights, many-indicators, unknowns, the four layers of discretion, the design counterfactual and the VioGén 2 bridge.
  - It is executed in an empty folder, where it writes its own engine and catalogue. Its 14 code cells ran with 0 errors.
  - The ipywidgets cell was tested headlessly, with ipywidgets 8.1.9.
- Tests: from 9 to **52** (4 files):
  - engine: 37;
  - interface (AppTest): 6;
  - source: 5, one of which re-reads the PDF when `VPR4_THESIS_PDF` is set;
  - package consistency: 4. These check that the notebook embeds the current engine and catalogue and ran without errors, and that the matrix covers all 63 rows.
- New `tools/annex1_transcription.py` (the hand transcription and the PDF check) and `tools/build_verification_matrix.py`.
- Figures redrawn from the verified table. There is a new figure 05, indicators per level, and figure 04 is now by category of the form.

### New documents

`SOURCE_VERIFICATION_MATRIX.csv`, `UNRESOLVED_LIMITATIONS.md`, `CLASSROOM_DEMO_SCRIPT.md`, `requirements.txt`, `source_evidence/` (page images of every passage cited).

## Version 1

The first package (9 tests, standalone notebook, Streamlit code not run) was built from a text transcription. Its indicator catalogue is kept in `version1_data/`, because the verification matrix audits it row by row. `VERIFICATION_STATUS.md` answers the version 1 review checklist item by item.
