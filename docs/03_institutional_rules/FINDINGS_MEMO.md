# Module 3 findings memo: where discretion sits in the 2019 and 2025 police protocols

**What this memo rests on**

| | Document | Status |
|---|---|---|
| Primary texts | Instrucción 4/2019 | Official PDF |
| | Instrucción 1/2025 | Signed copy with CSV GEN-61b6…598b, from a non-government host |
| | Instrucción 5/2021 (Protocolo Cero) | Official PDF |
| Intervening instructions | 8/2021, 11/2022, 1/2023, 2/2024 | Only official press summaries or secondary sources (graded below) |

**Page references.** "§" = section of the protocol. "p." = printed page, which equals the PDF page in both protocols. Clause IDs (e.g. `C25-6.3`) point to [`protocol_clauses.csv`](../../data/03_institutional_rules/protocol_clauses.csv). There, every excerpt is re-found on its page by the test suite.

**How to read each finding.**
- *Documented* = stated in a primary text.
- *Inference* = our reading of what the documented rules imply.
- *Unknown* = what the texts cannot tell us.

None of this describes what police actually do.

---

## 1. Discretion over the automatic level runs one way, and it is old

**Documented.**
- Officers may raise the system's level when they see indications the form does not capture:
  - 2019: §1.6 p. 7; §5.10 p. 14.
  - 2025: §3.8 p. 14; §6.2 p. 17.
- Neither text provides a downward route.
- The rule predates 2019:
  - The 2019 preamble (p. 2) describes it as a feature of the protocols already in force.
  - Instrucción 7/2016, rule 1.5, already contained the upward-only rule (quoted in the López Ossorio thesis, Annex 6; see Module 2).
- The 2025 text adds new language around the algorithm:
  - VPR and VPER are "semiactuarial" tools (p. 8).
  - The officer adopts the final decision "–ya sea en acuerdo o desacuerdo–" (p. 10).
  - The system has no machine learning, and "ni los puntos de corte se modifican con el funcionamiento del Sistema" (p. 10).
- The operative clauses are still upward-only. No duty to record the reasons for a raise is stated; the system merely "permite … realizar las observaciones que consideren" (p. 8).

**Inference.** At the output stage, officer discretion can only add protection. Any downward effect has to come through the *input*: which indicators are marked, and how many are left as "No se sabe". Protocolo Cero makes this explicit: the assessor "debe decidir si un indicador debe estar o no presente" (5/2021 §2.3 p. 7). The 2025 text asks officers to minimise "No se sabe" (§3.6 p. 13) and, for the first time, shows those answers to the court (Si/No/NS, §3.9 p. 14).

**Unknown.** How often officers raise the level, and how often input coding lowers it in effect.

## 2. Removing "no apreciado" is, procedurally, largely a relabelling of the bottom of the scale

**Documented** ([`03_low_risk_restructuring.png`](../../figures/03_institutional_rules/03_low_risk_restructuring.png)). "No apreciado" disappears and Bajo is split "a efectos de gestión del riesgo" by whether judicial measures are in force (p. 11).

| | 2019 no apreciado | 2025 Bajo, no judicial measures | 2019 bajo | 2025 Bajo, with judicial measures |
|---|---|---|---|---|
| First VPER | no deadline stated (§5.3–5.4) | no deadline stated (§4.3–4.4) | ≤ 7 days | ≤ 15 days |
| Later VPER | < 90 days | < 90 days (§6.1 p. 17) | < 60 days | < 60 days |
| Ordinary inactivation | open "con carácter general" | open | "excepcionalmente" | closed while measures are in force |
| Written measures (annex items) | 3 | 15 | 13 | 18 |

Read across: "Bajo without measures" takes the deadlines of "no apreciado", and "Bajo with measures" takes those of the old "bajo".

**Inference.** What changes for the former bottom group is the written protection floor and the conditions for closing a case (Finding 4), not the reassessment schedule.

**Unknown.**
- Which real cases sit in each group. The algorithm was recalibrated (Moncloa, 15/01/2025), so labels cannot be mapped onto cases.
- How Bajo splits by judicial measures. Public statistics do not report it, so workload cannot be computed.
- Module 1 shows only the aggregate: in July 2025 the "no apreciado" count was absorbed into Bajo.

## 3. Within Bajo, a court's decision now sets the police schedule

**Documented.** For a 2025 Bajo case, whether judicial measures exist decides four things:
- the first-VPER deadline: 15 days, or none stated (§4.4 p. 15);
- the later interval: 60 or 90 days (§6.1 p. 17);
- whether the ordinary inactivation route is open (§7.1 p. 18);
- two aggressor-side annex items: telling him that "su caso de violencia de género se encuentra sometido a control/protección policial", and checking "la información penitenciaria en el Sistema VioGén-2" for his movements. Both now sit under the heading "EN EL CASO DE EXISTENCIA DE MEDIDAS JUDICIALES" (Annex II p. 38; `A2-2025-15`, `A2-2025-17`).

In 2019 the bajo interval (60 days) did not depend on judicial measures, and both items applied to every bajo case (Anexo 1 p. 16; `A1-2019-09`, `A1-2019-12`). The third item under the 2025 heading, escorting the aggressor to collect his belongings, is not a change: in both years it applies only when the judge orders him out of the home (`A1-2019-11`, `A2-2025-16`).

The 2025 annex also ties the electronic-device request to designer-built flags:
- In 2019 police asked the prosecutor for a device in every medio case (Anexo 1 p. 17).
- In 2025 they do so at Medio only "EN LOS SUPUESTOS DE CASOS DE ESPECIAL RELEVANCIA" (p. 39), and at every Alto+ case.
- Special relevance is detected by the system "ante una combinación específica de indicadores" (§8.A p. 23). That combination is not public.

**Inference.** At the low end of the scale, discretion moved towards judges and prosecutors, whose decisions trigger police obligations. At Medio, it moved towards whoever designs the special-relevance flag.

**Unknown.** Where these annex differences came from. None is mentioned in the available summaries of 2021–2024 (grade D).

## 4. Case closure is where the rules moved most, and 2024 matters as much as 2025

**Documented and attributed** ([`01_change_chronology.png`](../../figures/03_institutional_rules/01_change_chronology.png), [`INTERVENING_INSTRUCTIONS_CHRONOLOGY.md`](../../docs/03_institutional_rules/INTERVENING_INSTRUCTIONS_CHRONOLOGY.md)).

| Rule | 2019 (A) | 2/2024 | 2025 (A) |
|---|---|---|---|
| Victim cannot be located | at least 1 month (§2.7 p. 9) | 6 months (C: La Marea, DEPOL) | 3 months, then judicial police and an oficio to court and prosecutor (§7.2.1 p. 18) |
| Renunciation | "con independencia del nivel de riesgo", if no judicial measures (§2.8 pp. 9–10) | no apreciado, bajo or medio (C) | Bajo or Medio; officers must look into the reasons (§7.2.2 p. 19) |
| Modal verb for exceptional inactivation | "podrá" | "podrá" (C) | "Se procederá" |
| Ordinary-inactivation test | negative: "no aconsejen lo contrario" (§2.6 p. 9) | same wording (C) | positive: the circumstances must show "de manera fehaciente … que no se dan las condiciones objetivas para una reproducción de la agresión" (§7.1 p. 18) |
| Contact with the victim | at least once | "al menos una vez y de manera presencial" (B: Consejo de Ministros 08/03/2024) | "preferentemente de manera presencial" |
| Supervised cases | not present | created as "inactivación supervisada" (B); details below (C) | 3-month minimum; exit after one VPER at Bajo plus an interview (§7.4 pp. 20–21) |

Details of the 2024 supervision regime (grade C): a 6-month look-back for Medio+, a 6-month minimum, an evaluator-discretion entry criterion, and exit after two VPER-S at "no apreciado".

**Inference.**
- A two-document comparison would misread several of these changes. Against 2019, the 2025 non-location rule looks stricter (1 → 3 months). Against 2024, it is shorter (6 → 3). The same applies to the supervision periods.
- VioGén-2 both *constrains* officers (a positive finding is now needed; supervision triggers apply) and *relaxes* parts of the 2024 regime (shorter supervision, shorter non-location, contact only "preferably" in person).
- None of this can be attributed to the software launch.

**Unknown.** The primary text of Instrucción 2/2024, which is restricted. Every grade-C figure above should be confirmed against it.

## 5. The accountability trail is uneven

**Documented.**

*Must be recorded or communicated in 2025:*
- capacity shortfalls: "Esta incidencia debe hacerse constar en el Sistema VioGén-2" (§5.7 p. 16);
- causes and actions of an exceptional inactivation, with communication to court and prosecutor (§7.2.1 p. 19);
- efforts made after a renunciation (§7.2.2 p. 19);
- the impossibility of an interview in supervision (§7.4.2 p. 21);
- the fact that a victim was told about a persistent aggressor's record (§8.C.2.3 p. 26);
- the risk level, given to the victim "a través de un medio que deje constancia en derecho" (§5.4 p. 16).

*No duty stated:*
- Recording the measures actually applied: "En la medida de lo posible, resulta recomendable registrar en el Sistema las medidas policiales de protección a través del Módulo de Actuaciones Policiales" (Annex II p. 37).
- Reasons for an upward raise.
- Any communication to the court when a Bajo case is inactivated through the ordinary route (§7.1 requires only traceability).

*Court communication of routine VPER results narrowed:*
- 2019: on any variation (§5.11 p. 14).
- 2025: only when the level rises (§6.3 p. 17).

**Inference.** Under the 2025 texts, a case can fall to Bajo and then be closed through the ordinary route with no individual communication to the court at either step. The same sequence under 2019 produced an oficio at the drop. What the police *did* to protect a victim may leave no structured record at all.

**Unknown.** Whether practice records more than the text requires, for example through the Módulo de Actuaciones Policiales or force-level rules.

---

### Limits that apply to every finding

- These are formal rules. Implementation, resources and outcomes are unobserved (see [`uncertainty_register.csv`](../../data/03_institutional_rules/uncertainty_register.csv)).
- The 2025 PDF has not been validated through the official CSV service.
- The scoring of VioGén-2 is out of scope by design. Module 2's VPR4.0 (2016) is not VioGén-2.
- No causal claim about VioGén-2 can be drawn from comparing protocols.

### Interpretation

> **The algorithm's output is fenced (raise-only); the discretion moved to inputs, to courts' measures, to designer-built flags, and above all to the rules for closing a case, which changed in 2024 as much as in 2025.**
