# Module 2: methods, documented rules and reconstruction assumptions

## 1. Object

This module reconstructs the **VPR4.0** police risk form (initial assessment) as designed in Juan José López Ossorio's doctoral thesis (Universidad Autónoma de Madrid, 2016). It uses:

- Annex 1 (pp. 274–275) for the weights;
- the construction chapter (pp. 189–196) for the method and the cut-offs;
- Annexes 2 and 5 (pp. 276–307) for the screen and the coding instructions;
- Annex 6 (pp. 327–328) for Instrucción 7/2016.

The companion follow-up form VPER4.0 (its manual weight adjustments are described on pp. 198–199) is excluded. It is not VioGén 2, not VPR5.0-H (2019), and not the operational software.

**Source file.** UAM DSpace bitstream `09c11ef0-a544-439a-a623-4e492db41610`. 336 pages; MD5 `5d111ff6d9a6717d14f2c265544406f1`, which equals the repository's own checksum. Printed page numbers equal PDF page numbers.

## 2. How the source was verified

1. **Transcription.** All 63 Annex 1 rows were typed by hand from the page images. Each row records page, group, Spanish label and value as printed ([`annex1_transcription.py`](../../scripts/02_historical_scoring/tools/annex1_transcription.py)).
2. **Automatic cross-check** (`verify_against_pdf`, run by [`test_source_transcription.py`](../../scripts/02_historical_scoring/tests/test_source_transcription.py) when `VPR4_THESIS_PDF` is set):
   - every label occurs in the text layer of its page;
   - the 63 values read top to bottom from the value column of the PDF equal the transcription, in order.

   This catches transpositions, which the 77.019 total cannot.
3. **Independent checks.**
   - The 13 critical flags against Table 1 (p. 193), typed separately in the test file.
   - I20 fixed at 3 (p. 192).
   - The cut-offs, the 77.019 maximum and the 68.062 empirical maximum (p. 194).
4. **Form structure** from Annexes 2 and 5. Every parent link carries the passage that supports it (`structure_evidence` column).
5. Every claim with its status (verified / corrected / inferred / assumption / not documented) is in [`SOURCE_VERIFICATION_MATRIX.csv`](../../data/02_historical_scoring/SOURCE_VERIFICATION_MATRIX.csv). The page images are in [`02_historical_scoring/`](../../sources/02_historical_scoring/).

## 3. Documented rules (implemented as stated)

| Rule | Source |
|---|---|
| The score is the sum of the weights of rows answered Sí ("pesos aditivos ponderados") | p. 193 |
| Sub-items are asked only "en caso afirmativo": a child requires its parent | Annex 5, pp. 291–307 |
| Weapon, threat, control and life-problem types are multi-select checkboxes | pp. 294, 295, 297, 301 |
| Firearm access (I6) is assessed "independientemente de si empleó armas" | p. 295 |
| I17, I18, I19 are asked only when the record question (F08) is Sí | p. 301 |
| Severity is a radio *Leve / Grave / Muy grave*; the weighted row is "grave o muy grave" | Annex 2; pp. 292–294, 296 |
| Cut-offs: 9.535 / 21.886 / 34.715 / 45.284; theoretical maximum 77.019; highest observed score 68.062 | p. 194 |
| Empirical weights = odds ratios for a new police report against the same aggressor within 4 months; construction sample n = 3,907 | p. 191 |
| 13 critical indicators: expert weighting for a homicide screening; final weight = 2 × initial value; I20 fixed at 3 | pp. 191–193 |
| Zero-weight rows kept about 18 months to collect information | p. 196 |
| Officers may raise the automatic level, not lower it | Instrucción 7/2016 rule 1.5, p. 327 |
| At "no apreciado", officers may make a case inactive unless a judicial protection measure is in force | rule 1.6, p. 328 |
| Victim informed at medio and above; result reported to the judicial authority | rule 1.8, p. 328 |

## 4. Additive, dependent or mutually exclusive?

The rows fall into five types:

| Type | Rows | How they combine |
|---|---|---|
| Indicators | 37 | Added when Sí. I17–I19 count only when F08 is Sí. |
| Gate questions F02, F03, F08 | 3 | Added when Sí. A gate opens its sub-items. |
| Severity options | 4 | Added when the radio is *Grave* or *Muy grave*. Each requires its parent. |
| Subtype checkboxes | 16 | Each box ticked is added. Each requires its parent. |
| Sub-questions | 3 | Weigh zero. Each requires its parent. |

Points to note:

- **Mutually exclusive.** The only mutually exclusive control is the severity radio. Its *Leve* option has no row, so **no two weighted rows exclude each other**, and 77.019 is attainable (inferred).
- **Nesting.** There is one level of nesting. In the engine, a sub-item answered Sí sets its parent to Sí, and a parent answered No closes its sub-items. A Sí sub-item under a No parent is rejected.

## 5. Reconstruction assumptions (the source is silent)

| Question | Choice made | Alternative available |
|---|---|---|
| How the software scored "No se sabe" | Report the range from all-unknown-No to all-unknown-Sí (respecting parents). A level is given only when both ends agree. Because all weights are ≥ 0, every possible rule lies inside this range. | Read `score_min` / `score_max` |
| Whether "hasta" includes the cut-off | Inclusive (≤). Every cut-off is exactly attainable, so this matters. | `category(score, upper_inclusive=False)` |
| Placement of rows 4, 7, 16, 54, 55 on the screen | See [`UNRESOLVED_LIMITATIONS.md`](../../docs/02_historical_scoring/UNRESOLVED_LIMITATIONS.md) §5. Only row 16 carries weight. | None needed for zero-weight rows |
| Factors F01 and F05, and the "Otros" options | Not modelled; Annex 1 gives them no row | None |

## 6. Computed results (properties of the rule, not of cases)

The structural analysis is exact. A dynamic programme runs over the form's groups (a parent with its sub-items, or the rows of one indicator), enumerating every consistent form.

- **Attainable scores.** 64,879 distinct scores are attainable. Every cut-off can be hit exactly.
- **Indicators I1–I39 per level, fewest to most:**

  | Level | Fewest | Most |
  |---|---|---|
  | No apreciado | 0 | 25 |
  | Bajo | 1 | 30 |
  | Medio | 3 | 34 |
  | Alto | 6 | 37 |
  | Extremo | 9 | 39 |

  "Facts", which add the weighted gate questions without an I-number, run from 0 to 27 at no apreciado and from 12 to 42 at extremo.
- **Example forms.** `indicator_count_example()` builds a concrete form for each extreme. The no-apreciado form with 25 indicators scores 9.165.

These results show what the rule allows. They say nothing about how often such forms occurred.

## 7. Interpretation rules used throughout

1. Score differences are differences in **points under a historical rule**, never differences in danger.
2. A zero weight means the row did not count in this version of the score. It does not mean the fact was harmless or ignored by the police.
3. Historical numbers are never used to explain VioGén 2 classifications, Module 1 trends, or police decisions.
4. The aim is to locate discretion across four layers, not to audit predictive accuracy:
   - **input**: officer coding;
   - **design**: weights;
   - **design**: cut-offs;
   - **procedure**: override and inactivation rules.

## 8. Reproduction

```bash
pip install -r requirements.txt
python scripts/02_historical_scoring/build_catalog.py                  # catalogue CSV from the verified transcription
python scripts/02_historical_scoring/demo_scenarios.py                 # hypothetical_scenarios.csv / .json
python scripts/02_historical_scoring/generate_figures.py               # figures/01-05
python scripts/02_historical_scoring/tools/build_verification_matrix.py /path/to/thesis.pdf   # SOURCE_VERIFICATION_MATRIX.csv
python scripts/02_historical_scoring/make_notebook.py && jupyter nbconvert --to notebook --execute --inplace scripts/02_historical_scoring/VioGen_Module2_Historical_Research_Lab.ipynb
VPR4_THESIS_PDF=/path/to/thesis.pdf python -m pytest scripts/02_historical_scoring/tests/ -q      # 52 tests
streamlit run scripts/02_historical_scoring/interactive_app.py
```
