# Module 2 verification status, version 2

Each item of the review checklist for version 1 is answered here.

## Scope (unchanged)

- Module 2 is a historical reconstruction of VPR4.0 (2016).
- Never use it to predict or explain VioGén 2 classifications, Module 1 trends, or police decisions.
- The aim is to locate discretion, not to audit accuracy.

## A. Primary-source cross-check: done

| Item | Status |
|---|---|
| Obtain the UAM thesis | Done, via the DSpace API (the `/download` URL returns 403). MD5 `5d111ff6d9a6717d14f2c265544406f1` matches the repository checksum. |
| Map printed page numbers to PDF pages | They are identical; checked on pp. 163, 190–196, 274–277, 291–307 and 327–328. |
| Verify each row: label, weight, page, parent, critical flag | Done for all 63 rows. See [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/02_historical_scoring/SOURCE_VERIFICATION_MATRIX.csv). 7 rows corrected (10, 15, 18, 20, 38, 40, 41); 5 rows with an inferred screen mapping (4, 7, 16, 54, 55). |
| Treat the total as different evidence from the visual check | Done. A test runs the automatic PDF check (labels and value sequence), and the notebook demonstrates that a transposition keeps 77.019. |

## B. Assumptions investigated: done

| Item | Finding |
|---|---|
| Additive or mutually exclusive? | Additive (p. 193). Sub-types are multi-select. Severity is a radio whose *Leve* option carries no row. No two weighted rows exclude each other, so 77.019 is attainable. |
| Child implies parent? | Documented: sub-items are asked "en caso afirmativo". Implemented in both directions. |
| Raw or transformed score? | Raw sum of the Annex 1 values (p. 193–194). No normalisation. |
| Missing values | Not documented for the software. The engine reports bounds and never counts unknown as No. |
| Impossible combinations | The structure is enforced. Every example and every computed extreme is a consistent form. |
| Regression tests | 52 tests in total (37 on the engine). |

## C. Interfaces executed: done

| Item | Status |
|---|---|
| Streamlit | Verified with six Streamlit AppTest tests. Presets, reset, parent/child behaviour, unknown ranges, override and the judicial checkbox are all tested. A live result was added to the sidebar after testing showed the score scrolled out of view. |
| Notebook | Executed from an empty folder (14 code cells, 0 errors), both in the build environment and in a fresh virtual environment built from [`requirements.txt`](../../scripts/02_historical_scoring/requirements.txt). The widget logic was tested headlessly. **Not run on Colab itself.** |
| Requirements | [`requirements.txt`](../../scripts/02_historical_scoring/requirements.txt) with the tested versions. |

## D. Accuracy and narrative: done

| Item | Status |
|---|---|
| 1.533 versus 5.533 | Verified. Explained by the critical list (p. 192) and the 30-case frequency (p. 163). |
| 8.226 and 11.056 | Verified (rows 30, 60, 63). |
| "22 facts and still no apreciado" | **Superseded.** The exact maximum is 25 indicators (27 facts), example score 9.165. It is a logical possibility, not an observed case. |

## Package files

[`SOURCE_VERIFICATION_MATRIX.csv`](../../data/02_historical_scoring/SOURCE_VERIFICATION_MATRIX.csv), [`CHANGELOG.md`](../../docs/02_historical_scoring/CHANGELOG.md), [`UNRESOLVED_LIMITATIONS.md`](../../docs/02_historical_scoring/UNRESOLVED_LIMITATIONS.md), [`requirements.txt`](../../scripts/02_historical_scoring/requirements.txt), the updated catalogue, engine, app, notebook, tests and figures, plus [`02_historical_scoring/`](../../sources/02_historical_scoring/).

## Open items for a later round

1. Run the notebook once on Colab, and click through the widget.
2. Find the official text of Instrucción 7/2016 (the thesis quotes it in an annex) and the Adjunto I protection catalogues.
3. Interviews: ask how "No se sabe" was scored, how cut-off ties were handled, and when the 18-month zero-weight review happened.
4. Module 3: the VioGén 2 procedural rules, kept separate from these numbers.
