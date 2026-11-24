# What we still do not know

This module rebuilds the risk form that Spanish police used from 2016 (VPR4.0), using the doctoral thesis in which it was designed. The table of weights and the cut-offs are now checked line by line against that thesis. What follows is what the thesis does **not** tell us, and what the module therefore cannot claim.

## 1. This is not the system in use today

- VioGén 2 has been in force since 30 June 2025. Its questions, weights and cut-offs are not public. Neither are those of the version before it, VPR5.0-H, in use from March 2019.
- Nothing in this module explains a classification made in 2025 or 2026, a trend in the Module 1 statistics, or any police decision.
- What carries over is the *kind* of rule (an automatic level that officers may raise but not lower), not the numbers.

## 2. We have the design document, not the software

The thesis describes the form as it was designed. We have not seen the program police actually ran. It may have differed in ways the thesis does not mention: later corrections, rounding, or how it handled a field left blank.

## 3. "No se sabe" (unknown) answers

Officers could answer most questions "No se sabe". The thesis says these answers were treated as missing *in its statistics* (p. 161). It does not say how the software scored them.

The module does not guess. It shows the lowest possible score, with every unknown counted as No, and the highest, with every unknown counted as Sí. It gives a level only if both ends fall in the same level.

## 4. A score exactly on a cut-off

The thesis says "no apreciado, de 0 hasta 9.535; bajo, hasta 21.886; …". It does not say whether "hasta 9.535" includes 9.535 itself. At the top boundary the wording even overlaps: "alto, hasta 45.284" and "extremo, a partir del punto anterior". A form can score exactly 9.535, so this matters for a handful of forms. We read "hasta" as "up to and including". The other reading is one switch away (`upper_inclusive=False`).

## 5. Rows whose place on the screen is uncertain

Five of the 63 rows are weighted correctly, but their exact link to a control on the police screen is our interpretation. All five except the threat-severity row weigh zero, so the interpretation cannot change a score.

| Row | Content | What is uncertain |
|---|---|---|
| 4, 7 | "with or without injuries" | Under physical and sexual violence, but no matching control appears in the screen images. |
| 16 | "serious threats" (1.893) | Taken to be the *Grave / Muy grave* option of the threat-severity button. |
| 54, 55 | The two parts of indicator 32 | Which row is which checkbox. |

## 6. Things on the screen that the table does not cover

- The screen shows "Otros" (other) options for life problems and for victim vulnerability. They have no row and no weight in Annex 1, so they are not modelled.
- The questions for factors 1 and 5 have no weight of their own and are not modelled as separate questions.

## 7. What happens after the level

- The instruction of 2016 (Instrucción 7/2016) is quoted from an annex of the thesis, not from the official text.
- The police protection measures attached to each level are in a separate catalogue ("Adjunto I"), which the thesis does not reproduce. The module shows only rules 1.5, 1.6, 1.8 and 2.1.

## 8. What the weights measure

The empirical weights are odds ratios for one outcome: a new police report against the same aggressor within four months. They were estimated on cases reported in autumn 2015 (p. 191). They are **not** measures of how dangerous a situation is, and not probabilities.

The 13 heavier "critical" weights were set by expert judgement for a homicide screening and then doubled (p. 192). The thesis does not give the experts' original values, or say why some items, such as firearm use, are not on the list.

## 9. "Logically possible" is not "it happened"

The structural results describe the rule, not real cases:

- 25 of the 39 indicators can be present while the level stays "no apreciado";
- 9 indicators can be enough for "extremo".

We have no case data, and we make no claim about how often any combination occurred.

## 10. Not checked here

- **The companion follow-up form, VPER4.0.** It has its own annex and its own manual adjustments (pp. 198–199). It is cited only as an example of designer discretion.
- **The notebook on Colab.** It ran start to finish in a clean local environment. It was not run on Colab itself, and the widget in section 10 was tested without a browser.
- **The thesis PDF.** It is not redistributed. The source tests re-read it when `VPR4_THESIS_PDF` points to a copy. The page images of every passage cited are in [`02_historical_scoring/`](../../sources/02_historical_scoring/).
