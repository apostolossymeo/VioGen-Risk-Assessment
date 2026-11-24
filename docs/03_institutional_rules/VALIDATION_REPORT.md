# Validation report: Module 3, version 2

This report covers what was checked, how it was checked, what changed as a result, and what remains unverified. Machine-readable versions:
- claim by claim: [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/03_institutional_rules/SOURCE_VERIFICATION_MATRIX.csv);
- per clause: [`protocol_clauses.csv`](../../data/03_institutional_rules/protocol_clauses.csv).

## 1. Sources and provenance

| Source | Copy used | Pages | Checks done | Residual doubt |
|---|---|---|---|---|
| Instrucción 4/2019 | Official site, violenciagenero.igualdad.gob.es | 23, scanned, no text layer | sha256 `238f9010…`; printed page = PDF page; signed 6 March 2019, effective 13 March 2019 | Text comes from Tesseract OCR (spa, 200 dpi). Every quote was also read against the page image. |
| Instrucción 1/2025 | mundopolicial.net. academia-geopol.es is byte-identical (sha256 `08e6c0ec…`); avefor.com is unstamped and text-identical (6 whitespace differences) | 52, text layer | CSV `GEN-61b6-a6bd-ca9d-fb9e-612a-3074-2815-598b` printed on all 52 pages (tested); signer and date (15/01/2025) checked; effective 30 June 2025 | No government host found. The CSV was **not** checked on the official verification site, which is behind a captcha. |
| Instrucción 5/2021 (Protocolo Cero) | Official site, violenciagenero.igualdad.gob.es | text layer | sha256 `1eb535a5…`; dated 27 July 2021 (DGVG Observatory report) | none |
| 8/2021, 11/2022, 1/2023, 2/2024 | Press and official summaries only | n/a | Graded B (La Moncloa) or C (press or police academy) | Primary texts not obtained |
| 7/2019, 12/2018 | Titles only | n/a | Grade D | Content not established |

The three primary PDFs are in [`primary/`](../../sources/03_institutional_rules/primary/) and their text in [`text/`](../../sources/03_institutional_rules/text/). Press texts are not redistributed; they are cited by URL in [`source_ledger.csv`](../../data/03_institutional_rules/source_ledger.csv).

## 2. Clause and annex verification

**Clauses.** 128 clauses were coded (82 from 2025, 43 from 2019, 3 from 5/2021). Each one stores:
- the exact Spanish excerpt;
- the section;
- the declared page.

[`quote_check.py`](../../scripts/03_institutional_rules/src/quote_check.py) finds every excerpt again **on its declared page**:
- 2025 and 5/2021: exact match against the text layer (85 clauses).
- 2019: fuzzy token match against the OCR (43 clauses). The threshold is a SequenceMatcher ratio of at least 0.90 over sliding windows. After normalisation, all 43 scored 1.00.

All 128 pass. The test suite repeats this check on every run.

**Annexes.**
- Both annexes were transcribed in full and checked against the page images: 2019 Anexo 1 pp. 15–18 (26 items) and 2025 Annex II pp. 37–40 (41 items).
- Each item carries:
  - level and block;
  - modality: mandatory, conditional on a fact, conditional on judgement, advice, request to another authority, resource-dependent, or discretionary;
  - decision owner;
  - any condition.
- All 67 items are found again on their declared pages.
- The 16 changes between the annexes ([`protection_measure_changes.csv`](../../data/03_institutional_rules/protection_measure_changes.csv)) are keyed to these item IDs.

**Other checks on the 2025 text.**
- Derogation list on p. 4 (tested).
- 5/2021 not derogated (pp. 9, 10, 13 and 29 refer to it as current).
- Two absence checks: no clause in §7.1 requires communicating an ordinary inactivation to the court, and no clause requires recording the reasons for an upward override.

## 3. Audit of the version-1 package

Every v1 claim is a row in the matrix.

| v1 element | Verified | Qualified | Corrected | Other |
|---|---|---|---|---|
| 35 decision-rule records | 22 | 7 | 6 | n/a |
| 16 protocol comparisons | 10 | 3 | 3 | n/a |
| 13 selected measures | 10 | 3 | 0 | n/a |
| 7 initial hypotheses (H1–H7) | 6 | 1 | 0 | n/a |
| 4 provenance statements | 1 | 2 | 0 | 1 superseded |

The substantive corrections:
1. **The 2019 7-day first-VPER cap covers bajo and above**, not just medio and above (§5.3, p. 12).
2. **The special-relevance clause is a minimum wait** of at least 7 days, not an exception to the maximum. This holds in 2019 (§5.5) and 2025 (§4.5).
3. **The 2025 ordinary-inactivation premise is a positive finding** ("de manera fehaciente", §7.1 p. 18), not "professional assessment supports it".
4. **Supervised cases come from Instrucción 2/2024.** v1 said "2022/2024", but 11/2022 concerns resistant cases.
5. **Ex officio assessment without a complaint is already in the 2019 text** (Cuestiones preliminares C, p. 5). Protocolo Cero (2021) added the first-contact procedure.
6. **Page ranges.** The 2019 annex is pp. 15–18, not 15–19 (p. 19 begins Anexo 2). 2025 §7.1 is pp. 17–18.

20 new rule records were added, covering stages v1 did not code: reactivation, exceptional inactivation, supervision, special relevance, persistent aggressors, resistant cases, and court reports. 34 comparison topics were each given an attribution and an evidence grade (A 9, B 9, C 5, D 11).

## 4. Decision-rule engine

[`decision_rules.py`](../../scripts/03_institutional_rules/src/decision_rules.py) returns, for each function:
- a status;
- the clause IDs it relies on;
- where relevant, a deadline with its unit and bound.

Statuses: `applies`, `not_applicable`, `cannot_determine`, `not_stated`, `requires_judgement`, `eligible`, `insufficient_conditions`, `not_eligible`, `routes_to_supervision`.

Unknown premises stay unknown (`None` gives `cannot_determine`). The engine never infers a deadline whose prerequisites are absent.

**Pathway audit.** v1 and v2 were compared on all 50 abstract pathways ([`pathway_audit_v1_vs_v2.csv`](../../data/03_institutional_rules/pathway_audit_v1_vs_v2.csv)). Deadlines agree in all 50. Inactivation semantics agree in 47. The other 3 are v1 errors:
- **2019, no apreciado, no judicial measures:** v1 assumed the evaluator-judgement premise (§2.6.ii) was met.
- **2019, low assigned or kept, no judicial measures (2 pathways):** v1 treated unknown premises as unmet.

The engine models only the formal rules. It does not score risk and does not reconstruct VioGén-2.

## 5. Automated tests and notebook

- `python3 -m pytest scripts/03_institutional_rules/tests -q` gives **275 passed**: 52 test functions, many parametrised over every clause, measure, record and page.
  - [`test_rules.py`](../../scripts/03_institutional_rules/tests/test_rules.py) (34 functions): deadlines, bounds, court-notification rules, inactivation routes, supervision, reactivation, the protection floor, and the upward-only override.
  - [`test_data_integrity.py`](../../scripts/03_institutional_rules/tests/test_data_integrity.py) (14 functions):
    - every clause and measure is found on its page;
    - PDF hashes; the derogation list; CSV stamps on 52 pages;
    - controlled vocabularies;
    - every v1 record appears in the matrix;
    - B and C grades carry evidence;
    - export schema;
    - no root duplicates.
  - [`test_reproducibility.py`](../../scripts/03_institutional_rules/tests/test_reproducibility.py) (4 functions): the build is byte-deterministic; the notebook embeds the current `src`; the notebook is executed without errors; the figures exist.
- The notebook was rebuilt and executed in a clean directory: 29 cells, 15 code cells, 0 errors.
- Fresh environment: see §7.

## 6. What could not be established

1. **Official validation of the 2025 CSV.** Manual step: enter the CSV at the government verification site (sede.administracionespublicas.gob.es) and compare the returned PDF hash.
2. **Primary texts of 8/2021, 11/2022, 1/2023 and 2/2024.** All 2024 parameters cited (6-month non-location, 6-month supervision, two-VPER-S exit, renunciation levels) are grade C. The in-person contact and the creation of supervised cases are grade B.
3. **The origin of the grade-D changes:**
   - the 72-hour limit for the consolidated VPR;
   - court notification only when the level rises;
   - the device request at Medio limited to special-relevance cases;
   - the Annex II items made conditional on judicial measures.
   They are first *documented* in 2025, which does not prove they were *introduced* in 2025.
4. **Practice.** The texts cannot show any of the following, and nothing here describes what officers do:
   - how often officers raise the level;
   - how "No se sabe" answers affect the score;
   - whether measures are delivered or recorded;
   - how supervised cases are handled;
   - how Bajo cases split by judicial measures.
   See [`INTERVIEW_PROMPTS.md`](../../docs/03_institutional_rules/INTERVIEW_PROMPTS.md) and [`uncertainty_register.csv`](../../data/03_institutional_rules/uncertainty_register.csv) (14 items).
5. **VioGén-2 scoring.** Weights, cut-offs and the special-relevance combination are not public. Reconstructing them is out of scope by design.

## 7. Clean-environment run

The package was copied to an empty directory and run in a new virtual environment created from [`requirements.txt`](../../scripts/03_institutional_rules/requirements.txt):
- Python 3.13.18, pandas 3.1.1, matplotlib 3.11.2, nbformat 5.11.1, nbconvert 7.17.2, pytest 9.2.0, ipykernel 7.4.0.
- Steps: [`build_module3.py`](../../scripts/03_institutional_rules/build_module3.py), then [`make_figures.py`](../../scripts/03_institutional_rules/make_figures.py), then [`make_notebook.py`](../../scripts/03_institutional_rules/make_notebook.py), then the notebook executed with nbconvert, then pytest.
- Result: exit code 0; **275 passed**; notebook executed with 0 errors.
- All 12 data files and [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/03_institutional_rules/SOURCE_VERIFICATION_MATRIX.csv) were rebuilt **byte-identical** to the packaged copies.
- The four figures match in content, but are not byte-identical: text anti-aliasing differs slightly between matplotlib builds.
