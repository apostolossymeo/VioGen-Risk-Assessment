# Classroom interface specification

> **Status: not built.** This is a specification for a later, separate project. Nothing in Module 3 is application code. The data describe formal rules in two protocol texts; they do not describe police practice or real cases.

## Purpose

An interactive classroom tool. The user walks through a fictional case and sees, at each step, who holds the decision and which clause says so. It is a teaching device about where discretion sits. It is not a risk calculator.

## Data contract

The single source is [`research_export.json`](../../data/03_institutional_rules/research_export.json), schema `viogen-module3-research-export/2.0`.

| Key | Use in the tool |
|---|---|
| `levels` | Level names per protocol (2019: five levels; 2025: four) |
| `sources` | Footer citations: title, dates, host, hash, access note |
| `clauses` | Pop-ups: Spanish excerpt, section, page, English summary |
| `rules` | One card per decision point: owner, other actors, modality, clause IDs, attribution |
| `comparison` | "What changed" view: 34 topics, each with attribution and evidence grade |
| `measures` | Protection floor by level and block, with modality and condition |
| `measure_changes` | Highlights in the annex comparison |
| `chronology` | Timeline of instruments |
| `uncertainty` | "What we don't know" panel |
| `abstract_pathways` | Pre-computed outcomes for the 50 rule combinations (no cases) |

Display rules that must follow [`decision_rules.py`](../../scripts/03_institutional_rules/src/decision_rules.py) exactly:
- deadlines with their bound ("before 60 days", "at most 15 days", "at least 7 days");
- `not_stated` shown as "the text sets no deadline", never as zero;
- `cannot_determine` shown as "depends on facts the user has not set".

## Required behaviour

1. **Fictional input only.** No free-text field about real abuse; no personal data collected.
2. **The level is an input.** The user picks an already-assigned level. The tool never computes a score and must say that VioGén-2's scoring is not public.
3. **Officer adjustment is upward only.** The tool shows that this rule dates from 2016 at least (rule `2025-R03`, comparison `T03`).
4. **Judicial measures are an input**, with an explanation of who decides them.
5. **Every output shows:** clause IDs, page, evidence grade, and attribution (`predates_2019`, `baseline_2019`, `continuity`, `introduced_between_2019_2025`, `changed_twice`, `first_documented_2025` or `origin_unknown`).
6. **Grade-C and grade-D items carry a visible caution badge.**
7. **The protection floor** is shown as the written minimum, labelled "not evidence of delivery".
8. **The ending screen** shows the accountability map ([`02_decision_authority_map_2025.png`](../../figures/03_institutional_rules/02_decision_authority_map_2025.png)) and the formal-versus-practice caveat.

## Must not

- Present VPR4.0 (Module 2) as VioGén-2.
- Claim effects or outcomes of the 2025 reform.
- Compute workload without the split of Bajo cases by judicial measures.
- Attribute a change to 2025 when the export says `changed_twice`, `introduced_between_2019_2025` or `origin_unknown`.

## Before building

- Validate the 2025 CSV on the official site, and update `sources` if a government copy is obtained.
- If the texts of 2/2024 (or 8/2021, 11/2022, 1/2023) are obtained, re-grade the affected `comparison` rows and re-run [`build_module3.py`](../../scripts/03_institutional_rules/build_module3.py).
