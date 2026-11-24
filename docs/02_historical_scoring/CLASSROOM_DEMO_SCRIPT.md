# Classroom demonstration: who decided? (about 12 minutes)

**Aim.** Use one fictitious account to show that an "algorithmic" risk level comes from three kinds of human decision: the officer's coding, the designers' weights and cut-offs, and the procedural rules. **This is an investigation of how discretion is structured, not an audit of accuracy.**

**Set-up.** Run `streamlit run scripts/02_historical_scoring/interactive_app.py`, or open the notebook at section 8. Keep [`02_historical_cutoffs.png`](../../figures/02_historical_scoring/02_historical_cutoffs.png) ready.

**Say first (30 seconds).** "This is the 2016 form, VPR4.0, rebuilt from the doctoral thesis that designed it. It is not VioGén 2, which is in force today. Every case you will see is invented. The numbers are additive points, not probabilities and not measures of danger."

---

## 1 · The account (1 minute)

> A woman reports that her former partner has followed her repeatedly since she ended the relationship four months ago. He insults her by message, and last week he pushed her against a door.

Load the preset **"Stalking + separation"** (I11 + I36).

- **Score 8.226 → No apreciado.**
- Both facts are among the 13 "critical" indicators, but the score is still below the first cut-off of 9.535.

## 2 · Input discretion: the officer codes the account (3 minutes)

The facts do not change, only how they are recorded:

| Coding | What the officer records | Score | Level |
|---|---|---|---|
| A | The push as physical violence, *leve*; the insults not recorded | 8.226 | No apreciado |
| B | As A, plus the insults as psychological violence (I1) | 9.654 | Bajo |
| C | The push as *grave*, following Annex 5: "en caso de duda entre dos niveles, se recomienda indicar el nivel más grave" | 10.226 | Bajo |

In the app: set I2 to *Sí*, then compare I1 *Sí* / *No* and the I2 severity sub-item.

**Ask:** "Did the algorithm decide the level, or did the officer?"

## 3 · Design discretion: the weights and the lines (3 minutes)

Show figure 02 (the cut-offs) and figure 01 (the weights).

- **Firearm used = 1.533. Knife used = 5.533.** The knife is on the experts' homicide-screening list and its weight was doubled (p. 192). Firearm use was too rare in the study (30 of 6,613 cases, p. 163) to reach significance for the criterion used, *a new police report within months*. The zero is a design choice under that criterion. It is not a statement that firearms are less dangerous.
- **31 of 63 rows weigh zero.** These include pregnancy, disability and dependent children. They were kept "to obtain more information" (p. 196).
- **Cut-offs.** The first was set to keep false negatives low. One criterion was that each level hold a share of cases "asumible desde el punto de vista de la seguridad" (p. 194), in other words a workload criterion.
- **The counterfactual** (notebook section 8). Without the doubling of critical weights, the stalking + separation + fear form drops from 11.056 (Bajo) to 5.528 (No apreciado), with the same cut-offs.

**Ask:** "Who is accountable for a line drawn partly for police workload?"

## 4 · Two routes to a level (1 minute)

Open the "Structural facts" expander in the app, or notebook section 6:

- A consistent form can hold **25 of 39 indicators** and still score *no apreciado*. The example includes physical and sexual violence recorded as *leve*, an object used as a weapon, threats to the children and pregnancy.
- **9 indicators** can be enough for *extremo*.

Say: "This is what the rule allows, not what happened. We have no case data."

## 5 · Procedural discretion: what the level does (2 minutes)

Use the override selector in the app (Instrucción 7/2016, thesis Annex 6):

- **Rule 1.5.** The officer may raise the automatic level, **never lower it**. The app only offers higher levels.
- **Rule 1.6.** At *no apreciado* the officer **may** switch the case to inactive, unless a judicial protection measure is in force. Tick the checkbox and the text changes.
- **Rule 1.8.** At *medio* and above the victim is informed of the level.

Combine this with step 2. Coding A leaves the case open to inactivation. Codings B and C keep it active. The difference between them is a single answer on the form.

## 6 · Bridge, carefully (1 minute)

- **Continuity.** Instrucción 1/2025, which introduced VioGén 2, keeps the upward-only override (§§ 3.8, 6.2, as read in Module 1) and removed *no apreciado* from 30 June 2025.
- **What we do not know.** The current weights, items and cut-offs are not public. The 2016 numbers **cannot** explain 2025–2026 classifications.

**Closing question.** "If discretion is removed from the output, an override that only goes up, where does it go? Our answer from 2016: into the input coding and into design choices that are hard to see from outside."
